import asyncio
import aiohttp
from aiocookiespool.log import logger
from login.gsxt.config import PROXY_API
from tenacity import retry, wait_fixed


class Proxy:
    def __init__(self, api: str = PROXY_API):
        self.api = api

    @retry(wait=wait_fixed(5))
    async def proxies(self) -> str:
        """
        获取适合aiohttp的代理
        :return: 'https://***.***.***.***:***'
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api) as response:
                text = await response.text()
                text = text.strip('"')
                logger.success(f"[proxy-from-api] - {text}")
                return text


if __name__ == '__main__':
    p = Proxy()
    asyncio.run(p.proxies())
