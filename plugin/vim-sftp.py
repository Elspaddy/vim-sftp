import sys
import json
import os
import re
import pysftp
from shutil import copyfile
import subprocess #TODO: Replace

class Config:
    def __init__(self, filename):
        self._user = None
        self._host = None
        self._port = None
        self._remote_folder = None
        self._local_folder = None
        self._key_path = None
        self._ignore = []

        self.load_config(filename)

    def user(self):
        return self._user

    def host(self):
        return self._host

    def port(self):
        return self._port

    def key_path(self):
        return self._key_path

    def remote_folder(self):
        return self._remote_folder

    def local_folder(self):
        return self._local_folder

    def ignore(self):
        return self._ignore

    def load_config(self, filename):
        if not os.path.isfile(filename):
            raise Exception(f"Provided filename: '{filename}' is not a file.")

        content = open(filename, 'r').read()

        config = None

        try:
            config = json.loads(content)
        except:
            raise Exception(f"Content of '{filename}' is not a valid json file.")

        if config is not None:
            required_fields = ['user', 'host', 'port', 'key_path', 'remote_folder', 'local_folder']
            missing_fields = [field for field in required_fields if field not in config]

            if len(missing_fields) > 0:
                raise Exception(f"Attributes {missing_fields} are required.")

            self._user = config['user']
            self._host = config['host']
            self._port = config['port']
            self._key_path = config['key_path']
            self._remote_folder = config['remote_folder']
            self._local_folder = config['local_folder']

            self._ignore = config.get('ignore', [])

            if not os.path.isfile(self._key_path):
                raise Exception(f"key_path: '{self._key_path}' is NOT a file.")

    def __eq__(self, other):
        return self._user == other._user \
            and self._host == other._host \
            and self._port == other._port \
            and self._key_path == other._key_path \
            and self._remote_folder == other._remote_folder \
            and self._local_folder == other._local_folder

class SSHKeyHelper:
    def __init__(self, sftp_config):
        self._sftp_config = sftp_config
        self._path = None

        if not self._sftp_config:
            raise Exception(f"Invalid sftp_config.")

    def path(self):
        return self._path

    def __enter__(self):
        workspace = os.getcwd()

        self._path = f"{workspace}/ssh_key"

        copyfile(self._sftp_config.key_path(), self._path)

        subprocess.call(['chmod', '400', self._path])

        return self._path

    def __exit__(self, exc_type, exc_eval, exc_tb):
        os.remove(self._path)

class Node:
    def __init__(self, path, name, modified_date, is_dir, is_local):
        self._path = path
        self._name = name
        self._modified_date = modified_date
        self._is_dir = is_dir
        self._is_local = is_local

    def full_path(self):
        return f"{self._path}/{self._name}"

    def to_local(self, sftp_provider):
        remote_folder = sftp_provider._config.remote_folder()
        local_folder = sftp_provider._config.local_folder()

        return sftp_provider.get_local_node(self.full_path().replace(remote_folder, local_folder))

    def to_remote(self, sftp_provider):
        remote_folder = sftp_provider._config.remote_folder()
        local_folder = sftp_provider._config.local_folder()

        return sftp_provider.get_remote_node(self.full_path().replace(local_folder, remote_folder))

    @classmethod
    def split_path(cls, path):
        items = path.split('/')
        return "/".join(items[:-1]), items[-1]

