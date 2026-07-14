import pytest


@pytest.mark.parametrize("case_name, expect, result",
                         [("1","2","3"),
                          ("4","5","6")],
                         ids=[
        "登录接口-正确账号密码-期望登录成功",
        "登录接口-手机号为空-期望返回参数错误"
    ]
                         )
def test_demo1(case_name,expect,result):
    decode = "111"
    assert decode==result

