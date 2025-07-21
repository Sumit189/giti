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
            {
                "user": "commit all changes with message fix bugs",
                "bot": "git add .\ngit commit -m \"fix bugs\""
            },
            {
                "user": "push to main branch",
                "bot": "git push origin main"
            },
            {
                "user": "create new branch feature-login",
                "bot": "git checkout -b feature-login"
            },
            {
                "user": "undo last commit but keep changes",
                "bot": "git reset --soft HEAD~1"
            },
            {
                "user": "show status of repository",
                "bot": "git status"
            },
            {
                "user": "pull latest changes from remote",
                "bot": "git pull"
            },
            {
                "user": "stash current changes",
                "bot": "git stash"
            },
            {
                "user": "switch to main branch",
                "bot": "git checkout main"
            }
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