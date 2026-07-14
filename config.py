from pathlib import Path


# 接口服务基础地址
BASE_URL = "http://wy.lemonban.com:7001/smarthome"

# 接口请求超时时间
REQUEST_TIMEOUT = 10

# 短信验证码测试手机号环境变量名称
SMS_TEST_PHONE_ENV = "SMS_TEST_PHONE"

# 测试数据目录
DATA_DIR = Path(__file__).resolve().parent / "data"
