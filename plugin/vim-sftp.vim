let s:vim_sftp_plugin_root_dir = fnamemodify(resolve(expand('<sfile>:p')), ':h')
let s:vim_sftp_plugin_python_exec = s:vim_sftp_plugin_root_dir . '/' . 'vim-sftp.py'

function! GetVimSFTPCommandLine()
	let s:current_dir = fnamemodify(resolve(expand('<sfile>:p')), ':h')
	return ':AsyncRun python3.7 ' . s:vim_sftp_plugin_python_exec . ' ' . s:current_dir . '/.vim-sftp/config.json '
endfunction

function! GetAllFilesFromRemote()
	let command_line = GetVimSFTPCommandLine()
	execute command_line . 'get_all_files_from_remote'
endfunction

function! SendAllFilesToRemote()
	let command_line = GetVimSFTPCommandLine()
	execute command_line . 'send_all_files_to_remote'
endfunction

function! SendCurrentFileToRemote()
	let command_line = GetVimSFTPCommandLine()
	execute command_line . 'send_single_file_to_remote ' . expand('%h:p')
endfunction

function! SendAllOpenBuffersToRemote()
	let current_dir = fnamemodify(resolve(expand('<sfile>:p')), ':h')
	let buffers = getbufinfo()

	let items = ''

	for buffer in buffers
		if buffer.name =~ current_dir
			if buffer.name !~ "NERD_tree"
				let items = items . ' ' . buffer.name
			endif
		endif
	endfor

	echo items
	let command_line = GetVimSFTPCommandLine()
	execute command_line . 'send_multiple_files_to_remote ' . items
endfunction
