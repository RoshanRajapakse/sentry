from datetime import timedelta
from unittest.mock import patch

from django.utils import timezone

from sentry.auth.exceptions import IdentityNotValid
from sentry.auth.providers.dummy import DummyProvider
from sentry.models import AuthIdentity, AuthProvider, OrganizationMember
from sentry.tasks.check_auth import AUTH_CHECK_INTERVAL, check_auth, check_auth_identity
from sentry.testutils import TestCase
from sentry.testutils.silo import control_silo_test


@control_silo_test
class CheckAuthTest(TestCase):
    @patch("sentry.tasks.check_auth.check_auth_identity")
    def test_simple(self, mock_check_auth_identity):
        organization = self.create_organization(name="Test")
        user = self.create_user(email="bar@example.com")
        auth_provider = AuthProvider.objects.create(organization=organization, provider="dummy")
        OrganizationMember.objects.create(
            user=user, organization=organization, flags=OrganizationMember.flags["sso:linked"]
        )

        ai = AuthIdentity.objects.create(
            auth_provider=auth_provider, user=user, last_synced=timezone.now() - timedelta(days=1)
        )

        check_auth()

        updated_ai = AuthIdentity.objects.get(id=ai.id)
        assert updated_ai.last_synced != ai.last_synced
        assert updated_ai.last_verified == ai.last_verified

        mock_check_auth_identity.apply_async.assert_called_once_with(
            kwargs={"auth_identity_id": ai.id}, expires=AUTH_CHECK_INTERVAL
        )


@control_silo_test
class CheckAuthIdentityTest(TestCase):
    @patch("sentry.tasks.check_auth.check_auth_identity")
    def test_simple(self, mock_check_auth_identity):
        organization = self.create_organization(name="Test")
        user = self.create_user(email="bar@example.com")
        auth_provider = AuthProvider.objects.create(organization=organization, provider="dummy")
        om = OrganizationMember.objects.create(
            user=user, organization=organization, flags=OrganizationMember.flags["sso:linked"]
        )

        ai = AuthIdentity.objects.create(
            auth_provider=auth_provider, user=user, last_verified=timezone.now() - timedelta(days=1)
        )

        with patch.object(DummyProvider, "refresh_identity") as mock_refresh_identity:
            mock_refresh_identity.side_effect = IdentityNotValid()
            with self.auth_provider("dummy", DummyProvider):
                check_auth_identity(auth_identity_id=ai.id)
            mock_refresh_identity.assert_called_once_with(ai)

        # because of an error, it should become inactive
        om = OrganizationMember.objects.get(id=om.id)
        assert not om.flags["sso:linked"]
        assert om.flags["sso:invalid"]

        updated_ai = AuthIdentity.objects.get(id=ai.id)
        assert updated_ai.last_synced != ai.last_synced
        assert updated_ai.last_verified != ai.last_verified
