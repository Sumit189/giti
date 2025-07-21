"""
Parser - Prompt generation and RAG logic for Git commands
"""

import re
import os
from typing import List, Optional, Dict


class PromptParser:
    """Handles prompt generation and command parsing"""
    
    def __init__(self):
        self.base_examples = self.base_examples = [
            # Basic Workflow
            {"user": "check repository status", "bot": "git status"},
            {"user": "add all changes", "bot": "git add ."},
            {"user": "add specific file app.js", "bot": "git add app.js"},
            {"user": "commit changes with message update README", "bot": "git commit -m \"update README\""},
            {"user": "add and commit in one line with message fix", "bot": "git commit -am \"fix\""},
            {"user": "amend last commit message to better explanation", "bot": "git commit --amend -m \"better explanation\""},
            {"user": "push current branch", "bot": "git push"},
            {"user": "push to origin main", "bot": "git push origin main"},
            {"user": "pull latest changes", "bot": "git pull"},
            {"user": "pull with rebase", "bot": "git pull --rebase"},
            
            # Branching
            {"user": "create new branch dev-feature", "bot": "git checkout -b dev-feature"},
            {"user": "switch to dev branch", "bot": "git checkout dev"},
            {"user": "delete local branch dev", "bot": "git branch -d dev"},
            {"user": "delete remote branch dev", "bot": "git push origin --delete dev"},
            {"user": "list all branches", "bot": "git branch"},
            {"user": "list remote branches", "bot": "git branch -r"},
            {"user": "rename current branch to hotfix", "bot": "git branch -m hotfix"},
            {"user": "create branch and push to remote", "bot": "git checkout -b new-feature\ngit push -u origin new-feature"},

            # Merging & Rebasing
            {"user": "merge dev into current branch", "bot": "git merge dev"},
            {"user": "rebase current branch onto main", "bot": "git rebase main"},
            {"user": "abort merge", "bot": "git merge --abort"},
            {"user": "abort rebase", "bot": "git rebase --abort"},
            {"user": "continue rebase", "bot": "git rebase --continue"},
            {"user": "resolve conflicts and mark as resolved", "bot": "git add .\ngit rebase --continue"},

            # Reset & Revert
            {"user": "undo last commit but keep changes", "bot": "git reset --soft HEAD~1"},
            {"user": "undo last commit and discard changes", "bot": "git reset --hard HEAD~1"},
            {"user": "reset file to last commit", "bot": "git checkout -- <file>"},
            {"user": "revert last commit", "bot": "git revert HEAD"},
            {"user": "revert specific commit abc123", "bot": "git revert abc123"},

            # Stash
            {"user": "stash changes", "bot": "git stash"},
            {"user": "apply last stash", "bot": "git stash apply"},
            {"user": "pop and apply stash", "bot": "git stash pop"},
            {"user": "list all stashes", "bot": "git stash list"},
            {"user": "drop last stash", "bot": "git stash drop"},

            # Remote Repos
            {"user": "add remote origin", "bot": "git remote add origin <url>"},
            {"user": "view remotes", "bot": "git remote -v"},
            {"user": "remove remote upstream", "bot": "git remote remove upstream"},
            {"user": "set upstream for current branch", "bot": "git push --set-upstream origin <branch>"},

            # Tags
            {"user": "create tag v1.0", "bot": "git tag v1.0"},
            {"user": "push tags", "bot": "git push --tags"},
            {"user": "delete tag v1.0", "bot": "git tag -d v1.0"},
            {"user": "show all tags", "bot": "git tag"},

            # Logs & History
            {"user": "show commit history", "bot": "git log"},
            {"user": "show one line log", "bot": "git log --oneline"},
            {"user": "show file history", "bot": "git log <file>"},
            {"user": "show changes", "bot": "git diff"},
            {"user": "show staged changes", "bot": "git diff --cached"},
            {"user": "show commit details", "bot": "git show"},
            {"user": "view log with graph", "bot": "git log --oneline --graph --all"},

            # Blame & Inspect
            {"user": "blame a file", "bot": "git blame <file>"},
            {"user": "who modified this line", "bot": "git blame <file>"},
            {"user": "view specific commit abc123", "bot": "git show abc123"},

            # Init & Clone
            {"user": "initialize git repo", "bot": "git init"},
            {"user": "clone repo", "bot": "git clone <url>"},
            {"user": "clone with specific branch", "bot": "git clone -b <branch> <url>"},

            # Cherry Pick & Bisect
            {"user": "cherry-pick commit abc123", "bot": "git cherry-pick abc123"},
            {"user": "start bisect", "bot": "git bisect start"},
            {"user": "mark current commit as bad", "bot": "git bisect bad"},
            {"user": "mark current commit as good", "bot": "git bisect good"},
            {"user": "reset bisect", "bot": "git bisect reset"},

            # Configuration
            {"user": "set username", "bot": "git config --global user.name \"Your Name\""},
            {"user": "set email", "bot": "git config --global user.email \"you@example.com\""},
            {"user": "view config", "bot": "git config --list"},
            {"user": "create alias for checkout", "bot": "git config --global alias.co checkout"},

            # Clean & Maintenance
            {"user": "clean untracked files", "bot": "git clean -fd"},
            {"user": "remove all untracked files and directories", "bot": "git clean -fdx"},
            {"user": "prune deleted remote branches", "bot": "git remote prune origin"},
            {"user": "fetch latest changes", "bot": "git fetch"},
            {"user": "fetch and prune", "bot": "git fetch -p"}
        ]
    
    def load_context_file(self, file_path: str) -> List[Dict[str, str]]:
        """
        Load RAG context from a file
        
        Args:
            file_path: Path to the context file
            
        Returns:
            List of user/bot example pairs
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Context file not found: {file_path}")
        
        examples = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse USER/BOT format
        pattern = r'USER:\s*(.*?)\s*BOT:\s*(.*?)(?=USER:|$)'
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        
        for user_text, bot_text in matches:
            examples.append({
                "user": user_text.strip(),
                "bot": bot_text.strip()
            })
        
        print(f"📚 Loaded {len(examples)} examples from context file")
        return examples
    
    def generate_prompt(self, query: str, context_examples: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Generate a few-shot prompt for the LLM
        
        Args:
            query: User's natural language query
            context_examples: Additional examples from RAG context
            
        Returns:
            Complete prompt for the LLM
        """
        # Combine base examples with context examples
        all_examples = self.base_examples.copy()
        if context_examples:
            all_examples.extend(context_examples)
        
        # Building the prompt
        prompt_parts = [
            "You are a Git command assistant. Convert natural language to Git commands.",
            "Respond only with the Git command(s), nothing else.",
            "Use multiple commands on separate lines if needed.",
            "",
            "Examples:",
            ""
        ]
        
        # Add examples
        for example in all_examples[-10:]:  # Taking last 10 examples to fit context
            prompt_parts.append(f"USER: {example['user']}")
            prompt_parts.append(f"BOT: {example['bot']}")
            prompt_parts.append("")
        
        # Add the current query
        prompt_parts.append(f"USER: {query}")
        prompt_parts.append("BOT:")
        
        return "\n".join(prompt_parts)
    
    def extract_commands(self, response: str) -> List[str]:
        """
        Extract Git commands from the LLM response
        
        Args:
            response: Raw response from the LLM
            
        Returns:
            List of Git commands
        """
        # Response cleaning
        response = response.strip()
        
        # Split into lines
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        
        commands = []
        for line in lines:
            # Skip lines that don't look like git commands
            if self._is_git_command(line):
                commands.append(line)
        
        return commands
    
    def _is_git_command(self, line: str) -> bool:
        """
        Check if a line is a valid Git command
        
        Args:
            line: Line to check
            
        Returns:
            True if it's a Git command
        """
        # Remove common prefixes
        line = line.strip()
        if line.startswith('$'):
            line = line[1:].strip()
        if line.startswith('> '):
            line = line[2:].strip()
        
        # Check if it starts with git
        return line.startswith('git ') 