from vim_sftp_sl import Node

def test_create_node(mocked_sftp_provider):
    local_file1 = mocked_sftp_provider.get_local_node("/home/foo/file1.txt")
    assert local_file1

    remote_file1 = mocked_sftp_provider.get_remote_node("/home/bar/file1.txt")
    assert remote_file1

    assert local_file1._name == "file1.txt"
    assert local_file1._path == "/home/foo"

    assert remote_file1._name == "file1.txt"
    assert remote_file1._path == "/home/bar"

def test_convert_node_local_to_remote(mocked_sftp_provider):
    local_file1 = mocked_sftp_provider.get_local_node("/home/foo/file1.txt")
    assert local_file1

    remote_file1 = local_file1.to_remote(mocked_sftp_provider)

    assert local_file1._name == remote_file1._name

    assert remote_file1._path == "/home/bar"

def test_convert_node_remote_to_local(mocked_sftp_provider):
    remote_file1 = mocked_sftp_provider.get_remote_node("/home/bar/file1.txt")
    assert remote_file1

    local_file1 = remote_file1.to_local(mocked_sftp_provider)

    assert local_file1._name == remote_file1._name

    assert local_file1._path == "/home/foo"
