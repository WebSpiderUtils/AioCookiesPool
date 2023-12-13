import json
import time
import asyncio
from asyncio import gather
from typing import NoReturn
from asyncio import Semaphore
from aiocookiespool.log import logger
from aiocookiespool.db import RedisClient
from aiocookiespool.config import MONITOR_CONCURRENCE


class Monitor:
    def __init__(self, website='default'):
        self.website = website
        self.blocklist_db = RedisClient('blocklist', self.website)
        self.tasks = []

    async def task(self, username: str, sem: Semaphore) -> NoReturn:
        async with sem:
            if await self.blocklist_db.delete(username):
                logger.info(f'剔除黑名单：{username}')

    async def run(self):
        sem = Semaphore(MONITOR_CONCURRENCE)
        blocklist_groups = await self.blocklist_db.all()
        for username, item in blocklist_groups.items():
            logger.info(f'正在检查账号：{username}')
            item2json = json.loads(item)
            enter_time = item2json.get('timestamp')
            total_time = item2json.get('total_time')
            now = int(time.time())
            slept_time = now - enter_time
            remaining_time = total_time - slept_time
            if slept_time >= total_time:
                self.tasks.append(self.task(username, sem))
            else:
                logger.info(f'仍需睡眠：{username} 剩余时间：{remaining_time} 秒')
        await gather(*self.tasks)
        logger.success("黑名单检查结束")

    def main(self):
        asyncio.run(self.run())


if __name__ == '__main__':
    Monitor().main()
