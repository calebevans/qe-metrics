from typing import Any
import re

import click
from jira import JIRA
from jira.exceptions import JIRAError
from pyaml_env import parse_config
from simple_logger.logger import get_logger
from qe_metrics.utils.general import verify_creds


class Jira:
    def __init__(self, creds_file: str) -> None:
        """
        Initialize the Jira class

        Args:
            creds_file (str): Path to the yaml file holding database and Jira credentials.
        """
        self.logger = get_logger(name=self.__class__.__module__)

        self.jira_creds = parse_config(creds_file)["jira"]

        if verify_creds(creds=self.jira_creds, required_keys=["token", "server"]):
            self.connection = self._connect(token=self.jira_creds["token"], server=self.jira_creds["server"])
        else:
            self.logger.error(f'Some or all configuration values in the "jira" section of {creds_file} are missing.')
            raise click.Abort()

    def _connect(self, server: str, token: str) -> JIRA:
        """
        Connect to Jira

        Args:
            server (string): Jira server
            token (string): Jira token

        Returns:
            JIRA: Jira connection
        """
        server = re.sub(r"^(http://)?(https://)?", "https://", server)

        try:
            connection = JIRA(server=server, token_auth=token)
            self.logger.info("Jira authentication successful")
            return connection
        except JIRAError as error:
            self.logger.error(f"Failed to connect to Jira: {error}")
            raise click.Abort()

    def search(self, query: str) -> list[Any]:
        """
        Performs a Jira JQL query using the Jira connection and returns a list of issues, including all fields.

        Args:
            query (str): JQL query to execute.

        Returns:
            list[Any]: List of Jira issues returned from the query.
        """
        try:
            return self.connection.search_issues(query, maxResults=False, validate_query=True)
        except JIRAError as error:
            self.logger.error(f"Failed to execute Jira query: {error}")
            raise click.Abort()
