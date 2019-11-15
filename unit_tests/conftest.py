import pytest

@pytest.fixture
def valid_config_file1():
    content = {
        "user": "foo",
        "host": "mock.host.com",
        "port": 2222,
        "key_path": "./unit_tests/configs/valid_key",
        "path": "./unit_tests/configs/successful_configs.json"
    }

    yield content

@pytest.fixture
def valid_config_file2():
    content = {
        "user": "bar",
        "host": "mock2.host.com",
        "port": 2222,
        "key_path": "./unit_tests/configs/valid_key",
        "path": "./unit_tests/configs/successful_configs2.json"
    }

    yield content
