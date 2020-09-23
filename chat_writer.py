import asyncio
import signal
import configargparse
import json
import logging
import re
from utils import get_message_with_datetime, get_parser, \
    decode_message, open_connection, get_answer


def sanitize(message):
    return message.replace("\n", "").replace("\r", "")


async def write_message_to_chat(writer, message=''):
    message = "{}\n\n".format(sanitize(message))
    writer.write(message.encode())
    await writer.drain()


def get_user_text(string):
    return input(string)


async def register_user(reader, writer, after_incorrect_login=False):
    if after_incorrect_login == False:
        host_answer = await get_answer(reader)
        await write_message_to_chat(writer)
    host_answer = await get_answer(reader)
    nick_name = get_user_text('Enter your nick name: ')
    await write_message_to_chat(writer, nick_name)
    credentials = json.loads(await reader.readline())
    logging.debug(credentials)
    return credentials


async def authorise(token, reader, writer):
    host_answer = await get_answer(reader)
    await write_message_to_chat(writer, token)
    response = json.loads(await reader.readline())
    logging.debug(response)
    if response is None:
        print('The current token is incorrect, we are going to create new user.')
        return await register_user(reader, writer, after_incorrect_login=True)
    return response


async def submit_message(reader, writer):
    host_answer = await get_answer(reader)
    message = get_user_text('Enter your message: ')
    await write_message_to_chat(writer, message)
    logging.debug(get_message_with_datetime(message))


async def write_to_chat(host, port,
                        token, attempts):
    async with open_connection(host, port, attempts) as rw:
        reader, writer = rw
        if token:
            credentials = await authorise(token, reader, writer)
        else:
            credentials = await register_user(reader, writer)
        print(credentials)
        while True:
            await submit_message(reader, writer)


def get_writer_args(parser):
    parser.add_argument("-t", '--token',
                        help="Chat token", type=str)
    parser.add_argument("-p", '--port', default=5050,
                        help="Port number", type=int)
    return parser.parse_args()


def main():
    parser = get_parser()
    args = get_writer_args(parser)
    host = args.host
    token = args.token
    port = args.port
    attempts = args.attempts
    logging.basicConfig(level=logging.DEBUG)

    asyncio.run(write_to_chat(host, port, token, attempts))


if __name__ == "__main__":
    main()
