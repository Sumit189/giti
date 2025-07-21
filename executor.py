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
                    
                    # Ask if user wants to continue with remaining commands
                    if i < len(commands) and not self.no_confirm:
                        if not self._get_continue_confirmation():
                            print("🛑 Execution stopped")
                            break
                            
            except subprocess.TimeoutExpired:
                print("⏰ Command timed out after 30 seconds")
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