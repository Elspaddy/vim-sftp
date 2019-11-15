class SFTPConnection:
    def __init__(sftp_config):
        self._sftp_config = sftp_config

    #Yields a SFTPFunctions object
    def connect(self):
        yield None

    def execute(self, batch_path):
        pass
