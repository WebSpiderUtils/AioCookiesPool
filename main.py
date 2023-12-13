import asyncio
import argparse
from aiocookiespool.log import logger
from aiocookiespool.scheduler import Scheduler


parser = argparse.ArgumentParser(description='AioCookiesPool')
parser.add_argument('--processor', type=str, help='processor to run')
args = parser.parse_args()

if __name__ == '__main__':
    try:
        if args.processor:
            asyncio.run(getattr(Scheduler(), f'{args.processor}')())
        else:
            asyncio.run(Scheduler().run())
    except KeyboardInterrupt:
        logger.warning('主动终止程序')

