import re
import json
import execjs
import asyncio
import aiohttp
import hashlib
from lxml import etree
from typing import Tuple
from login.gsxt.exception import *
from login.gsxt.proxy import Proxy
from fake_useragent import UserAgent
from aiocookiespool.log import logger
from aiohttp import ClientResponse, ClientSession


class Net:
    def __init__(self):
        self.proxy_client = Proxy()

    @staticmethod
    def ex_jsl(js: str) -> str:
        """
        处理加速乐js
        :param js:
        :return:
        """
        result = ''

        def case_1():
            data = json.loads(re.findall('go\((.*?)\)', js)[1])
            chars_length = len(data.get('chars'))
            for i in range(chars_length):
                for j in range(chars_length):
                    result = data.get('bts')[0] + data.get('chars')[i] + data.get('chars')[j] + data.get('bts')[1]
                    b = eval('hashlib.{}()'.format(data.get('ha')))
                    b.update(result.encode(encoding='utf-8'))
                    res = b.hexdigest()
                    if res == data.get('ct'):
                        return result

        def case_2():
            _js = js.split('location.href=loc')[0].replace('document.cookie=', '')
            k = '''
            function cracker() {
                s = eval(%r)
                return s
            }
            ''' % _js
            r = execjs.compile(k)
            s = r.call('cracker').split(';')[0]
            return s
        if "=['" in js[:25]:
            result = case_1()
        if 'location.href=location.pathname' in js:
            result = case_2()
        logger.debug(result)
        return result

    async def request(
            self,
            method: str,
            conn: ClientSession,
            url: str,
            headers: dict,
            data: dict = None,
            proxy: str = '',
            allow_status: list = None
    ) -> Tuple[ClientResponse, str]:
        if allow_status is None:
            allow_status = [200]
        method = method.lower()
        if not proxy:
            proxy = await self.proxy_client.proxies()
        while True:
            try:
                resp = await eval(f"conn.{method}")(url, headers=headers, proxy=proxy, data=data, allow_redirects=False)
                html = await resp.text()
                status = resp.status
                logger.debug(status)
                if status in allow_status:
                    return resp, proxy
                elif status == 521:
                    parser = etree.HTML(html)
                    js_content = parser.xpath("//script/text()")[0]
                    __jsl_clearance = self.ex_jsl(js_content).split('=')[-1]
                    conn.cookie_jar.update_cookies({"__jsl_clearance_s": __jsl_clearance}, response_url=resp.url)
                else:
                    raise UnknownStatus(status)
            except Exception as e:
                logger.exception(e)
                proxy = await self.proxy_client.proxies()

    async def get(
            self,
            url: str,
            conn: ClientSession,
            headers: dict,
            data: dict = None,
            proxy: str = '',
            allow_status: list = None
    ) -> Tuple[ClientResponse, str]:
        return await self.request('get', conn, url, headers, data, proxy, allow_status)

    async def post(
            self,
            url: str,
            conn: ClientSession,
            headers: dict,
            data: dict = None,
            proxy: str = '',
            allow_status: list = None
    ) -> Tuple[ClientResponse, str]:
        return await self.request('post', conn, url, headers, data, proxy, allow_status)


async def test():
    n = Net()
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;"
                  "q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "shiming.gsxt.gov.cn",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": UserAgent().random
    }
    async with aiohttp.ClientSession() as session:
        logger.debug(
            await n.get(url="https://shiming.gsxt.gov.cn", conn=session, headers=headers, allow_status=[200, 302])
        )


if __name__ == '__main__':
    asyncio.run(test())


