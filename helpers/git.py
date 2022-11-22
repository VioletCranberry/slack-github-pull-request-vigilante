from urllib import parse
import logging


class PullRequest:
    """ GitHub Pull Request helper class """
    def __init__(self, client, url: str):
        """
        Instantiate class instance
        :param client: clients.git.GitHubClient (cls)
        :param url:    GitHub pull request web url (str)
        """
        self.client = client

        self.pr_url = url
        self.pull_url = parse.urlparse(self.pr_url)
        self.url_path = self.pull_url.path

        self.params = self.params_from_path()
        self.reviews = self.load_pr_reviews()
        self.is_approved = self.is_approved()

    def params_from_path(self):
        """
        Split url path and generate params for
        self.client.get_pr_reviews method call
        :return: params (dict)
        """
        url_path = self.url_path.split("/")
        try:
            params = {
                "repo_owner": url_path[1],
                "repo_name": url_path[2],
                "pull_number": url_path[4]
            }
            logging.debug(f"using params: {params}")
            return params
        except IndexError:
            logging.warning(f"received invalid url path")
            return {}

    def load_pr_reviews(self):
        """
        Get pull request reviews
        :return: reviews (list of dict)
        """
        if self.params:
            logging.info(f"processing pull request {self.pr_url}")
            reviews = self.client.get_pr_reviews(**self.params)
            return reviews
        else:
            return []

    def is_approved(self):
        """
        Check if last review action was PR approval
        :return: True if approved, otherwise False (bool)
        """
        if self.reviews:
            pr_states = [review.get("state") for review
                         in self.reviews]
            if pr_states:
                if pr_states[-1] == "APPROVED":
                    logging.info("pull request is approved")
                    return True
        logging.info("pull request is not approved")
        return False
