import configargparse
import logging
import signal
import socket
import asyncio
from datetime import datetime


def keyboard_interrupt_handler(signal, frame):
    print('\n[Close the connection]')
    writer.close()
    exit(0)


async def open_connection(host, port, attempts=1):
    global writer
    for attempt in range(attempts):
        try:
            reader, writer = await asyncio.open_connection(
                host, port)
            logging.debug('The connection opened')
            signal.signal(signal.SIGINT, keyboard_interrupt_handler)
            return reader, writer
        except (
            socket.gaierror,
            ConnectionRefusedError,
            ConnectionResetError,
            ConnectionError,
        ):
            logging.debug(f'Could not connect to {host}:{port}')
            await asyncio.sleep(3)
            continue
    logging.debug(
        f'Host {host} is unavailable, the program will be terminated')
    raise SystemExit


def get_message_with_datetime(message):
    formated_datetime = datetime.now().strftime('%d.%m.%Y %H:%M')
    return f'[{formated_datetime}] {message}'


def parse_args(is_listener):
    parser = configargparse.get_argument_parser()
    if is_listener:
        parser.add_argument("-f", '--file_name', default='minechat.history',
                            help="Chat history file name", type=str)
        parser.add_argument("-p", '--port', default=5000,
                            help="Port number", type=int)
    else:
        parser.add_argument("-t", '--token',
                            help="Chat token", type=str)
        parser.add_argument("-p", '--port', default=5050,
                            help="Port number", type=int)

    parser.add_argument("-h", '--host', default='minechat.dvmn.org',
                        help="Host name", type=str)
    parser.add_argument("-a", '--attempts', default=3,
                        help="Attempts to reconnect", type=int)
    arg = parser.parse_args()
    return arg


def decode_message(message):
    return message.decode('utf-8').strip()


async def logging_host_answer(reader, use_datetime=True):
    answer = decode_message(await reader.readline())
    if use_datetime:
        answer = get_message_with_datetime(answer)
    logging.debug(answer)
    return answer
