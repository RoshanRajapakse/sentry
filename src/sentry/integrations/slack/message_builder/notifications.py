from typing import TYPE_CHECKING, Dict, List, Union

from sentry.integrations.notifications import NotificationMessageBuilderMixin
from sentry.integrations.slack.message_builder import SlackBody
from sentry.integrations.slack.message_builder.base.base import SlackMessageBuilder
from sentry.integrations.slack.message_builder.issues import SlackIssuesMessageBuilder
from sentry.integrations.slack.utils import build_deploy_buttons, build_notification_footer
from sentry.notifications.notifications.activity.release import ReleaseActivityNotification
from sentry.notifications.notifications.base import BaseNotification

if TYPE_CHECKING:
    from sentry.models import Group, Team, User


class SlackNotificationsMessageBuilder(SlackMessageBuilder, NotificationMessageBuilderMixin):  # type: ignore
    def build_deploy_buttons(
        self, notification: ReleaseActivityNotification
    ) -> List[Dict[str, str]]:
        return build_deploy_buttons(notification)

    def build_footer(self, notification: BaseNotification, recipient: Union[Team, User]) -> str:
        return build_notification_footer(notification, recipient)

    def fall_back_to_alert(self, group: Group) -> SlackBody:
        return SlackIssuesMessageBuilder(
            group=group,
            event=getattr(self.notification, "event", None),
            tags=self.context.get("tags", None),
            rules=getattr(self.notification, "rules", None),
            issue_details=True,
            notification=self.notification,
            recipient=self.recipient,
        ).build()
