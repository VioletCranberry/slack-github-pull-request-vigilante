from functools import wraps
import logging

import helpers


class GitClient:
    """ GitClient class of client helper functions """

    @staticmethod
    def debug_request(req: dict):
        """
        Log API request
        :param req: request (dict)
        :return: None
        """
        request = vars(req)
        logging.debug(f"request data: {request}")

    @staticmethod
    def api_rate_control(func):
        """
        Wrapper for GitHub api rate control
        :param func: function
        :return: wrapper
        """
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            while True:
                core = self.get_rate_core_data()
                if core["remaining"] == 0:
                    time_wait = float(core["reset"])
                    helpers.sleep_until(time_wait)
                    continue
                else:
                    logging.info(f"api quota remaining: "
                                 f"{core['remaining']} "
                                 f"of {core['limit']}")

                    logging.info(f"api quota used:"
                                 f" {core['used']}")
                    logging.info(f"api quota reset time:"
                                 f" {core['reset']}")
                    result = func(self, *args, **kwargs)
                    return result
        return wrapper
