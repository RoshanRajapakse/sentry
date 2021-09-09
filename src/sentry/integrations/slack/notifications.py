import logging
from collections import defaultdict
from typing import AbstractSet, Any, Mapping, MutableMapping, Optional, Set, Union

from sentry import analytics
from sentry.integrations.slack.client import SlackClient  # NOQA
from sentry.integrations.slack.message_builder.notifications import SlackNotificationsMessageBuilder
from sentry.models import Organization, Team, User
from sentry.notifications.integrations import (
    get_channel_and_integration_by_team,
    get_channel_and_integration_by_user,
    get_context,
    get_key,
)
from sentry.notifications.notifications.base import BaseNotification
from sentry.notifications.notify import register_notification_provider
from sentry.shared_integrations.exceptions import ApiError
from sentry.types.integrations import ExternalProviders
from sentry.utils import json, metrics

logger = logging.getLogger("sentry.notifications")
SLACK_TIMEOUT = 5


def get_channel_and_token_by_recipient(
    organization: Organization, recipients: AbstractSet[Union[User, Team]]
) -> Mapping[Union[User, Team], Mapping[str, str]]:
    output: MutableMapping[Union[User, Team], MutableMapping[str, str]] = defaultdict(dict)
    for recipient in recipients:
        channels_to_integrations = (
            get_channel_and_integration_by_user(recipient, organization, ExternalProviders.SLACK)
            if isinstance(recipient, User)
            else get_channel_and_integration_by_team(
                recipient, organization, ExternalProviders.SLACK
            )
        )
        for channel, integration in channels_to_integrations.items():
            try:
                token = integration.metadata["access_token"]
            except AttributeError as e:
                logger.info(
                    "notification.fail.invalid_slack",
                    extra={
                        "error": str(e),
                        "organization": organization,
                        "recipient": recipient.id,
                    },
                )
                continue

            output[recipient][channel] = token
    return output


@register_notification_provider(ExternalProviders.SLACK)
def send_notification_as_slack(
    notification: BaseNotification,
    recipients: Union[Set[User], Set[Team]],
    shared_context: Mapping[str, Any],
    extra_context_by_user_id: Optional[Mapping[int, Mapping[str, Any]]],
) -> None:
    """Send an "activity" or "alert rule" notification to a Slack user or team."""
    client = SlackClient()
    data = get_channel_and_token_by_recipient(notification.organization, recipients)

    for recipient, tokens_by_channel in data.items():
        is_multiple = True if len([token for token in tokens_by_channel]) > 1 else False
        if is_multiple:
            logger.info(
                "notification.multiple.slack_post",
                extra={
                    "notification": notification,
                    "recipient": recipient.id,
                },
            )
        extra_context = (extra_context_by_user_id or {}).get(recipient.id, {})
        context = get_context(notification, recipient, shared_context, extra_context)
        attachment = [SlackNotificationsMessageBuilder(notification, context, recipient).build()]
        for channel, token in tokens_by_channel.items():
            # unfurl_links and unfurl_media are needed to preserve the intended message format
            # and prevent the app from replying with help text to the unfurl
            payload = {
                "token": token,
                "channel": channel,
                "link_names": 1,
                "unfurl_links": False,
                "unfurl_media": False,
                "text": notification.get_notification_title(),
                "attachments": json.dumps(attachment),
            }
            try:
                client.post("/chat.postMessage", data=payload, timeout=5)
            except ApiError as e:
                logger.info(
                    "notification.fail.slack_post",
                    extra={
                        "error": str(e),
                        "notification": notification,
                        "recipient": recipient.id,
                        "channel_id": channel,
                        "is_multiple": is_multiple,
                    },
                )
            analytics.record(
                "integrations.slack.notification_sent",
                organization_id=notification.organization.id,
                project_id=notification.project.id,
                category=notification.get_category(),
                actor_id=recipient.actor_id,
            )

    key = get_key(notification)
    metrics.incr(
        f"{key}.notifications.sent",
        instance=f"slack.{key}.notification",
        skip_internal=False,
    )
