import json
import time
import asyncio
from typing import NoReturn
from asyncio import Semaphore, gather
from aiocookiespool.log import logger
from aiocookiespool.db import RedisClient
from login.gsxt.cookies import GsxtCookies
from aiocookiespool.config import GENERATOR_CONCURRENCE


class CookiesGenerator(object):
    def __init__(self, website: str = 'default'):
        """
        父类, 初始化一些对象
        :param website: 名称
        """
        self.website = website
        self.cookies_db = RedisClient('cookies', self.website)
        self.accounts_db = RedisClient('accounts', self.website)
        self.blocklist_db = RedisClient('blocklist', self.website)
        self.tasks = []

    def __del__(self):
        self.close()

    async def new_cookies(self, username: str, password: str) -> dict:
        """
        新生成Cookies，子类需要重写
        :param username: 用户名
        :param password: 密码
        :return: {'status': 1, 'content': {}}
        """
        raise NotImplementedError

    async def get_cookies_failed(self, username: str) -> NoReturn:
        """
        cookie生成失败由子类处理
        :param username:
        :return:
        """
        raise NotImplementedError

    async def task(self, username: str, sem: Semaphore) -> NoReturn:
        async with sem:
            password = await self.accounts_db.get(username)
            logger.info(f'正在生成Cookies，账号: {username}')
            result = await self.new_cookies(username, password)
            # 成功获取
            if result.get('status') == 1:
                cookies = result.get('content')
                cookie_and_username = {"username": username, "cookies": cookies}
                logger.info(f'成功获取到Cookies: {cookies}')
                if await self.cookies_db.set(username, json.dumps(cookie_and_username)):
                    logger.success('成功保存Cookies')
            # 密码错误，移除账号
            elif result.get('status') == 2:
                logger.warning(f'账号密码错误: {username}')
                if await self.accounts_db.delete(username):
                    logger.warning(f'成功删除账号: {username}')
            # 获取cookie失败，账号加入黑名单休眠一段时间
            else:
                await self.get_cookies_failed(username)

    async def run(self) -> NoReturn:
        """
        运行, 得到所有账户, 然后顺次登陆获取cookie
        :return:
        """
        sem = Semaphore(GENERATOR_CONCURRENCE)
        accounts_usernames = await self.accounts_db.usernames()
        cookies_usernames = await self.cookies_db.usernames()
        blocklist_usernames = await self.blocklist_db.usernames()
        for username in accounts_usernames:
            if username not in cookies_usernames and username not in blocklist_usernames:
                self.tasks.append(self.task(username, sem))
        await gather(*self.tasks)
        logger.success(f'{self.website} 所有账号都已经成功获取Cookies')

    def main(self):
        asyncio.run(self.run())

    def close(self):
        """
        关闭
        :return:
        """
        pass


class GsxtCookiesGenerator(CookiesGenerator):
    def __init__(self, website='gsxt'):
        CookiesGenerator.__init__(self, website)
        self.website = website

    async def new_cookies(self, username, password):
        return await GsxtCookies(username, password).login()

    async def get_cookies_failed(self, username: str) -> NoReturn:
        """
        账号获取cookie失败，放入黑名单中休眠total_time
        :param username:
        :return:
        """
        logger.info('Cookie获取失败')
        await self.blocklist_db.set(
            username=username,
            value=json.dumps({
                "timestamp": int(time.time()),
                "total_time": 18000,
                "reason": "Cookie获取失败"
            }, ensure_ascii=False)
        )
        logger.info(f'账号放入黑名单：{username}')


if __name__ == '__main__':
    CookiesGenerator().main()

