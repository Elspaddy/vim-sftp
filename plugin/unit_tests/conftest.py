import pytest
import json
import os
from vim_sftp_sl import Node
from vim_sftp_sl import Config

@pytest.fixture
def config_file():
    data = {
            "user": "foo",
            "host": "sftp.foo.com",
            "port": 2222,
            "key_path": "./unit_tests/data/key",
            "remote_folder": "/home/bar",
            "local_folder": "/home/foo",
            "ignore": [
                    "/build",
                    ".swp$",
                    ".git",
                    ".swo$",
                    ".o$",
                    ".d$",
                    ".pyc$",
                    ".lcldev",
                    ".vscode",
                    ".cscope.out$",
                    ".vim"
            ]
    }

    workspace = os.getcwd()
    file_path = f"{workspace}/.unit_test_data"
    json_str = json.dumps(data)

    with open(file_path, 'w') as data_file:
        data_file.write(json_str)
        data_file.close()

        data['path'] = file_path

    yield data

    os.remove(file_path)

class MockedSFTPProvider:
    def __init__(self, config, local_tree, remote_tree):
        self._config = config
        self._local_tree = local_tree
        self._remote_tree = remote_tree

    def get_local_node(self, path):
        steps = path.split('/')[1:]
        current = self._local_tree

        for step in steps:
            current = current[step]

        root, name = Node.split_path(path)
        return Node(root, name, current['modified_date'], current['is_dir'], True)

    def get_remote_node(self, path):
        steps = path.split('/')[1:]
        current = self._remote_tree

        for step in steps:
            current = current[step]

        root, name = Node.split_path(path)
        return Node(root, name, current['modified_date'], current['is_dir'], False)

@pytest.fixture
def mocked_sftp_provider(config_file):
    config = Config(config_file["path"])

    local_tree = {
        "home": {
            "foo": {
                "file1.txt": {
                    "name": "file1.txt",
                    "modified_date": 76855867,
                    "is_dir": False
                }, 
                "bar":
                {
                    "file2.txt": 
                    {
                        "name": "file2.txt",
                        "modified_date": 76855866,
                        "is_dir": False
                    }
                }
            }
        }
    }

    remote_tree = {
        "home": {
            "bar": {
                "file1.txt": {
                    "name": "file1.txt",
                    "modified_date": 76855867,
                    "is_dir": False
                    },
                "bar": {
                    "file2.txt": {
                        "name": "file2.txt",
                        "modified_date": 76855866,
                        "is_dir": False
                        }
                    }
                }
            }
        }

    yield MockedSFTPProvider(config, local_tree, remote_tree)
