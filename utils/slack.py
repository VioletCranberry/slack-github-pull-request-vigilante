from datetime import datetime, timedelta
from functools import wraps
import logging

from slack_sdk.errors import SlackApiError
import helpers


class SlackClient:
    """ SlackClient class of client helper functions """

    @staticmethod
    def set_oldest_ts(minutes: int):
        """
        Return timestamp from the past based on the
         amount of minutes provided
        :param minutes: minutes (int)
        :return: timestamp (str)
        """
        init_time = datetime.now()
        oldest = init_time - timedelta(
            minutes=minutes)
        return str(oldest.timestamp())

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
                try:
                    result = func(self, *args, **kwargs)
                    return result
                except SlackApiError as err:
                    if err.response.headers['Retry-After']:
                        time_wait = float(err.response["headers"]["Retry-After"])
                        helpers.sleep_until(time_wait)
                        continue
                    else:
                        break

        return wrapper

    @staticmethod
    def set_conv_params(channel: str, minutes: int,
                        latest_ts: str = None):
        """
        Methods app.client.conversations_replies and app.client.conversations_history
        are accepting the same optional parameters
        :param channel: slack channel id (str)
        :param minutes: look back window in minutes (int)
        :param latest_ts: latest message timestamp
        :return: dict of common methods' parameters
        """
        # set oldest_ts ts based on minutes to look back
        oldest_ts = SlackClient.set_oldest_ts(minutes)
        # set latest_ts to current time if not provided
        latest_ts = latest_ts if latest_ts else str(datetime.now().timestamp())

        params = {
            "latest": latest_ts,
            "oldest": oldest_ts,
            "channel": channel,
            "limit": 100,
            "inclusive": True
        }
        return params


class SlackMessage:
    """ SlackMessage class of common Slack message utils """

    @staticmethod
    def log_message(raw_message: dict):
        """
        Log message timestamp and entire object
        :param raw_message: Slack message object
        :return:
        """
        logging.info(f"processing message {raw_message.get('ts')}")
        logging.debug(f"{raw_message}")

    @staticmethod
    def get_msg_reactions(raw_message: dict):
        """
        Get a list of message reactions
        :param raw_message: Slack message object
        :return: list of reactions
        """
        if "reactions" in raw_message.keys():
            reactions = [msg_reaction.get("name")
                         for msg_reaction
                         in raw_message.get("reactions")]

            logging.info(f"found {len(reactions)} message user reactions")
            logging.debug(f"user reactions: {reactions}")
            return reactions
        else:
            logging.info("message has no user reactions")
            return []

    @staticmethod
    def lookup_reaction(raw_message: dict, reaction: str):
        """
        Look up if message already has a reaction
        :param raw_message: Slack message object
        :param reaction:    Slack reaction to search for
        :return: True or False (bool) based on reaction lookup
        """
        msg_reactions = SlackMessage.get_msg_reactions(raw_message)
        if msg_reactions and reaction in msg_reactions:
            logging.info(f"message has reaction '{reaction}'")
            return True
        else:
            logging.info(f"message has no reaction '{reaction}'")
            return False
