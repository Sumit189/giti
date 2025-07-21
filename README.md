# giti - Natural Language Git Commands

Convert natural language into executable Git commands using a local LLM.

## Installation

### Quick Install

```bash
git clone <your-repo-url>
cd giti
./install_manual.sh
```

This will:
- Install Python dependencies (llama-cpp-python)
- Download the language model (~875MB)
- Create a global `giti` command

### Manual Install

```bash
# Install dependency
pip3 install llama-cpp-python

# Download model
cd models
wget https://huggingface.co/TKDKid1000/phi-1_5-GGUF/resolve/main/phi-1_5-Q4_K_M.gguf
cd ..

# Use directly
python3 main.py "your command"
```

### Global Command (Optional)

To use `giti` from anywhere:

```bash
echo '#!/bin/bash' > /tmp/giti
echo "cd $(pwd)" >> /tmp/giti
echo 'python3 main.py "$@"' >> /tmp/giti
chmod +x /tmp/giti
sudo mv /tmp/giti /usr/local/bin/giti
```

## Usage

```bash
# Basic usage
giti "commit all changes with message fix bugs"
giti "create new branch feature-auth"
giti "push to main branch"

# Options
giti --dry-run "reset last commit"          # Preview only
giti --shell                                # Interactive mode
giti --context examples/git_guide.txt "cmd" # Use custom examples
giti --no-confirm "show status"             # Skip confirmation
```

## Examples

| Input | Output |
|-------|--------|
| "commit all changes" | `git add .`<br>`git commit -m "changes"` |
| "create branch fix-bug" | `git checkout -b fix-bug` |
| "undo last commit" | `git reset --soft HEAD~1` |
| "show status" | `git status` |

## Custom Context

Create files in `USER: question` / `BOT: command` format:

```txt
USER: How do I stash changes?
BOT: git stash

USER: How do I apply stash?
BOT: git stash pop
```

Use with: `giti --context myfile.txt "stash my changes"`

## Uninstall

```bash
sudo rm /usr/local/bin/giti              # Remove command
pip3 uninstall llama-cpp-python          # Remove dependency  
rm models/phi-1_5-Q4_K_M.gguf           # Remove model
```

## Requirements

- Python 3.8+
- 1GB disk space
- Internet connection (for initial model download) 