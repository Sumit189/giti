"""
Parser - Prompt generation and RAG logic for Git commands
"""

import re
import os
from typing import List, Optional, Dict


class PromptParser:
    """Handles prompt generation and command parsing"""
    
    def __init__(self):
        self.base_examples = [
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

            # TIME-BASED OPERATIONS
            {"user": "go back to commit that was done 6 hours back", "bot": "git reset --hard HEAD@{6.hours.ago}"},
            {"user": "go back 6 hours", "bot": "git reset --hard HEAD@{6.hours.ago}"},
            {"user": "reset to 3 hours ago", "bot": "git reset --hard HEAD@{3.hours.ago}"},
            {"user": "checkout to 2 hours ago", "bot": "git checkout HEAD@{2.hours.ago}"},
            {"user": "find commits from last 2 days", "bot": "git log --since=\"2 days ago\" --oneline"},
            {"user": "reset to state from 3 hours ago", "bot": "git reset --hard HEAD@{3.hours.ago}"},
            {"user": "show changes from yesterday", "bot": "git log --since=\"yesterday\" --oneline"},
            {"user": "go back to commit made this morning", "bot": "git log --since=\"today 00:00\" --oneline"},
            {"user": "reset to last week", "bot": "git reset --hard HEAD@{1.week.ago}"},
            {"user": "go back to yesterday", "bot": "git reset --hard HEAD@{1.day.ago}"},
            {"user": "show commits from 4 hours ago", "bot": "git log --since=\"4 hours ago\" --oneline"},
            
            # COMMIT COUNT OPERATIONS (different from time)
            {"user": "go back 6 commits", "bot": "git reset --hard HEAD~6"},
            {"user": "go back 3 commits", "bot": "git reset --hard HEAD~3"},
            {"user": "checkout 5 commits back", "bot": "git checkout HEAD~5"},

            # HISTORY NAVIGATION
            {"user": "go back 5 commits", "bot": "git reset --hard HEAD~5"},
            {"user": "go back 3 commits but keep changes", "bot": "git reset --soft HEAD~3"},
            {"user": "undo last commit but keep changes", "bot": "git reset --soft HEAD~1"},
            {"user": "undo last commit and discard changes", "bot": "git reset --hard HEAD~1"},
            {"user": "undo last 2 commits but keep files", "bot": "git reset --soft HEAD~2"},

            # INTERACTIVE REBASE & SQUASHING
            {"user": "squash last 3 commits into one", "bot": "git rebase -i HEAD~3"},
            {"user": "interactive rebase last 5 commits", "bot": "git rebase -i HEAD~5"},
            {"user": "edit last commit", "bot": "git rebase -i HEAD~1"},

            # COMMITS WITH STAGING
            {"user": "commit all changes with message fix bugs", "bot": "git add .\ngit commit -m \"fix bugs\""},
            {"user": "stage and commit with message added feature", "bot": "git add .\ngit commit -m \"added feature\""},

            # FORCE OPERATIONS (with safety)
            {"user": "force push safely", "bot": "git push --force-with-lease"},
            {"user": "force push to origin main", "bot": "git push --force-with-lease origin main"},

            # MERGING & REBASING
            {"user": "merge dev into current branch", "bot": "git merge dev"},
            {"user": "rebase current branch onto main", "bot": "git rebase main"},
            {"user": "abort merge", "bot": "git merge --abort"},
            {"user": "abort rebase", "bot": "git rebase --abort"},

            # LOGS & HISTORY
            {"user": "show commit history", "bot": "git log --oneline"},
            {"user": "show last 10 commits", "bot": "git log -10 --oneline"},
            {"user": "show commits by author", "bot": "git log --author=\"<author>\" --oneline"},
            {"user": "search commits by message", "bot": "git log --grep=\"<search>\" --oneline"},

            # STASH
            {"user": "stash changes", "bot": "git stash"},
            {"user": "apply last stash", "bot": "git stash pop"},
            {"user": "list all stashes", "bot": "git stash list"},

            # REMOTE OPERATIONS
            {"user": "fetch latest changes", "bot": "git fetch"},
            {"user": "sync with remote", "bot": "git fetch origin\ngit reset --hard origin/main"},
        ]

    def load_context_file(self, file_path: str) -> List[Dict[str, str]]:
        """Load examples from a context file"""
        if not os.path.exists(file_path):
            return []
        
        examples = []
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Parse USER: ... BOT: ... format
        lines = content.split('\n')
        current_user = None
        current_bot = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('USER:'):
                current_user = line[5:].strip()
            elif line.startswith('BOT:'):
                current_bot = line[4:].strip()
                if current_user and current_bot:
                    examples.append({"user": current_user, "bot": current_bot})
                    current_user = None
                    current_bot = None
                    
        return examples

    def generate_prompt(self, user_query: str, context_data: Optional[List[Dict]] = None) -> str:
        """
        Generate a clean prompt for the LLM optimized for Qwen2.5-Coder
        
        Args:
            user_query: User's natural language query
            context_data: Optional additional examples from context file
            
        Returns:
            Formatted prompt string
        """
        # Combine base examples with context examples
        all_examples = self.base_examples.copy()
        if context_data:
            all_examples.extend(context_data)
        
        # Critical examples that should always be included (at the end for higher weight)
        critical_examples = [
            # CRITICAL: Time vs Commit Distinction
            {"user": "go back 6 commits", "bot": "git reset --hard HEAD~6"},
            {"user": "go back 3 commits", "bot": "git reset --hard HEAD~3"},
            {"user": "go back 6 hours", "bot": "git reset --hard HEAD@{6.hours.ago}"},
            {"user": "go back 3 hours", "bot": "git reset --hard HEAD@{3.hours.ago}"},
            {"user": "reset to 2 hours ago", "bot": "git reset --hard HEAD@{2.hours.ago}"},
            {"user": "checkout to 4 hours ago", "bot": "git checkout HEAD@{4.hours.ago}"},
            {"user": "go back to yesterday", "bot": "git reset --hard HEAD@{1.day.ago}"},
            {"user": "show commits from 5 hours ago", "bot": "git log --since=\"5 hours ago\" --oneline"},
        ]
        
        # Use a clean, focused prompt with explicit instructions
        prompt_parts = [
            "You are a Git command expert. Convert natural language descriptions into valid Git commands.",
            "",
            "CRITICAL RULES:",
            "- For TIME periods (hours, days): Use HEAD@{N.hours.ago} or --since syntax",
            "- For COMMIT counts: Use HEAD~N syntax", 
            "- 'go back 6 hours' = HEAD@{6.hours.ago} (TIME)",
            "- 'go back 6 commits' = HEAD~6 (COMMITS)",
            "",
            "Examples:",
        ]
        
        # Add regular examples first
        for example in all_examples[-10:]:  # Use last 10 examples
            prompt_parts.append(f"Human: {example['user']}")
            prompt_parts.append(f"Assistant: {example['bot']}")
            prompt_parts.append("")
        
        # Add critical examples at the end (highest weight)
        for example in critical_examples:
            prompt_parts.append(f"Human: {example['user']}")
            prompt_parts.append(f"Assistant: {example['bot']}")
            prompt_parts.append("")
        
        # Add the current query
        prompt_parts.append(f"Human: {user_query}")
        prompt_parts.append("Assistant:")
        
        return "\n".join(prompt_parts)

    def parse_commands(self, llm_output: str) -> List[str]:
        """
        Parse LLM output into git commands (minimal processing for better model)
        
        Args:
            llm_output: Raw output from the LLM
            
        Returns:
            List of git commands
        """
        if not llm_output.strip():
            return ["git status"]
        
        # Split by newlines and clean up
        commands = []
        for line in llm_output.strip().split('\n'):
            line = line.strip()
            if line and line.startswith('git'):
                commands.append(line)
        
        return commands if commands else ["git status"] 