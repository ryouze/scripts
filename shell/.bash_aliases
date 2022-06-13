# annoyances
alias cls='clear'
alias winhome='cd ~'
alias wincode='cd ~/Code'

# hack: turn "man xyz" into "xyz --help"
# this is because "man xyz" doesn't work with git bash on windows (for me, at least)
man() { $@ "--help"; }

# software
alias notepad++='/c/Program\ Files/Notepad++/notepad++.exe'
alias rlang='R.exe'
alias piplist='pip list | echo "Installed pip packages: $(wc -l)"'
alias pip-update='python ~/Software/Scripts/pip_updater.py'
alias yt-mp3='~/Software/yt-dlp/yt-dlp.exe --sponsorblock-remove all -x --audio-quality 192K --audio-format mp3 -o "~/Downloads/%(title)s.%(ext)s"'
alias yt-update='~/Software/yt-dlp/yt-dlp.exe -U'

# if in win32 dir, then move back to home
# windows terminal opens it by default but if you change it to $HOME then it will always open in home even if opened thru run panel in a custom directory
if [[ $PWD -ef "/c/Windows/system32" ]]; then
	# echo "Redirecting to home folder..."
	cd $HOME
fi
