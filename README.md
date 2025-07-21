<p align="center">
  <img src="./assets/giti.png" alt="giti logo" width="350"/>
</p>

# giti - Natural Language Git Commands
Convert natural language into executable Git commands using **Qwen2.5-Coder** - a powerful local LLM.

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
wget https://huggingface.co/bartowski/Qwen2.5-Coder-1.5B-Instruct-GGUF/resolve/main/Qwen2.5-Coder-1.5B-Instruct-Q4_K_M.gguf
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

# With context file for enhanced workflows
giti --context examples/simple_workflow.txt "start new feature auth-system"

# With context file
giti --context examples/git_guide.txt "undo last commit"
```

## Features

- **Qwen2.5-Coder**: Advanced code-focused model for accurate Git commands
- **Local LLM**: No internet required after setup (~1.0GB model)
- **Dry run mode**: Preview commands before execution
- **RAG support**: Use context files to improve responses
- **Interactive shell**: Multi-command sessions
- **Safety**: Confirmation prompts before dangerous operations

## Examples

| Input | Output |
|-------|--------|
| `giti "stage all files and commit"` | `git add .`<br>`git commit -m "..."` |
| `giti "squash last 3 commits"` | `git rebase -i HEAD~3` |
| `giti "create branch dev"` | `git checkout -b dev` |
| `giti "force push safely"` | `git push --force-with-lease origin main` |
| `giti "go back 6 hours"` | `git reset --hard HEAD@{6.hours.ago}` |
| `giti "go back 5 commits"` | `git reset --hard HEAD~5` |
| `giti "show commits from 3 hours ago"` | `git log --since="3 hours ago" --oneline` |

## Context Files (RAG Support)

Context files allow you to provide additional knowledge to enhance Git command generation. They use a simple Q&A format to teach the model about your specific workflows.

### Creating a Context File

Create a `.txt` file with Q&A pairs in this format:

**Example: `my_git_workflow.txt`**
```txt
USER: How to start new feature?
BOT: git checkout main && git pull && git checkout -b feature/<name>

USER: How to commit all changes?
BOT: git add . && git commit -m "message"

USER: How to force push safely?
BOT: git push --force-with-lease

USER: How to squash last 3 commits?
BOT: git rebase -i HEAD~3

USER: How to undo last commit?
BOT: git reset --soft HEAD~1

USER: How to stash work?
BOT: git stash push -m "work in progress"
```

### Using Context Files

**Single Command:**
```bash
# Use your context file
giti --context my_git_workflow.txt "start new feature auth-system"
# Output: git checkout main && git pull && git checkout -b feature/auth-system

# Test first with dry-run
giti --dry-run --context my_git_workflow.txt "force push safely"
# Output: git push --force-with-lease
```

**Interactive Shell:**
```bash
# Load context for entire session
giti --shell --context my_git_workflow.txt

# Example session:
giti> start new feature payment
giti> commit all changes  
giti> force push safely
giti> exit
```

### Tips

- Keep files short (8-10 examples work best)
- Match your queries to the exact wording in your context file
- Test with `--dry-run` first
- Use simple, direct commands rather than complex workflows

## Troubleshooting

**Model not found error:**
- Ensure you're in the giti directory when running installation
- Check that `models/qwen2.5-coder-3b-instruct-q4_k_m.gguf` exists
- Verify PATH includes the giti directory: `echo $PATH`

**Permission denied:**
- Run: `chmod +x main.py giti`

**Command not found:**
- Restart your terminal or run: `source ~/.zshrc`

## Model Details

- **Model**: Qwen2.5-Coder-1.5B (Q4_K_M quantization)
- **Size**: ~1GB
- **Purpose**: Specifically designed for code generation
- **Context**: 1K tokens (optimized for speed)
- **Performance**: Fast inference with good accuracy

## Uninstall

```bash
# Remove from PATH
sed -i '' '/giti/d' ~/.zshrc
source ~/.zshrc

# Remove files
rm -rf /path/to/giti
``` 
