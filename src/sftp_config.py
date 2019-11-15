import json
import os

class SFTPConfig:
    def __init__(self, filename):
        self._user = None
        self._host = None
        self._port = None
        self._key_path = None

        self.load_config(filename)

    def user(self):
        return self._user

    def host(self):
        return self._host

    def port(self):
        return self._port

    def key_path(self):
        return self._key_path


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
            required_fields = ['user', 'host', 'port', 'key_path']
            missing_fields = [field for field in required_fields if field not in config]

            if len(missing_fields) > 0:
                raise Exception(f"Attributes {missing_fields} are required.")

            self._user = config['user']
            self._host = config['host']
            self._port = config['port']
            self._key_path = config['key_path']

            if not os.path.isfile(self._key_path):
                raise Exception(f"key_path: '{self._key_path}' is NOT a file.")

    def __eq__(self, other):
        return self._user == other._user \
            and self._host == other._host \
            and self._port == other._port \
            and self._key_path == other._key_path
