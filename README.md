<p align="center">
  <img src="./assets/giti.png" alt="giti logo" width="350"/>
</p>

# giti - Natural Language Git Commands
Convert natural language into executable Git commands using **Qwen2.5-Coder** - a powerful local LLM.

## Quick Start

```bash
# Install
git clone https://github.com/Sumit189/giti && cd giti
pip3 install llama-cpp-python && chmod +x main.py giti
echo "export PATH=\"$(pwd):\$PATH\"" >> ~/.zshrc && source ~/.zshrc

# Download model (1GB)
cd models
wget https://huggingface.co/bartowski/Qwen2.5-Coder-1.5B-Instruct-GGUF/resolve/main/Qwen2.5-Coder-1.5B-Instruct-Q4_K_M.gguf

# Test (open new terminal first)
giti "check status" --dry-run
```

## Installation

### Option 1: Homebrew (Recommended - macOS/Linux)

The easiest way to install giti with automatic model download:

```bash
# Add the tap
brew tap sumit189/giti

# Install giti (includes automatic model download)
brew install giti

# Test the installation
giti "check status" --dry-run
```

### Option 2: Manual Installation

**Clone and setup:**
```bash
git clone https://github.com/Sumit189/giti
cd giti
pip3 install llama-cpp-python
chmod +x main.py giti
```

> **Important**: Run the PATH commands while in the giti directory since `$(pwd)` will capture the current working directory.
> 
> **Benefit**: This approach works regardless of where you clone giti (Desktop, Documents, Projects folder, etc.)

**Add to PATH (choose your shell):**

For **zsh** (most macOS users):
```bash
echo "export PATH=\"$(pwd):\$PATH\"" >> ~/.zshrc
source ~/.zshrc
```

For **bash**:
```bash
echo "export PATH=\"$(pwd):\$PATH\"" >> ~/.bashrc
source ~/.bashrc
```

> **Why double quotes?** Using `echo "export PATH=\"$(pwd):\$PATH\""` expands `$(pwd)` immediately to the absolute path, while `\$PATH` becomes `$PATH` in the config file. This ensures the path resolves correctly when your shell starts.

> **Alternative**: If you prefer, you can use the absolute path: `echo 'export PATH="/full/path/to/giti:$PATH"'`

**Download the model:**
```bash
mkdir -p models
cd models
wget https://huggingface.co/bartowski/Qwen2.5-Coder-1.5B-Instruct-GGUF/resolve/main/Qwen2.5-Coder-1.5B-Instruct-Q4_K_M.gguf
cd ..
```

**Verify installation:**
```bash
# Test from any directory
cd /tmp
giti "check status" --dry-run
```

You should see the model load and a command like `git status` generated.

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

**"Command not found: giti":**
- Open a **new terminal** (important for PATH changes to take effect)
- Verify PATH includes giti: `echo $PATH | grep giti`
- If not found, re-run the PATH export command for your shell

**PATH not resolving correctly:**
- Check what was written to your config: `tail -3 ~/.zshrc` (or `~/.bashrc`)
- If you see `export PATH="$(pwd):$PATH"` (literal), the command used single quotes
- Fix with double quotes: `echo "export PATH=\"$(pwd):\$PATH\"" >> ~/.zshrc`
- This expands `$(pwd)` to the actual path immediately

**Model not found error:**
- Ensure the model file exists: `ls -la models/Qwen2.5-Coder-1.5B-Instruct-Q4_K_M.gguf`
- If missing, re-download: 
  ```bash
  mkdir -p models && cd models
  wget https://huggingface.co/bartowski/Qwen2.5-Coder-1.5B-Instruct-GGUF/resolve/main/Qwen2.5-Coder-1.5B-Instruct-Q4_K_M.gguf
  ```

**Permission denied:**
- Run: `chmod +x main.py giti`

**Commands executing in wrong directory:**
- This should be fixed in the latest version
- Verify with: `giti "check status" --dry-run` (should show your current directory)

**Shell compatibility issues:**
- Use zsh on macOS: `chsh -s /bin/zsh`
- Or use bash: `chsh -s /bin/bash` and modify `~/.bashrc` instead of `~/.zshrc`

## Model Details

- **Model**: Qwen2.5-Coder-1.5B (Q4_K_M quantization)
- **Size**: ~1GB
- **Purpose**: Specifically designed for code generation
- **Context**: 1K tokens (optimized for speed)
- **Performance**: Fast inference with good accuracy

## Uninstall

```bash
# Remove from PATH (for zsh)
sed -i '' '/export PATH.*giti/d' ~/.zshrc && source ~/.zshrc

# Remove from PATH (for bash)  
sed -i '/export PATH.*giti/d' ~/.bashrc && source ~/.bashrc

# Remove files
# First, find where giti is installed:
which giti
# Then remove that directory (replace with actual path):
# rm -rf /actual/path/to/giti
```