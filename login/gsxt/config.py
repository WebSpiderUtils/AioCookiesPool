import os


PROXY_API = os.environ.get('PROXY_POOL_API')
GEETEST_API = os.environ.get('GEETEST_API')


if __name__ == '__main__':
    print(GEETEST_API)
