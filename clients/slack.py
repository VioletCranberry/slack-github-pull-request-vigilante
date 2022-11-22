from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

import logging
import utils


class SlackClient:
    """ Slack client class """

    def __init__(self, api_token: str):
        """
        Instantiate class instance
        :param api_token: api token (str)
        """
        logging.info('initialising slack client')
        self.client = WebClient(api_token)

    @utils.SlackClient.api_rate_control
    def get_channel_history(self, channel: str, minutes: int,
                            latest_ts: str = None):
        """
        Get channel messages. See
        https://api.slack.com/methods/conversations.history
        :param channel: slack channel id (str)
        :param minutes: look back window in mins (int)
        :param latest_ts: latest msg timestamp (str)
        :return: list of Slack messages
        """
        params = utils.SlackClient.set_conv_params(channel,
                                                   minutes,
                                                   latest_ts)
        try:
            history = self.client.conversations_history(**params)
            return history
        except SlackApiError as err:
            logging.info(f"error loading conv. history: {err}")
            return []

    def get_channel_messages(self, channel: str, minutes: int):
        """
        Wrapper around SlackClient.get_channel_history
        to provide easier pagination by time
        :param channel: slack channel id (str)
        :param minutes: look back window in mins (int)
        :return: list of messages/events
        """
        history = self.get_channel_history(channel, minutes)
        messages = history["messages"]

        while history.get("has_more"):
            last_ts = history["messages]"][-1]["ts"]
            history = self.get_channel_history(channel, minutes,
                                               last_ts)
            messages.extend(history["messages"])

        logging.info(f"fetched {len(messages)} messages")
        return messages

    @utils.SlackClient.api_rate_control
    def get_message_history(self, channel: str, minutes: int, ts: str,
                            latest_ts: str = None):
        """
        Get message threads / replies. See
        https://api.slack.com/methods/conversations.replies
        :param channel: slack channel id (str)
        :param minutes: look back window in mins (int)
        :param ts: timestamp of slack message
        :param latest_ts: latest msg timestamp (str)
        :return: list of message replies
        """
        params = utils.SlackClient.set_conv_params(channel, minutes, latest_ts)
        params["ts"] = ts
        try:
            threads = self.client.conversations_replies(**params)
            return threads
        except SlackApiError as err:
            logging.info(f"error loading message replies: {err}")
            return []

    def get_message_replies(self, channel: str, minutes: int, ts: str):
        """
        Wrapper around SlackClient.get_message_history
        to provide easier pagination by time
        :param channel: slack channel id (str)
        :param minutes: look back window in mins (int)
        :param ts: slack message ts
        :return: list of message threads/replies
        """
        history = self.get_message_history(channel, minutes, ts)
        replies = history["messages"]

        while history.get("has_more"):
            last_ts = history["messages]"][-1]["ts"]
            history = self.get_message_history(channel, minutes,
                                               ts, last_ts)
            replies.extend(history["messages"])

        logging.info(f"fetched {len(replies)} replies for message {ts}")
        return replies

    @utils.SlackClient.api_rate_control
    def add_message_reaction(self, channel: str, reaction: str,
                             timestamp: str):
        """
        Add reaction to array of reactions
        see https://api.slack.com/events/message#stars__pins__and_reactions
        :param channel: channel id (str)
        :param reaction: reaction (str)
        :param timestamp: message timestamp (str)
        :return: bool
        """
        try:
            logging.info(f"adding reaction '{reaction}' to message")
            self.client.reactions_add(channel=channel,
                                      name=reaction,
                                      timestamp=timestamp)
            return True
        except SlackApiError as err:
            logging.info(f"error reacting to message: {err}")
            return False
