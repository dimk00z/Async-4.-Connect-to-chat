import asyncio
import aiofiles
import signal
import configargparse
from datetime import datetime


async def write_chat_line_to_file(chat_file_name, chat_line):
    async with aiofiles.open(chat_file_name, "a") as chat_history:
        await chat_history.write(chat_line)


def parse_args():
    parser = configargparse.get_argument_parser()
    parser.add_argument("-f", '--file_name', default='minechat.history',
                        help="Chat history file name", type=str)
    parser.add_argument("-p", '--port', default=5000,
                        help="Port number", type=int)
    parser.add_argument("-h", '--host', default='minechat.dvmn.org',
                        help="Host name", type=str)
    arg = parser.parse_args()
    return arg


def keyboardInterruptHandler(signal, frame):
    print('Close the connection')
    writer.close()
    exit(0)


async def tcp_echo_client(host, port,
                          chat_file_name):
    global writer
    reader, writer = await asyncio.open_connection(
        host, port)
    signal.signal(signal.SIGINT, keyboardInterruptHandler)
    while True:
        chat_data = await reader.readline()
        formated_datetime = datetime.now().strftime('%d.%m.%Y %H:%M')
        chat_line = f'[{formated_datetime}] {chat_data.decode()}'
        await write_chat_line_to_file(chat_file_name, chat_line)
        print(chat_line.rstrip('\n'))


def main():
    args = parse_args()
    host = args.host
    chat_file_name = args.file_name
    port = args.port
    asyncio.run(tcp_echo_client(host, port, chat_file_name))


if __name__ == "__main__":
    main()
