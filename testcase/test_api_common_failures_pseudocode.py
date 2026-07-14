import json

import pytest


# 以下用例只使用模拟数据，用于复现接口自动化中的常见失败，不发送真实请求。


def test_code_key_error_when_response_field_missing():
    """模拟代码直接读取响应中不存在的字段。"""
    response_data = {"message": "success"}

    user_id = response_data["user_id"]
    assert user_id is not None


def test_code_type_error_when_amount_type_is_invalid():
    """模拟金额字段类型错误导致计算失败。"""
    response_data = {"amount": "100"}

    total_amount = response_data["amount"] + 20
    assert total_amount == 120


def test_code_attribute_error_when_response_object_is_invalid():
    """模拟错误地把字典当作 requests 响应对象使用。"""
    response = {"status_code": 200}

    response.raise_for_status()


def test_code_json_decode_error_when_response_is_not_json():
    """模拟接口返回 HTML，代码却按 JSON 解析。"""
    response_text = "<html>服务异常</html>"

    response_data = json.loads(response_text)
    assert response_data


def test_assert_status_code_mismatch():
    """模拟接口实际状态码与用例预期不一致。"""
    expected_status_code = 200
    actual_status_code = 500

    assert actual_status_code == expected_status_code


def test_assert_required_field_is_missing():
    """模拟响应缺少业务要求的必填字段。"""
    response_data = {"message": "success"}

    assert "user_id" in response_data


def test_assert_response_field_type_mismatch():
    """模拟响应字段类型不符合接口契约。"""
    response_data = {"user_id": "1001"}

    assert isinstance(response_data["user_id"], int)


def test_assert_response_list_count_mismatch():
    """模拟列表接口返回数量不符合用例预期。"""
    expected_count = 3
    response_data = {"items": [{"id": 1}, {"id": 2}]}

    assert len(response_data["items"]) == expected_count


def test_business_balance_should_not_be_negative():
    """模拟支付后余额违反不得小于零的业务规则。"""
    response_data = {"balance": -20}

    assert response_data["balance"] >= 0, "支付后账户余额不能小于零"


def test_business_inventory_should_not_be_oversold():
    """模拟下单数量超过库存但接口仍返回成功。"""
    request_data = {"quantity": 5}
    inventory = 2
    response_data = {"code": 0, "message": "下单成功"}

    assert not (
        request_data["quantity"] > inventory and response_data["code"] == 0
    ), "库存不足时不允许下单成功"


def test_business_cancelled_order_should_not_be_paid():
    """模拟已取消订单仍然可以支付。"""
    order_status = "cancelled"
    response_data = {"payment_status": "success"}

    assert not (
        order_status == "cancelled" and response_data["payment_status"] == "success"
    ), "已取消订单不允许支付成功"


def test_business_duplicate_request_should_be_rejected():
    """模拟相同幂等键重复提交时生成了两条订单。"""
    idempotency_key = "PAY-20260714-001"
    created_orders = [
        {"order_id": "ORDER-1", "idempotency_key": idempotency_key},
        {"order_id": "ORDER-2", "idempotency_key": idempotency_key},
    ]

    assert len(created_orders) == 1, "相同幂等键只能创建一条订单"


def test_setup_token_acquisition_failed(failed_token_setup):
    """模拟依赖 token 的用例在登录前置阶段失败。"""
    assert failed_token_setup["token"]


def test_setup_test_data_creation_failed(failed_test_data_setup):
    """模拟业务用例在测试数据准备阶段失败。"""
    assert failed_test_data_setup["user_id"]


def test_teardown_test_data_cleanup_failed(failed_data_cleanup):
    """模拟主测试步骤通过，但测试数据后置清理失败。"""
    assert failed_data_cleanup["order_id"] == "ORDER-1001"


def test_teardown_connection_close_failed(failed_connection_close):
    """模拟主测试步骤通过，但公共连接关闭失败。"""
    assert failed_connection_close["connection_status"] == "connected"


def test_environment_invalid_base_url_causes_connection_error():
    """模拟 base_url 配置错误，导致接口连接失败。"""
    base_url = "http://127.0.0.1:9999"

    raise ConnectionError(f"无法连接接口服务：{base_url}")


def test_environment_invalid_name_causes_request_timeout():
    """模拟环境名称配置错误，请求被路由到不可用服务并超时。"""
    environment_name = "unknown"
    timeout = 5

    raise TimeoutError(
        f"环境 {environment_name} 的接口请求超过 {timeout} 秒仍未响应"
    )
