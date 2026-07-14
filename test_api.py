import pytest

@pytest.mark.parametrize("name,age", [
    ("Alice", 30),
    ("Bob", 25),
    ("Charlie", 35),
], ids=["测试", "young_bob", "senior_charlie"])
def test_user_age(name, age):
    assert age > 0