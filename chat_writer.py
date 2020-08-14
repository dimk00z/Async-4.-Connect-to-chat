import asyncio
import signal
import configargparse
import json
import logging
from utils import get_message_with_datetime, parse_args, \
    decode_message, logging_host_answer, open_connection


async def write_message_to_chat(writer, message=None):
    if not message:
        message = f'\n'
    else:
        message = f'{message}\n'
    writer.write(message.encode())
    await writer.drain()


async def register_user(reader, writer, after_incorrect_login=False):
    if after_incorrect_login == False:
        await logging_host_answer(reader)
        await write_message_to_chat(writer)
    await logging_host_answer(reader)
    nick_name = input('Enter your nick name: ')
    await write_message_to_chat(writer, nick_name)
    credentials = json.loads(await reader.readline())
    logging.debug(credentials)
    return credentials


async def authorise(token, reader, writer):
    await logging_host_answer(reader)
    await write_message_to_chat(writer, token)
    response = json.loads(await reader.readline())
    logging.debug(response)
    if response is None:
        print('The current token is incorrect, we are going to create new user.')
        return await register_user(reader, writer, after_incorrect_login=True)
    return response


async def submit_message(reader, writer):
    await logging_host_answer(reader)
    message = input('Enter your message: ')
    await write_message_to_chat(writer, f'{message}\n')
    logging.debug(get_message_with_datetime(message))


async def write_to_chat(host, port,
                        token, attempts):
    reader, writer = await open_connection(
        host, port, attempts)
    if token:
        credentials = await authorise(token, reader, writer)
    else:
        credentials = await register_user(reader, writer)
    print(credentials)
    while True:
        await submit_message(reader, writer)


def main():
    args = parse_args(is_listener=False)
    host = args.host
    token = args.token
    port = args.port
    attempts = args.attempts
    logging.basicConfig(level=logging.DEBUG)

    asyncio.run(write_to_chat(host, port, token, attempts))


if __name__ == "__main__":
    main()