class SFTPProvider:
    def __init__(self, config):
        self._config = config

        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None

        with SSHKeyHelper(self._config) as ssh_key_path:
            self._sftp = pysftp.Connection(self._config.host(), 
                                            username=self._config.user(), 
                                            private_key=ssh_key_path, 
                                            port=self._config.port(), 
                                            cnopts=cnopts)

    def get_local_node(self, path):
        root, name = Node.split_path(path)

        try:
            modified_date = int(os.path.getmtime(path))
            return Node(root, name, modified_date, False, True)
        except: #If the files does NOT exist
            return Node(root, name, 0, False, True)


    def get_remote_node(self, path):
        root, name = Node.split_path(path)

        try:
            modified_date = self._sftp.lstat(path).st_mtime
            return Node(root, name, modified_date, False, False)
        except: #If the file does NOT exist
            return Node(root, name, 0, False, False)

    @classmethod
    def get_from_remote_callback(cls, sftp_provider, remote_file):
        def get_from_remote_callback_function(current, total):
            p = int((float(current)/total) * 100)
            print(f"{p}% of {remote_file._name} downloaded")
            sys.stdout.flush()

        return get_from_remote_callback_function

    def get_file_from_remote(self, remote_file):
        local_file = remote_file.to_local(self)

        if local_file._modified_date >= remote_file._modified_date:
            print(f"Up-to-date {local_file._name}")
            sys.stdout.flush()
            return

        os.makedirs(local_file._path, exist_ok=True)

        self._sftp.get(remote_file.full_path(), 
                        local_file.full_path(), 
                        SFTPProvider.get_from_remote_callback(self, remote_file), 
                        preserve_mtime=True)

    @classmethod
    def send_to_remote_callback(cls, sftp_provider, local_file):
        def send_to_remote_callback_function(current, total):
            p = int((float(current)/total) * 100)
            print(f"{p}% of {local_file._name} uploaded")
            sys.stdout.flush()

        return send_to_remote_callback_function

    def send_file_to_remote(self, local_file):
        remote_file = local_file.to_remote(self)

        if local_file._modified_date <= remote_file._modified_date:
            print(f"Up-to-date {remote_file._name}")
            sys.stdout.flush()
            return

        self._sftp.makedirs(remote_file._path)

        self._sftp.put(local_file.full_path(), 
                        remote_file.full_path(), 
                        SFTPProvider.send_to_remote_callback(self, local_file), 
                        preserve_mtime=True)

    @classmethod
    def should_ignore(cls, sftp_provider, path):
        for ig in sftp_provider._config.ignore():
            if len(re.findall(ig, path)) > 0:
                return True

        return False

    @classmethod
    def get_all_files_from_remote_callback(cls, sftp_provider, item_type):
        def get_all_files_from_remote_callback_function(path):
            if not SFTPProvider.should_ignore(sftp_provider, path):
                if item_type == 'file':
                    remote_file = sftp_provider.get_remote_node(path)
                    sftp_provider.get_file_from_remote(remote_file)

                if item_type == 'dir':
                    print(f"Scanning {path}")

                    sftp_provider._sftp.walktree(path, 
                            SFTPProvider.get_all_files_from_remote_callback(sftp_provider, 'file'),
                            SFTPProvider.get_all_files_from_remote_callback(sftp_provider, 'dir'),
                            SFTPProvider.get_all_files_from_remote_callback(sftp_provider, 'unknown'),
                            recurse=False)

        return get_all_files_from_remote_callback_function

    def get_all_files_from_remote(self, root):
        self._sftp.walktree(root.full_path(), 
                            SFTPProvider.get_all_files_from_remote_callback(self, 'file'),
                            SFTPProvider.get_all_files_from_remote_callback(self, 'dir'),
                            SFTPProvider.get_all_files_from_remote_callback(self, 'unknown'),
                            recurse=False)

    def send_all_files_to_remote(self, root):
        for root, dirs, files in os.walk(root.full_path()):
            for cur_file in files:
                file_path = f"{root}/{cur_file}"
                if not SFTPProvider.should_ignore(self, file_path):
                    local_file = sftp_provider.get_local_node(file_path)
                    sftp_provider.send_file_to_remote(local_file)

if __name__ == "__main__":
    config_path = sys.argv[1]
    operation = sys.argv[2]

    config = Config(config_path)
    sftp_provider = SFTPProvider(config)

    if operation == "get_all_files_from_remote":
        path = config.remote_folder()
        root, name = Node.split_path(path)
        node = Node(root, name, 0, True, False)

        sftp_provider.get_all_files_from_remote(node)

    if operation == "send_all_files_to_remote":
        path = config.local_folder()
        root, name = Node.split_path(path)
        node = Node(root, name, 0, True, False)

        sftp_provider.send_all_files_to_remote(node)

    if operation == "get_single_file_from_remote":
        path = sys.argv[3]
        local_file = sftp_provider.get_local_node(path)
        remote_file = local_file.to_remote()

        sftp_provider.get_file_from_remote(remote_file)

    if operation == "send_single_file_to_remote":
        path = sys.argv[3]
        local_file = sftp_provider.get_local_node(path)

        sftp_provider.send_file_to_remote(local_file)

    if operation == "get_multiple_files_from_remote":
        paths = sys.argv[3:]

        for path in paths:
            local_file = sftp_provider.get_local_node(path)
            remote_file = local_file.to_remote()

            sftp_provider.get_file_from_remote(remote_file)

    if operation == "send_multiple_files_to_remote":
        paths = sys.argv[3:]

        for path in paths:
            path = sys.argv[3]
            local_file = sftp_provider.get_local_node(path)

            sftp_provider.send_file_to_remote(local_file)
