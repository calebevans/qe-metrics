import pytest
import yaml
from qe_metrics.libs.database import Database
from pony import orm


@pytest.fixture(scope="module")
def db_session():
    with orm.db_session:
        yield


@pytest.fixture(scope="module")
def tmp_sqlite_db(tmp_db_creds) -> Database:
    """
    Setup and teardown a temporary SQLite database for testing.

    Yields:
        Database: Database object
    """

    with Database(creds_file=tmp_db_creds, verbose=False) as database:
        yield database


@pytest.fixture(scope="session")
def tmp_db_creds(tmp_path_factory) -> str:
    """
    Setup and teardown a temporary database credentials file for testing.

    Yields:
        str: Temporary database credentials file path
    """
    tmp_dir = tmp_path_factory.mktemp(basename="qe-metrics-test")

    creds = {
        "database": {
            "local": True,
            "local_filepath": str(tmp_dir / "qe_metrics_test.sqlite"),
        }
    }

    with open(tmp_dir / "creds.yaml", "w") as tmp_creds:
        yaml.dump(creds, tmp_creds)
    yield tmp_creds.name


@pytest.fixture
def service(db_session, tmp_sqlite_db, request):
    return tmp_sqlite_db.Services(name=request.param)


@pytest.fixture
def jira_issue(db_session, tmp_sqlite_db, service, request):
    """
    Setup a JiraIssues entry for testing.

    Yields:
        JiraIssues: JiraIssues object
    """
    with orm.db_session:
        jira_issue = tmp_sqlite_db.JiraIssues(service=service, **request.param)
        yield jira_issue
