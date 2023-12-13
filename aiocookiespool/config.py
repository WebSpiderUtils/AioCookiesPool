import os

# REDIS数据库配置
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_PASSWORD = None
REDIS_DB = 2

# 自定义项目日志存储位置，默认项目根目录
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'log/')

# API地址和端口
API_HOST = '0.0.0.0'
API_PORT = 5200

# 并发控制
# 生成器
GENERATOR_CONCURRENCE = 2
# 测试器
VALID_CONCURRENCE = 5
# 监视器，只是操作数据库，相比其他进程可以适当增大并发
MONITOR_CONCURRENCE = 10

# 程序开关
# 产生器开关，模拟登录添加Cookies
GENERATOR_PROCESS = True
# 验证器开关，循环检测数据库中Cookies是否可用，不可用删除
TESTER_PROCESS = True
# 黑名单检测器开关，循环检测黑名单中账号睡眠时间，到时间从黑名单剔除
MONITOR_PROCESS = True
# API接口服务
API_PROCESS = True

# 任务循环周期，单位秒
GENERATOR_CYCLE = 20
TESTER_CYCLE = 600
MONITOR_CYCLE = 600

# 产生器类，如扩展其他站点，请在此配置
GENERATOR_MAP = {
    # 'weibo': 'WeiboCookiesGenerator',
}
# 测试类，如扩展其他站点，请在此配置
TESTER_MAP = {
    # 'weibo': 'WeiboValidTester',
    # 'gsxt': 'GsxtValidTester',
}
# 黑名单检测类
MONITOR_MAP = {
    # 'gsxt': 'GsxtBlocklistMonitor'
}
# 为每个测试器配置测试URL
TEST_URL_MAP = {
    'weibo': 'https://m.weibo.cn/',
    'gsxt': 'https://shiming.gsxt.gov.cn/corp-query-entprise-info-loadUserInfo.html',
}



