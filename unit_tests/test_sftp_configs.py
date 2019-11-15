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

def test_parsing_correct(valid_config_file1):
    sftp_config = SFTPConfig(valid_config_file1['path'])
    assert sftp_config

    assert sftp_config.user() == valid_config_file1['user']
    assert sftp_config.host() == valid_config_file1['host']
    assert sftp_config.port() == valid_config_file1['port']
    assert sftp_config.key_path() == valid_config_file1['key_path']

def test_eq_function(valid_config_file1):
    sftp_config1 = SFTPConfig(valid_config_file1['path'])
    sftp_config2 = SFTPConfig(valid_config_file1['path'])

    assert sftp_config1 == sftp_config2

def test_not_eq_function(valid_config_file1, valid_config_file2):
    sftp_config1 = SFTPConfig(valid_config_file1['path'])
    sftp_config2 = SFTPConfig(valid_config_file2['path'])

    assert not sftp_config1 == sftp_config2
