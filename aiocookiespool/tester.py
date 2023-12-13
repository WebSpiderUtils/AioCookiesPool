import asyncio
from asyncio import gather
from typing import NoReturn
from asyncio import Semaphore
from aiocookiespool.log import logger
from aiocookiespool.db import RedisClient
from aiocookiespool.config import VALID_CONCURRENCE


class ValidTester(object):
    def __init__(self, website='default'):
        self.website = website
        self.cookies_db = RedisClient('cookies', self.website)
        self.accounts_db = RedisClient('accounts', self.website)
        self.blocklist_db = RedisClient('blocklist', self.website)
        self.tasks = []
    
    def test(self, username: str, cookies: dict, sem: Semaphore) -> NoReturn:
        raise NotImplementedError
    
    async def run(self):
        sem = Semaphore(VALID_CONCURRENCE)
        cookies_groups = await self.cookies_db.all()
        blocklist_usernames = await self.blocklist_db.usernames()
        for username, cookies in cookies_groups.items():
            if username in blocklist_usernames:
                logger.info('账号已入黑名单')
                if await self.cookies_db.delete(username):
                    logger.warning(f'删除Cookies: {username}')
            else:
                self.tasks.append(self.test(username, cookies, sem))
        await gather(*self.tasks)
        logger.success('所有账号测试完成')

    def main(self):
        asyncio.run(self.run())


if __name__ == '__main__':
    ValidTester().main()


