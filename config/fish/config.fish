# =============================================================================
# FISH SHELL CONFIGURATION — CUSTOM ARCH LINUX DESKTOP
# =============================================================================

# Disable default greeting
set -g fish_greeting

# Environment Variables
set -gx EDITOR nano
set -gx VISUAL $EDITOR
set -gx PAGER less
set -gx BROWSER xdg-open

# User Binaries & Local Paths
fish_add_path ~/.local/bin
fish_add_path ~/.cargo/bin
fish_add_path ~/.config/tejas-os/bin

# Prompt & Status Display
function fish_greeting
    echo -e "\e[1;34m󰣇 Arch Linux\e[0m \e[2m|\e[0m \e[1;36mHyprland 0.55+\e[0m \e[2m|\e[0m \e[1;35mJune AI Active\e[0m"
    echo -e "\e[2mType 'june --help' for AI CLI or press Super+Space for launcher.\e[0m\n"
end

# Navigation Shortcuts
abbr -a .. 'cd ..'
abbr -a ... 'cd ../..'
abbr -a .... 'cd ../../..'

# File & Directory Operations (Safe Defaults)
alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'
alias ls='ls --color=auto'
alias ll='ls -lh --color=auto'
alias la='ls -lha --color=auto'

# Git Convenience Abbreviations
abbr -a g 'git'
abbr -a gst 'git status -sb'
abbr -a gco 'git checkout'
abbr -a gcm 'git commit -m'
abbr -a gaa 'git add -A'
abbr -a glog 'git log --oneline --graph --decorate'

# Desktop & June Shortcuts
abbr -a june 'python3 -m assistant.core.cli'
abbr -a hypr-reload 'hyprctl reload'
abbr -a quick-reload 'killall quickshell; quickshell &'

# Midnight Theme Syntax Highlighting Colors
set -g fish_color_normal f0f6fc
set -g fish_color_command 58a6ff
set -g fish_color_param 79c0ff
set -g fish_color_keyword bc8cff
set -g fish_color_quote 56d364
set -g fish_color_redirection d29922
set -g fish_color_end 8b949e
set -g fish_color_error f85149
set -g fish_color_gray 484f58
set -g fish_color_selection --background=21262d
set -g fish_color_search_match --background=30363d
set -g fish_color_operator 39c5cf
