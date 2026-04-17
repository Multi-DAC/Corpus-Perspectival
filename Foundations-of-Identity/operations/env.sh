# Clawd environment — tool paths for the new body (Ryzen 9 / RTX 5080)
# Created 2026-03-31. Source this at session start or in commands.
# Usage: source /c/Users/mercu/clawd/operations/env.sh

# Core Windows paths
export PATH="/c/Windows/System32:/c/Windows:/c/Windows/System32/Wbem:$PATH"

# Python 3.14
export PATH="/c/Python314:/c/Python314/Scripts:$PATH"

# MiKTeX (LaTeX)
export PATH="/c/Program Files/MiKTeX/miktex/bin/x64:$PATH"

# Wolfram Engine 14.3
export PATH="/c/Program Files/Wolfram Research/Wolfram Engine/14.3:$PATH"
export PATH="/c/Program Files/Wolfram Research/WolframScript:$PATH"

# Aliases
alias python='/c/Python314/python.exe'
alias pip='/c/Python314/python.exe -m pip'
alias wsl='/c/Windows/System32/wsl.exe'

# WSL as clawd user (tools are installed under /home/clawd)
# Usage: wsl-clawd "sage --version"
#        wsl-clawd "python3 -c 'import torch; print(torch.cuda.is_available())'"
wsl-clawd() {
  /c/Windows/System32/wsl.exe -d Ubuntu -- sudo -u clawd bash -c "export HOME=/home/clawd; source /home/clawd/.bashrc 2>/dev/null; $1"
}

# Direct tool shortcuts via WSL
alias wsl-sage='/c/Windows/System32/wsl.exe -d Ubuntu -- sudo -u clawd bash -c "export HOME=/home/clawd; /home/clawd/miniconda3/bin/sage"'
alias wsl-python='/c/Windows/System32/wsl.exe -d Ubuntu -- sudo -u clawd bash -c "export HOME=/home/clawd; /home/clawd/miniconda3/bin/python3"'
