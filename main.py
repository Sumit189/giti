"""
giti - Natural language to Git commands CLI tool
"""

import argparse
import sys
import os
from pathlib import Path

from llm_runner import LLMRunner
from parser import PromptParser
from executor import CommandExecutor


def main():
    parser = argparse.ArgumentParser(
        description="Convert natural language to Git commands using local LLM",
        prog="giti"
    )
    
    parser.add_argument(
        "query",
        nargs="?",
        help="Natural language description of Git operation"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show commands without executing them"
    )
    
    parser.add_argument(
        "--context",
        type=str,
        metavar="FILE",
        help="Use RAG-style document to enhance model responses"
    )
    
    parser.add_argument(
        "--shell",
        action="store_true",
        help="Run in interactive REPL mode"
    )
    
    parser.add_argument(
        "--no-confirm",
        action="store_true",
        help="Skip confirmation prompts before execution"
    )
    
    parser.add_argument(
        "--model-path",
        type=str,
        default="models/phi-1_5-Q4_K_M.gguf",
        help="Path to the GGUF model file"
    )
    
    args = parser.parse_args()
    
    # Validate model file exists
    if not os.path.exists(args.model_path):
        print(f"Error: Model file not found at {args.model_path}")
        print("Please run the installation script or download the model manually:")
        print("cd models && wget https://huggingface.co/TKDKid1000/phi-1_5-GGUF/resolve/main/phi-1_5-Q4_K_M.gguf")
        sys.exit(1)
    
    # Initialize components
    try:
        llm_runner = LLMRunner(args.model_path)
        prompt_parser = PromptParser()
        executor = CommandExecutor(dry_run=args.dry_run, no_confirm=args.no_confirm)
    except Exception as e:
        print(f"Error initializing components: {e}")
        sys.exit(1)
    
    # Load context if provided
    context_data = None
    if args.context:
        if not os.path.exists(args.context):
            print(f"Error: Context file not found at {args.context}")
            sys.exit(1)
        context_data = prompt_parser.load_context_file(args.context)
    
    if args.shell:
        # Interactive shell mode
        run_interactive_shell(llm_runner, prompt_parser, executor, context_data)
    elif args.query:
        # Single command mode
        process_query(args.query, llm_runner, prompt_parser, executor, context_data)
    else:
        parser.print_help()
        sys.exit(1)


def process_query(query, llm_runner, prompt_parser, executor, context_data=None):
    """Process a single natural language query"""
    try:
        # Generate prompt with context
        prompt = prompt_parser.generate_prompt(query, context_data)
        
        # Get LLM response
        print("Thinking...")
        response = llm_runner.generate(prompt)
        
        # Parse commands from response
        commands = prompt_parser.extract_commands(response)
        
        if not commands:
            print("Error: No valid Git commands found in the response")
            return
        
        # Execute commands
        executor.execute_commands(commands)
        
    except Exception as e:
        print(f"Error processing query: {e}")


def run_interactive_shell(llm_runner, prompt_parser, executor, context_data=None):
    """Run interactive REPL mode"""
    print("Welcome to giti interactive shell!")
    print("Type 'exit' or 'quit' to leave, 'help' for assistance")
    print()
    
    while True:
        try:
            query = input("giti> ").strip()
            
            if query.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            elif query.lower() == "help":
                print_help()
                continue
            elif not query:
                continue
            
            process_query(query, llm_runner, prompt_parser, executor, context_data)
            print()
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break


def print_help():
    """Print help for interactive mode"""
    print("""
Available commands:
  - Any natural language Git query (e.g., "commit all changes")
  - help: Show this help message
  - exit/quit: Exit the shell
    """)


if __name__ == "__main__":
    main() 