from datetime import datetime
import logging
import sys

from ghapi.all import GhApi, pages
import utils


class GitHubClient:
    """ GitHub client class """

    def __init__(self, api_token: str, debug: bool = False):
        """
        Instantiate class instance
        :param api_token: api token (str)
        :param debug:     debug mode (bool)
        """
        self.token = api_token
        self.client = self.init_client()
        if debug:
            self.client.debug = utils.GitClient.debug_request

    def init_client(self):
        """
        Set up GitHub API client
        :return: ghapi.core.GhApi object
        """
        logging.info("initialising github client")
        try:
            return GhApi(token=self.token)
        except Exception as err:
            logging.fatal(err)
            sys.exit(1)

    def get_rate_core_data(self):
        """
        Get API rate limit details
        see https://docs.github.com/en/rest/rate-limit
        :return: api core data (dict):
        """
        rate = self.client.rate_limit.get()
        data = rate["resources"]["core"]

        keys = ["used", "remaining", "limit", "reset"]
        core = {key: data.get(key) for key in keys}
        reset_time = datetime.fromtimestamp(
            core.get('reset'))

        core.update({'reset': reset_time})
        return core

    @utils.GitClient.api_rate_control
    def get_pr_reviews(self, repo_owner: str,
                       repo_name: str, pull_number: int):
        """
        Get pull request reviews for a single PR
        see https://docs.github.com/en/rest/pulls/reviews#list-reviews-for-a-pull-request
        :param repo_owner: owner of the repo (str)
        :param repo_name:  repository name (str)
        :param pull_number: pull request number (int)
        :return: list of PR reviews (list of dicts)
        """
        params = {
            "pull_number": pull_number,
            "owner": repo_owner,
            "repo": repo_name,
            "per_page": 100
        }
        try:
            reviews = self.client.pulls.list_reviews(**params)

            # paginate if more results are available
            if self.client.last_page() > 0:
                reviews = pages(self.client.pulls.list_reviews,
                                self.client.last_page(),
                                **params)

            logging.info(f"found {len(reviews)} reviews")
            logging.debug(f"reviews: {reviews}")
            return reviews

        except Exception as err:
            logging.error(f"error fetching reviews: {err}")
            return []
