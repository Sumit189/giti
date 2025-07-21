<p align="center">
  <img src="./assets/giti.png" alt="giti logo" width="350"/>
</p>

# giti - Natural Language Git Commands
Convert natural language into executable Git commands using a local LLM.

## Installation

```bash
git clone https://github.com/Sumit189/giti
cd giti
pip3 install llama-cpp-python
chmod +x main.py giti
echo 'export PATH="$(pwd):$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Download the model:**
```bash
cd models
wget https://huggingface.co/TKDKid1000/phi-1_5-GGUF/resolve/main/phi-1_5-Q4_K_M.gguf
```

## Usage

```bash
# Basic usage
giti "commit all changes with message fix bugs"
giti "push to main branch"
giti "create new branch feature-auth"

# Dry run (preview commands)
giti --dry-run "reset to last commit"

# Interactive shell
giti --shell

# With context file
giti --context examples/git_guide.txt "undo last commit"
```

## Features

- **Local LLM**: No internet required after setup
- **Dry run mode**: Preview commands before execution
- **RAG support**: Use context files to improve responses
- **Interactive shell**: Multi-command sessions
- **Safety**: Confirmation prompts before dangerous operations

## Examples

| Input | Output |
|-------|--------|
| `giti "stage all files"` | `git add .` |
| `giti "undo last commit"` | `git reset --soft HEAD~1` |
| `giti "create branch dev"` | `git checkout -b dev` |
| `giti "push force"` | `git push --force-with-lease` |

## Context Files

Create `.txt` files with Q&A format for better responses:

```txt
USER: How to revert a merge?
BOT: git revert -m 1 <commit-hash>

USER: How to squash commits?
BOT: git rebase -i HEAD~<number>
```

## Troubleshooting

**Model not found error:**
- Ensure you're in the giti directory when running installation
- Check that `models/phi-1_5-Q4_K_M.gguf` exists
- Verify PATH includes the giti directory: `echo $PATH`

**Permission denied:**
- Run: `chmod +x main.py giti`

**Command not found:**
- Restart your terminal or run: `source ~/.zshrc`

## Uninstall

```bash
# Remove from PATH
sed -i '' '/giti/d' ~/.zshrc
source ~/.zshrc

# Remove files
rm -rf /path/to/giti
``` 
