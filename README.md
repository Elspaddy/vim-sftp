# VIM-SFTP Plugin

This is a simple plugin to download/upload files via SFTP using vim.

## How to set up

- In the local directory that you wish to keep synced with the remote directory:
	- Create a file `config.json` inside the folder `.vim-sftp`.
	- Write you `config.json` like the following example:
	```
		{
			"user": "foo",
			"host": "sftp.foo.com",
			"port": 2222,
			"key_path": "./unit_tests/data/key",
			"remote_folder": "/home/BarFoo/path/to/folder",
			"local_folder": "/home/FooBar/folder",
			"ignore": [
				"/build",
				".swp$",
				".swo$",
				".git",
				".o$",
				".pyc$"
			]
		}
	```

## How to use
- Open vim in the the root directory of your local folder.

The commands are:
	- `GetAllFilesFromRemote`

	- `SendAllFilesToRemote`

	- `SendCurrentFileToRemote`

	- `SendAllOpenBuffersToRemote`

## Warning
This project uses `AsyncRun` plugin in vim and `python3.7` with the `pysftp` package.

## Contributing
Feel free to create a pull request to add features or fix bugs.

### Suggestions:
	- Create SFTPProvider from `user` and `password`. So far, you can create it from a `user` and a `ssh_key`.
	- Add more tests
	- Improve README.md
