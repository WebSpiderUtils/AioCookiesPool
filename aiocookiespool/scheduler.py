import asyncio
import logging
import aiomultiprocess
from aiocookiespool.config import *
from multiprocessing import Process
from aiocookiespool.tester import *
from aiocookiespool.monitor import *
from aiocookiespool.generator import *
from aiocookiespool.api import web, routes


class Scheduler(object):
    @staticmethod
    async def executor(maps: dict) -> NoReturn:
        tasks = []
        for website, cls in maps.items():
            task = eval(cls + '(website="' + website + '")')
            tasks.append(task.run())
        await gather(*tasks)

    async def generator(self, cycle: int = GENERATOR_CYCLE) -> NoReturn:
        while True:
            logger.info('Cookies生成进程开始运行')
            try:
                await self.executor(GENERATOR_MAP)
                await asyncio.sleep(cycle)
            except Exception as e:
                logger.exception(e.args)

    async def tester(self, cycle: int = TESTER_CYCLE) -> NoReturn:
        while True:
            logger.info('Cookies检测进程开始运行')
            try:
                await self.executor(TESTER_MAP)
                await asyncio.sleep(cycle)
            except Exception as e:
                logger.exception(e.args)

    async def monitor(self, cycle: int = MONITOR_CYCLE) -> NoReturn:
        while True:
            logger.info('黑名单检测程序开始运行')
            try:
                await self.executor(MONITOR_MAP)
                await asyncio.sleep(cycle)
            except Exception as e:
                logger.exception(e.args)

    @staticmethod
    def api():
        logger.info('API接口开始运行')
        app = web.Application()
        logging.basicConfig(level=logging.DEBUG)
        app.add_routes(routes)
        web.run_app(app, port=API_PORT)

    async def run(self):
        if API_PROCESS:
            api_process = Process(target=Scheduler.api)
            api_process.start()
        async with aiomultiprocess.Pool() as pool:
            tasks = []
            if GENERATOR_PROCESS:
                tasks.append(pool.apply(Scheduler.generator, (self, )))
            if TESTER_PROCESS:
                tasks.append(pool.apply(Scheduler.tester, (self, )))
            if MONITOR_PROCESS:
                tasks.append(pool.apply(Scheduler.monitor, (self, )))
            await gather(*tasks)


if __name__ == '__main__':
    s = Scheduler()
    asyncio.run(s.run())

