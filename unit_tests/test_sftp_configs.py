import pytest

from src.sftp_config import SFTPConfig

@pytest.mark.parametrize(['config_file'], [
    ['./unit_tests/configs/successful_configs.json'],
    ['./unit_tests/configs/successful_configs2.json']
])
def test_successful_construction(config_file):
    sftp_config = SFTPConfig(config_file)
    assert sftp_config

@pytest.mark.parametrize(['config_file'], [
    ['./unit_tests/configs/failing_configs.json'],
    ['./unit_tests/configs/failing_configs_invalid_key.json']
])
def test_failing_construction(config_file):
    with pytest.raises(Exception):
        SFTPConfig(config_file)

def test_parsing_correct(valid_config_file):
    sftp_config = SFTPConfig(valid_config_file['path'])
    assert sftp_config

    assert sftp_config.user() == valid_config_file['user']
    assert sftp_config.host() == valid_config_file['host']
    assert sftp_config.port() == valid_config_file['port']
    assert sftp_config.key_path() == valid_config_file['key_path']
