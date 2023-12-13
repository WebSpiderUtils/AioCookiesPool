import json
import logging
from aiohttp import web
from aiocookiespool.db import RedisClient
from aiocookiespool.log import logger
from aiocookiespool.config import API_PORT


routes = web.RouteTableDef()


def get_conn(t, website):
    return RedisClient(t, website)


@routes.get('/')
async def index(request):
    text = '<h2>Welcome to AioCookiesPool System</h2>'
    return web.Response(text=text, content_type='text/html')


@routes.get('/{website}/infos')
async def infos(request):
    """
    信息总览，查看库中cookie生成的情况
    :param request:
    :return:
    """
    website = request.match_info['website']
    accounts = get_conn('accounts', website)
    cookies = get_conn('cookies', website)
    blocklist = get_conn('blocklist', website)
    accounts_count = await accounts.count()     # 账号总量
    cookies_count = await cookies.count()       # 已生成的cookie数量
    blocklist_count = await blocklist.count()   # 黑名单中账号数量
    data = {
        "title": f"{website} cookies pool",
        "accounts_count": accounts_count,
        "cookies_count": cookies_count,
        "blocklist_count": blocklist_count
    }
    return web.json_response(data)


@routes.get('/{website}/random')
async def random(request):
    """
    获取随机的Cookie, 访问地址如 /weibo/random
    :return: 随机Cookie
    """
    website = request.match_info['website']
    g = get_conn('cookies', website)
    cookies = await g.random()
    return web.json_response(json.loads(cookies))


@routes.get('/{website}/add/{username}/{password}')
async def add(request):
    """
    添加账号, 访问地址如 /weibo/add/user/password
    :return:
    """
    website = request.match_info['website']
    username = request.match_info['username']
    password = request.match_info['password']
    g = get_conn('accounts', website)
    logger.info(username, password)
    await g.set(username, password)
    return web.json_response({'status': '1'})


@routes.get('/{website}/count')
async def count(request):
    """
    获取Cookies总数
    """
    website = request.match_info['website']
    g = get_conn('cookies', website)
    c = await g.count()
    return web.json_response({'status': '1', 'count': c})


if __name__ == '__main__':
    app = web.Application()
    logging.basicConfig(level=logging.DEBUG)
    app.add_routes(routes)
    web.run_app(app, port=API_PORT)




