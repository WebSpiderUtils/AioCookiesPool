import json
import time
import random
import aredis
import asyncio
from typing import Optional
from aiocookiespool.config import *
from aiocookiespool.log import logger

# type of password
TOP = Optional[str]


class RedisClient(object):
    def __init__(
            self,
            operate: str,
            website: str,
            host: str = REDIS_HOST,
            port: int = REDIS_PORT,
            password: TOP = REDIS_PASSWORD,
            rdb: int = REDIS_DB
    ):
        """
        初始化Redis连接
        :param operate: 操作类型
        :param host: 地址
        :param port: 端口
        :param password: 密码
        """
        self.db = aredis.StrictRedis(host=host, port=port, password=password, decode_responses=True, db=rdb)
        self.operate = operate
        self.website = website

    def name(self):
        """
        获取Hash的名称
        :return: Hash名称
        """
        return "{operate}:{website}".format(operate=self.operate, website=self.website)

    async def set(self, username, value):
        """
        设置键值对
        :param username: 用户名
        :param value: 密码或Cookies
        :return:
        """
        return await self.db.hset(self.name(), username, value)

    async def get(self, username):
        """
        根据键名获取键值
        :param username: 用户名
        :return:
        """
        return await self.db.hget(self.name(), username)

    async def delete(self, username):
        """
        根据键名删除键值对
        :param username: 用户名
        :return: 删除结果
        """
        return await self.db.hdel(self.name(), username)

    async def count(self):
        """
        获取数目
        :return: 数目
        """
        return await self.db.hlen(self.name())

    async def random(self):
        """
        随机得到键值，用于随机Cookies获取
        :return: 随机Cookies
        """
        return random.choice(await self.db.hvals(self.name()))

    async def usernames(self):
        """
        获取所有账户信息
        :return: 所有用户名
        """
        return await self.db.hkeys(self.name())

    async def all(self) -> dict:
        """
        获取所有键值对
        :return: 用户名和密码或Cookies的映射表
        """
        return await self.db.hgetall(self.name())


if __name__ == '__main__':
    conn = RedisClient('blocklist', 'gsxt')
    result = asyncio.run(
        conn.set(
            '123123',
            json.dumps({"reason": "访问异常", "timestamp": int(time.time()), "total_time": 50}, ensure_ascii=False)
        )
    )
    logger.info(result)
