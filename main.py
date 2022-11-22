import logging
import asyncio

import configargparse

from clients import GitHubClient, SlackClient
from helpers import PullRequest, SlackMessage
import utils


def get_arguments():
    parser = configargparse.ArgParser()

    parser.add_argument("-st",
                        "--slack_api_token",
                        action="store",
                        type=str,
                        required=True,
                        env_var="SLACK_API_TOKEN")
    parser.add_argument("-cid",
                        "--channel_id",
                        action="store",
                        type=str,
                        required=True,
                        env_var="CHANNEL_ID")
    parser.add_argument("-tw",
                        "--time_window",
                        action="store",
                        type=int,
                        required=True,
                        env_var="TIME_WINDOW")
    parser.add_argument("-rn",
                        "--reaction_name",
                        action="store",
                        type=str,
                        required=False,
                        default="white_check_mark",
                        env_var="REACTION_NAME")
    parser.add_argument("-gt",
                        "--github_api_token",
                        action="store",
                        type=str,
                        required=True,
                        env_var="GITHUB_API_TOKEN")
    parser.add_argument("-sp",
                        "--sleep_period",
                        action="store",
                        type=bool,
                        required=True,
                        env_var="SLEEP_PERIOD")
    parser.add_argument("-d",
                        "--debug",
                        action="store_true",
                        required=False,
                        env_var="DEBUG")
    return parser.parse_args()


async def process_message(args: configargparse,
                          slack_client: SlackClient,
                          github_client: GitHubClient,
                          message: SlackMessage):
    """
    Process a single Slack message:
    - check if message is approved
    - check if message has PRs
    - check if all PRs were approved
    - react to the message accordingly
    :param args:          instance of configargparse
    :param slack_client:  instance of SlackClient class
    :param github_client: instance of GitHubClient cls
    :param message:       instance of SlackMessage cls
    :return:
    """
    if not message.is_approved and message.pull_reqs:
        states = []
        for pr_url in message.pull_reqs:
            pull_request = PullRequest(github_client, pr_url)
            states.append(pull_request.is_approved)

            if all(state for state in states):
                slack_client.add_message_reaction(
                    args.channel_id,
                    args.reaction_name,
                    message.timestamp)


async def process_messages(args: configargparse, slack_client: SlackClient,
                           github_client: GitHubClient):
    """
    Fetch all messages and process them
    :param args:          instance of configargparse
    :param slack_client:  instance of SlackClient class
    :param github_client: instance of GitHubClient cls
    :return:
    """
    sleep_period = args.sleep_period * 60

    messages = slack_client.get_channel_messages(args.channel_id,
                                                 args.time_window)

    for message in messages:

        # ts is a timestamp of an existing message with 0 or more replies.
        # if there are no replies then just the single message referenced
        # by ts will return - it is just an ordinary message.

        threads = slack_client.get_message_replies(
            args.channel_id,
            args.time_window,
            message["ts"])

        for thread_message in threads:
            utils.SlackMessage.log_message(
                thread_message)

            thread_message = SlackMessage(thread_message, args.reaction_name)
            await process_message(args, slack_client,
                                  github_client,
                                  thread_message)

    logging.info("finished processing messages")
    await asyncio.sleep(sleep_period)


def main():
    args = get_arguments()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                        format="%(asctime)4s - "
                               "%(module)8s: - "
                               "%(levelname)5s - "
                               "%(message)4s")

    slack_client = SlackClient(args.slack_api_token)
    github_client = GitHubClient(args.github_api_token,
                                 args.debug)

    while True:
        loop = asyncio.get_event_loop()
        task = [loop.create_task(
            process_messages(args, slack_client,
                             github_client))]
        loop.run_until_complete(
            asyncio.wait(task))


if __name__ == '__main__':
    main()
