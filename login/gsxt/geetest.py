import asyncio
import aiohttp
from aiocookiespool.log import logger
from login.gsxt.config import GEETEST_API


class Geetest:
    def __init__(self, api: str = GEETEST_API):
        self.api = api

    async def apis(self) -> dict:
        """
        获取geetest验证码结果
        :return: {'captcha_id': '**', 'lot_number': '**', 'pass_token': '**', 'gen_time': '**', 'captcha_output': '***'}
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api) as rsp:
                data = await rsp.json()
                info = data['data']['data']['seccode']
                logger.success(info)
                return info


if __name__ == '__main__':
    g = Geetest()
    asyncio.run(g.apis())
