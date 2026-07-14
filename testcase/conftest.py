import pytest


@pytest.fixture
def failed_token_setup():
    """模拟前置登录接口失败，无法获得后续请求所需的 token。"""
    raise RuntimeError("前置登录失败：未获取到 token")


@pytest.fixture
def failed_test_data_setup():
    """模拟前置造数失败，业务测试数据没有准备成功。"""
    raise RuntimeError("前置造数失败：用户数据创建失败")


@pytest.fixture
def failed_data_cleanup():
    """模拟用例执行完成后，测试数据清理失败。"""
    yield {"order_id": "ORDER-1001"}
    raise RuntimeError("后置清理失败：测试订单删除失败")


@pytest.fixture
def failed_connection_close():
    """模拟用例执行完成后，公共连接关闭失败。"""
    yield {"connection_status": "connected"}
    raise RuntimeError("后置处理失败：数据库连接关闭失败")
