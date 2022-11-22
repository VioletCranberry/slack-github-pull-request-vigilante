import logging
import re

import utils


class SlackMessageData:
    """ Slack Raw Message Data Parser """
    def __init__(self, slack_message: dict):
        """
        Instantiate class instance
        :param slack_message: Slack message (dict)
        """
        self.raw_message = slack_message

        self.timestamp = self.raw_message["ts"]
        self.blocks = self.parse_msg_blocks()
        self.elements = self.parse_elements()

    def parse_msg_blocks(self):
        """
        Return all message layout blocks
        :return: list of message blocks
        """
        if "blocks" in self.raw_message.keys():
            msg_blocks = [msg_block for msg_block
                          in self.raw_message.get("blocks")]

            logging.info(f"found {len(msg_blocks)} message blocks")
            logging.debug(f"message blocks: {msg_blocks}")
            return msg_blocks
        else:
            logging.info("message has no blocks")
            return []

    def get_block_elements(self, block: dict, block_elements: [] = None):
        """
        Recursively iterate through layout block elements.
        Each element can have nested blocks with elements
        :param block: Slack message block
        :param block_elements: list of block elements
        :return: list of block elements
        """
        if block_elements is None:
            block_elements = []

        if block.get("elements"):

            for block_element in block.get("elements"):
                if "elements" not in block_element.keys():
                    block_elements.append(block_element)
                else:

                    for element in block_element.get("elements"):
                        if "elements" not in element.keys():
                            block_elements.append(element)
                        else:
                            self.get_block_elements(
                                element, block_elements)

        return block_elements

    def parse_elements(self):
        """
        Get all message elements from all blocks
        :return: list of elements
        """
        if self.blocks:
            message_elements = []
            for block in self.blocks:
                block_elements = self.get_block_elements(block)
                message_elements.extend(block_elements)

            logging.info(f"found {len(message_elements)} message"
                         f" elements")
            logging.debug(f"message elements: {message_elements}")
            return message_elements
        else:
            logging.info("message has no elements")
            return []


class SlackMessage(SlackMessageData):
    """ Slack custom data parser """

    def __init__(self, slack_message: dict, slack_reaction: str):
        """
        Instantiate child class instance
        :param slack_message:  Slack message (dict)
        :param slack_reaction: Slack reaction
        """
        self.reaction = slack_reaction
        super().__init__(slack_message)

        self.is_approved = utils.SlackMessage.lookup_reaction(
            self.raw_message, self.reaction)
        self.urls = self.get_msg_urls()
        self.pull_reqs = self.parse_pr_urls()

    def get_msg_urls(self):
        """
        Look up URLs in the list message elements
        :return: list of URLs
        """
        urls = [element.get("url")
                for element in self.elements
                if element.get("type") == "link"]
        if urls:
            logging.info(f"found {len(urls)} message urls")
            logging.debug(f"urls: {urls}")
            return urls
        else:
            logging.info("message has no urls")
            return []

    def parse_pr_urls(self):
        """
        Look up GitHub PRs in the list of web urls
        :return: list of PRs
        """
        re_pattern = r"http[s]://github.com/.+/pull/\d+"
        pr_urls = [match.group() for url in self.urls
                   if (match := re.search(re_pattern, url)
                       )]
        if pr_urls:
            logging.info(f"found {len(pr_urls)} pull requests")
            logging.debug(f"pull requests: {pr_urls}")
            return pr_urls
        else:
            logging.info("message has no pull requests")
            return []
