"""
Executor - Command execution with confirmation and dry-run support
"""

import subprocess
from typing import List


class CommandExecutor:
    """Handles execution of Git commands with safety features"""
    
    def __init__(self, dry_run: bool = False, no_confirm: bool = False):
        """
        Initialize the command executor
        
        Args:
            dry_run: If True, only show commands without executing
            no_confirm: If True, skip confirmation prompts
        """
        self.dry_run = dry_run
        self.no_confirm = no_confirm
    
    def execute_commands(self, commands: List[str]) -> None:
        """
        Execute a list of Git commands
        
        Args:
            commands: List of Git commands to execute
        """
        if not commands:
            print("❌ No commands to execute")
            return
        
        # Display commands
        print("Generated commands:")
        for i, cmd in enumerate(commands, 1):
            print(f"  {i}. {cmd}")
        print()
        
        if self.dry_run:
            print("Dry run mode - commands not executed")
            return
        
        # Get confirmation unless --no-confirm is used
        if not self.no_confirm:
            if not self._get_confirmation():
                print("❌ Execution cancelled")
                return
        
        # Execute commands
        print("🚀 Executing commands...")
        for i, cmd in enumerate(commands, 1):
            print(f"\n[{i}/{len(commands)}] {cmd}")
            
            try:
                result = subprocess.run(
                    cmd.split(),
                    capture_output=True,
                    text=True,
                    cwd=".",
                    timeout=30  # 30 second timeout
                )
                
                if result.returncode == 0:
                    print("✅ Success")
                    if result.stdout.strip():
                        print(f"📤 Output:\n{result.stdout}")
                else:
                    print(f"❌ Error (exit code {result.returncode})")
                    if result.stderr.strip():
                        print(f"📥 Error output:\n{result.stderr}")
                        
                        # try alternatives
                        error_msg = result.stderr.lower()
                        retry_attempted = False
                        
                        if "pathspec" in error_msg and "did not match" in error_msg:
                            retry_attempted = self._try_branch_alternatives(cmd, i, len(commands))
                        
                        if not retry_attempted:
                            # Show suggestions if no auto-retry was possible
                            if "pathspec" in error_msg and "did not match" in error_msg:
                                print("\n💡 Suggestion: The reference doesn't exist (branch, file, or commit).")
                                print("Try these commands to check what's available:")
                                print("  git branch -a    # See all branches")
                                print("  git log --oneline # See recent commits")
                                print("  git status       # See current state")
                            elif "did not match any file" in error_msg:
                                print("\n💡 Suggestion: The reference doesn't exist.")
                                print("Check available options with: git branch -a")
                        
                        # Ask if user wants to continue with remaining commands (if no successful retry)
                        if not retry_attempted and i < len(commands) and not self.no_confirm:
                            if not self._get_continue_confirmation():
                                print("🛑 Execution stopped")
                                break
                    else:
                        # No stderr but still failed
                        if i < len(commands) and not self.no_confirm:
                            if not self._get_continue_confirmation():
                                print("🛑 Execution stopped")
                                break
                        
            except subprocess.TimeoutExpired:
                print("Command timed out after 30 seconds")
                if i < len(commands) and not self.no_confirm:
                    if not self._get_continue_confirmation():
                        print("🛑 Execution stopped")
                        break
                        
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                if i < len(commands) and not self.no_confirm:
                    if not self._get_continue_confirmation():
                        print("🛑 Execution stopped")
                        break
        
        print("\n✨ Command execution completed")
    
    def _try_branch_alternatives(self, original_cmd: str, cmd_index: int, total_commands: int) -> bool:
        """
        Try alternative commands when branch operations fail
        Returns True if a successful retry was made, False otherwise
        """
        cmd_lower = original_cmd.lower()
        
        if not ("checkout" in cmd_lower or "switch" in cmd_lower):
            return False
            
        # Extract branch name from checkout/switch commands
        parts = original_cmd.split()
        if len(parts) < 2:
            return False
            
        target_branch = parts[-1]  # Last argument is usually the branch
        
        # Get all available branches
        available_branches = self._get_available_branches()
        if not available_branches:
            return False
            
        print(f"\n🔍 Looking for alternatives to '{target_branch}'...")
        print(f"📋 Available branches: {', '.join(available_branches[:5])}{'...' if len(available_branches) > 5 else ''}")
        
        retry_commands = []
        
        # Strategy 1: Exact case-insensitive matches
        exact_matches = [b for b in available_branches if b.lower() == target_branch.lower() and b != target_branch]
        for exact_match in exact_matches[:1]:  # Only try the first exact match
            if "checkout" in cmd_lower:
                retry_commands.append(f"git checkout {exact_match}")
            elif "switch" in cmd_lower:
                retry_commands.append(f"git switch {exact_match}")
        
        # Strategy 2: Create the exact branch the user asked for
        if "checkout" in cmd_lower:
            retry_commands.append(f"git checkout -b {target_branch}")
        elif "switch" in cmd_lower:
            retry_commands.append(f"git switch -c {target_branch}")
            
        # Strategy 3: Fuzzy matches as suggestions only (don't auto-execute)
        similar_branches = self._find_similar_branches(target_branch, available_branches)
        if similar_branches:
            print(f"💡 Also found similar branches: {', '.join(similar_branches[:2])}")
            # Don't auto-add fuzzy matches - they should be manual suggestions
        
        # Try each alternative
        for retry_cmd in retry_commands:
            print(f"\n🔄 Trying alternative: {retry_cmd}")
            
            try:
                retry_result = subprocess.run(
                    retry_cmd.split(),
                    capture_output=True,
                    text=True,
                    cwd=".",
                    timeout=30
                )
                
                if retry_result.returncode == 0:
                    print("✅ Alternative succeeded!")
                    if retry_result.stdout.strip():
                        print(f"📤 Output:\n{retry_result.stdout}")
                    return True
                else:
                    print(f"❌ Alternative failed: {retry_result.stderr.strip()}")
                    
            except Exception as e:
                print(f"❌ Alternative failed with exception: {e}")
        
        # If all retries failed, suggest fuzzy matches
        if similar_branches:
            print(f"\n💡 Did you mean one of these existing branches?")
            for branch in similar_branches[:3]:
                print(f"   giti 'switch to {branch}'")
        
        return False
    
    def _get_available_branches(self) -> list:
        """Get list of all available branches (local and remote)"""
        try:
            result = subprocess.run(
                ["git", "branch", "-a"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return []
            
            branches = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    # Clean up branch names (remove *, whitespace, remotes/origin/)
                    branch = line.strip().replace('*', '').strip()
                    if branch.startswith('remotes/origin/'):
                        branch = branch.replace('remotes/origin/', '')
                    if branch and branch != 'HEAD' and '->' not in branch:
                        branches.append(branch)
            
            # Remove duplicates and return
            return list(set(branches))
            
        except Exception:
            return []
    
    def _find_similar_branches(self, target: str, available: list) -> list:
        """Find branches similar to target using fuzzy matching"""
        if not available:
            return []
            
        similar = []
        target_lower = target.lower()
        
        # Exact matches first (case insensitive)
        for branch in available:
            if branch.lower() == target_lower:
                similar.append(branch)
        
        # Partial matches
        for branch in available:
            branch_lower = branch.lower()
            if (target_lower in branch_lower or branch_lower in target_lower) and branch not in similar:
                similar.append(branch)
        
        # Fuzzy matches (common patterns)
        fuzzy_matches = []
        for branch in available:
            branch_lower = branch.lower()
            if branch in similar:
                continue
                
            # Check for common variations
            if any(pattern in branch_lower for pattern in [target_lower[:4], target_lower[-4:]]) and len(target) > 3:
                fuzzy_matches.append(branch)
        
        similar.extend(fuzzy_matches[:2])  # Add top 2 fuzzy matches
        
        return similar[:3]  # Return top 3 overall matches
    
    def _get_confirmation(self) -> bool:
        """
        Get user confirmation to execute commands
        
        Returns:
            True if user confirms, False otherwise
        """
        while True:
            try:
                response = input("Execute these commands? [y/N]: ").strip().lower()
                if response in ['y', 'yes']:
                    return True
                elif response in ['n', 'no', '']:
                    return False
                else:
                    print("Please enter 'y' for yes or 'n' for no")
            except (KeyboardInterrupt, EOFError):
                print("\n❌ Cancelled by user")
                return False
    
    def _get_continue_confirmation(self) -> bool:
        """
        Get user confirmation to continue after an error
        
        Returns:
            True if user wants to continue, False otherwise
        """
        while True:
            try:
                response = input("Continue with remaining commands? [y/N]: ").strip().lower()
                if response in ['y', 'yes']:
                    return True
                elif response in ['n', 'no', '']:
                    return False
                else:
                    print("Please enter 'y' for yes or 'n' for no")
            except (KeyboardInterrupt, EOFError):
                print("\n❌ Cancelled by user")
                return False 