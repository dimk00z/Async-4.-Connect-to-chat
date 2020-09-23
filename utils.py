import configargparse
import logging
import signal
import socket
import asyncio
import contextlib

from datetime import datetime

ATTEMPT_DELAY_SECS = 3


def keyboard_interrupt_handler(signal, frame):
    print('\n[Program was closed]')
    exit(0)


# @contextlib.asynccontextmanager
# async def open_connection(host, port, attempts=1):
#     global writer
#     for attempt in range(attempts):
#         try:
#             reader, writer = await asyncio.open_connection(
#                 host, port)
#             logging.debug('The connection opened')
#             signal.signal(signal.SIGINT, keyboard_interrupt_handler)
#             return reader, writer
#         except (
#             socket.gaierror,
#             ConnectionRefusedError,
#             ConnectionResetError,
#             ConnectionError,
#         ):
#             logging.debug(f'Could not connect to {host}:{port}')
#             await asyncio.sleep(3)
#             continue
#     logging.debug(
#         f'Host {host} is unavailable, the program will be terminated')
#     raise SystemExit


@contextlib.asynccontextmanager
async def open_connection(server, port, attempts=1):
    attempt = 0
    connected = False
    reader, writer = None, None
    while True:
        try:
            reader, writer = await asyncio.open_connection(server, port)
            logging.debug('The connection opened')
            signal.signal(signal.SIGINT, keyboard_interrupt_handler)
            connected = True
            yield reader, writer
            break

        except asyncio.CancelledError:
            raise

        except (ConnectionRefusedError, ConnectionResetError):
            if connected:
                logging.debug("The connection was closed")
                break
            if attempt >= attempts:
                logging.debug(
                    f"There is no connection. Next try in {ATTEMPT_DELAY_SECS} seconds")
                await asyncio.sleep(ATTEMPT_DELAY_SECS)
                continue
            attempt += 1
        finally:
            if all((reader, writer)):
                writer.close()
                await writer.wait_closed()
            logging.debug("Connection closed")


def get_message_with_datetime(message):
    formated_datetime = datetime.now().strftime('%d.%m.%Y %H:%M')
    return f'[{formated_datetime}] {message}'


def get_parser():
    parser = configargparse.get_argument_parser()

    parser.add_argument("-h", '--host', default='minechat.dvmn.org',
                        help="Host name", type=str)
    parser.add_argument("-a", '--attempts', default=3,
                        help="Attempts to reconnect", type=int)
    arg = parser.parse_args()
    return parser


def decode_message(message):
    return message.decode('utf-8').strip()


async def get_answer(reader, use_datetime=True):
    answer = decode_message(await reader.readline())
    if use_datetime:
        answer = get_message_with_datetime(answer)
    logging.debug(answer)
    return answer
