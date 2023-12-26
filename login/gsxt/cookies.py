import aiohttp
from yarl import URL
from login.gsxt.net import Net
from urllib.parse import urljoin
from login.gsxt.exception import *
from fake_useragent import UserAgent
from aiocookiespool.log import logger
from login.gsxt.geetest import Geetest
from tenacity import retry, stop_after_attempt
from aiohttp import ClientSession, TCPConnector


BASE_URL = 'https://shiming.gsxt.gov.cn'


def _callback(retry_state):
    """
    重试错误
    :param retry_state:
    :return:
    """
    logger.error(retry_state)
    return {
        'status': 3,
        'content': None
    }


class GsxtCookies(object):
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.net_client = Net()
        self.geetest_client = Geetest()

    def get_cookies(self, session: ClientSession) -> dict:
        """
        获取session中的cookie
        :param session:
        :return:
        """
        cookies = session.cookie_jar.filter_cookies(URL(BASE_URL))
        c = {}
        for k, v in cookies.items():
            c[v.key] = v.value
        if not c.get('SECTOKEN'):
            raise SectokenNotInCookies
        logger.success(f'成功获取cookies: {c}')
        return c

    @retry(retry_error_callback=_callback, stop=stop_after_attempt(3), reraise=True)
    async def login(self) -> dict:
        timeout = aiohttp.ClientTimeout(total=60)
        jar = aiohttp.CookieJar(unsafe=True)
        connector = TCPConnector(ssl=False)
        _index = urljoin(BASE_URL, 'index.html')
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;"
                      "q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "shiming.gsxt.gov.cn",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": UserAgent().random
        }
        async with aiohttp.ClientSession(timeout=timeout, connector=connector, cookie_jar=jar) as session:
            html, proxy = await self.net_client.get(url=_index, conn=session, headers=headers, allow_status=[200, 302])
            geetest_data = await self.geetest_client.apis()
            login_data = {
                "un": self.username,
                "gp": self.password,
                "gen_time": geetest_data['gen_time'],
                "lot_number": geetest_data['lot_number'],
                "pass_token": geetest_data['pass_token'],
                "captcha_output": geetest_data['captcha_output'],
                'captchaId': 'b608ae7850d2e730b89b02a384d6b9cc'
            }
            login_url = urljoin(BASE_URL, 'socialuser-use-login-request.html')
            html, proxy = await self.net_client.post(
                url=login_url, conn=session, headers=headers, data=login_data, proxy=proxy
            )
            if html == '{"message":"","success":true,"value":"1"}':
                headers['Referer'] = urljoin(BASE_URL, 'socialuser-use-rllogin.html')
                await self.net_client.get(url=_index, conn=session, headers=headers)
                return {'status': 1, 'content': self.get_cookies(session)}
            elif html == '{"message":"用户名或密码错误！","success":true,"value":"0"}':
                return {'status': 2, 'content': None}
            else:
                raise UnknownReturnWithLoginPage
