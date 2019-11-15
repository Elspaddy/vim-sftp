import pytest

@pytest.fixture
def valid_config_file():
    content = {
        "user": "foo",
        "host": "mock.host.com",
        "port": 2222,
        "key_path": "./unit_tests/configs/valid_key",
        "path": "./unit_tests/configs/successful_configs.json"
    }

    yield content
