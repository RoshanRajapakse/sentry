from fixtures.page_objects.issue_details import IssueDetailsPage
from sentry.testutils import AcceptanceTestCase, SnubaTestCase
from sentry.testutils.helpers.datetime import before_now, iso_format
from sentry.testutils.silo import region_silo_test
from sentry.utils.samples import load_data


@region_silo_test
class IssueTagValuesTest(AcceptanceTestCase, SnubaTestCase):
    page: IssueDetailsPage

    def setUp(self):
        super().setUp()
        self.user = self.create_user("foo@example.com")
        self.org = self.create_organization(owner=self.user, name="Rowdy Tiger")
        self.team = self.create_team(organization=self.org, name="Mariachi Band")
        self.project = self.create_project(organization=self.org, teams=[self.team], name="Bengal")
        self.login_as(self.user)
        self.page = IssueDetailsPage(self.browser, self.client)
        self.dismiss_assistant()

    def create_issue(self):
        event_data = load_data("javascript")
        event_data["timestamp"] = iso_format(before_now(minutes=1))
        event_data["tags"] = {"url": "http://example.org/path?key=value"}
        return self.store_event(data=event_data, project_id=self.project.id)

    def test_user_tag(self):
        event = self.create_issue()
        self.page.visit_tag_values(self.org.slug, event.group_id, "user")

        assert self.browser.element_exists_by_test_id("group-tag-mail")
        self.browser.snapshot("issue details tag values - user")

    def test_url_tag(self):
        event = self.create_issue()
        self.page.visit_tag_values(self.org.slug, event.group_id, "url")

        assert self.browser.element_exists_by_test_id("group-tag-url")
        self.browser.snapshot("issue details tag values - url")
