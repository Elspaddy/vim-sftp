import pytest
import os
from vim_sftp_sl import Config

workspace = os.getcwd()

@pytest.mark.parametrize(["file_path"], [
    [workspace + "/unit_tests/data/successful_config.json"],
    [workspace + "/unit_tests/data/successful_config2.json"]
])
def test_create_valid_file(file_path):
    config = Config(file_path)
    assert config
 
@pytest.mark.parametrize(["file_path"], [
    ["./unit_tests/data/foo.json"], #Non-existing file
    ["./unit_tests/data/incomplete_file.json"] #Incomplete file
])
def test_create_invalid_file(file_path):
    with pytest.raises(Exception):
        config = Config(file_path)

def test_right_reading(config_file):
    config = Config(config_file["path"])

    assert config.user() == config_file["user"]
    assert config.host() == config_file["host"]
    assert config.port() == config_file["port"]
    assert config.key_path() == config_file["key_path"]
    assert config.remote_folder() == config_file["remote_folder"]
    assert config.local_folder() == config_file["local_folder"]
    assert config.ignore() == config_file["ignore"]
