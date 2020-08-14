import asyncio
import aiofiles
import configargparse
import logging
from utils import get_message_with_datetime, parse_args, \
    decode_message, logging_host_answer, open_connection


async def write_chat_line_to_file(chat_file_name, chat_line):
    async with aiofiles.open(chat_file_name, "a") as chat_history:
        await chat_history.write(chat_line)


async def listen_to_chat(host, port,
                         chat_file_name, attempts):
    reader, writer = await open_connection(host, port, attempts)
    while True:
        chat_line = await logging_host_answer(reader)
        await write_chat_line_to_file(chat_file_name, f'{chat_line}\n')


def main():
    args = parse_args(is_listener=True)
    host = args.host
    attempts = args.attempts
    chat_file_name = args.file_name
    port = args.port
    asyncio.run(listen_to_chat(host, port, chat_file_name, attempts))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
