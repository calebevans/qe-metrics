from datetime import date
import pytest
from qe_metrics.libs.database_mapping import JiraIssuesEntity
from qe_metrics.utils.issue_utils import (
    update_existing_issue,
    mark_obsolete_issues,
    create_update_issues,
    format_issue_date,
    delete_old_issues,
)


@pytest.mark.parametrize(
    "product, raw_jira_issues, jira_issues",
    [
        pytest.param(
            ("update-existing-issue-product"),
            [{"key": "TEST-1234", "title": "New Test Summary", "last_updated": "2024-01-01T23:59:59.999999+0000"}],
            [
                {
                    "issue_key": "TEST-1234",
                    "title": "Test Summary",
                    "url": "https://jira.com",
                    "project": "TEST",
                    "severity": "blocker",
                    "status": "To Do",
                    "issue_type": "bug",
                    "customer_escaped": True,
                    "date_created": "2023-12-29",
                    "last_updated": "2023-12-30",
                }
            ],
        ),
    ],
    indirect=True,
)
def test_update_existing_issue(product, raw_jira_issues, jira_issues):
    update_existing_issue(existing_issue=jira_issues[0], new_issue_data=raw_jira_issues[0], severity="critical")
    expected_values = {
        "title": "New Test Summary",
        "severity": "critical",
        "status": "In Progress",
        "customer_escaped": False,
        "last_updated": date(2024, 1, 1),
    }
    actual_values = {
        "title": jira_issues[0].title,
        "severity": jira_issues[0].severity,
        "status": jira_issues[0].status,
        "customer_escaped": jira_issues[0].customer_escaped,
        "last_updated": jira_issues[0].last_updated,
    }
    assert actual_values == expected_values, f"actual: {actual_values} != expected: {expected_values}"


@pytest.mark.parametrize(
    "product, raw_jira_issues, jira_issues",
    [
        pytest.param(
            ("mark-obsolete-issues-product"),
            [
                {
                    "key": "TEST-1134",
                    "title": "Test Summary",
                },
                {
                    "key": "TEST-1136",
                    "title": "Test Summary",
                },
            ],
            [
                {
                    "issue_key": "TEST-1134",
                    "title": "Test Summary",
                    "url": "https://jira.com",
                    "project": "TEST",
                    "severity": "blocker",
                    "status": "In Progress",
                    "issue_type": "bug",
                    "customer_escaped": False,
                    "date_created": "2024-12-30",
                    "last_updated": "2024-12-31",
                },
                {
                    "issue_key": "TEST-1135",
                    "title": "Test Summary",
                    "url": "https://jira.com",
                    "project": "TEST",
                    "severity": "blocker",
                    "status": "In Progress",
                    "issue_type": "bug",
                    "customer_escaped": False,
                    "date_created": "2024-12-30",
                    "last_updated": "2024-12-31",
                },
            ],
        ),
    ],
    indirect=True,
)
def test_mark_obsolete_issues(product, raw_jira_issues, jira_issues):
    mark_obsolete_issues(current_issues=raw_jira_issues, db_issues=jira_issues, product=product)
    assert (
        JiraIssuesEntity.get(lambda issue: issue.issue_key == "TEST-1135").status == "obsolete"
    ), f"Issue {jira_issues[1].issue_key} was not marked as obsolete."


@pytest.mark.parametrize(
    "product, raw_jira_issues",
    [
        pytest.param(
            ("create-update-issues-product"),
            [
                {
                    "key": "NEW-1234",
                    "title": "Test Summary",
                    "customer_escaped": "1.0",
                },
            ],
        ),
    ],
    indirect=True,
)
def test_create_update_issues_creates_issues(product, raw_jira_issues):
    create_update_issues(issues=raw_jira_issues, product=product, severity="blocker", jira_server="https://jira.com")
    assert JiraIssuesEntity.get(
        issue_key=raw_jira_issues[0].key, product=product
    ), f"New issue {raw_jira_issues[0].key} was not created."


@pytest.mark.parametrize(
    "product, jira_issues",
    [
        pytest.param(
            ("delete_old_issues_product"),
            [
                {
                    "issue_key": "OLD-1234",
                    "title": "Test Issue",
                    "url": "https://jira.com",
                    "project": "OLD",
                    "severity": "blocker",
                    "status": "Open",
                    "issue_type": "bug",
                    "customer_escaped": False,
                    "date_created": "2023-01-01",
                    "last_updated": "2023-01-01",
                }
            ],
        ),
    ],
    indirect=True,
)
def test_delete_old_issues(product, jira_issues):
    delete_old_issues(days_old=180)
    assert not JiraIssuesEntity.get(
        issue_key="OLD-1234", product=product
    ), f"Old issue {jira_issues[0].issue_key} was not deleted."


@pytest.mark.parametrize(
    "raw_jira_issues",
    [
        [
            {
                "key": "TEST-3234",
                "title": "New Test Summary",
                "last_updated": "2023-01-31T23:59:59.999999+0000",
            }
        ]
    ],
    indirect=True,
)
def test_format_issue_date(raw_jira_issues):
    assert format_issue_date(raw_jira_issues[0].fields.updated) == date(
        2023, 1, 31
    ), "Issue date not formatted properly."