#!/usr/bin/env python3

"""
giti - Natural language to Git commands CLI tool
"""

import argparse
import sys
import os
import atexit
from pathlib import Path

from llm_runner import LLMRunner
from parser import PromptParser
from executor import CommandExecutor

# Store the original working directory where giti was invoked
ORIGINAL_CWD = os.environ.get('GITI_ORIGINAL_CWD', os.getcwd())

# Global model cache for speed
_model_cache = {}
_parser_cache = None


def get_llm_runner(model_path: str) -> LLMRunner:
    """Get cached LLM runner or create new one"""
    global _model_cache
    
    if model_path not in _model_cache:
        _model_cache[model_path] = LLMRunner(model_path)
        # Register cleanup on exit
        atexit.register(lambda: _model_cache[model_path].cleanup() if model_path in _model_cache else None)
    
    return _model_cache[model_path]


def get_prompt_parser() -> PromptParser:
    """Get cached prompt parser or create new one"""
    global _parser_cache
    
    if _parser_cache is None:
        _parser_cache = PromptParser()
    
    return _parser_cache


def main():
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    default_model_path = script_dir / "models" / "Qwen2.5-Coder-1.5B-Instruct-Q4_K_M.gguf"
    
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
        default=str(default_model_path),
        help="Path to the GGUF model file"
    )
    
    args = parser.parse_args()
    
    # Validate model file exists
    if not os.path.exists(args.model_path):
        print(f"❌ Model file not found at {args.model_path}")
        print("📥 Please download the Qwen2.5-Coder-1.5B model:")
        print("   wget https://huggingface.co/bartowski/Qwen2.5-Coder-1.5B-Instruct-GGUF/resolve/main/Qwen2.5-Coder-1.5B-Instruct-Q4_K_M.gguf")
        sys.exit(1)
    
    # Initialize components (with caching for speed)
    try:
        llm_runner = get_llm_runner(args.model_path)
        prompt_parser = get_prompt_parser()
    except Exception as e:
        print(f"❌ Error initializing components: {e}")
        print("💡 Make sure the model file is valid and you have enough memory.")
        sys.exit(1)
    
    # Load context if provided
    context_data = None
    if args.context:
        if not os.path.exists(args.context):
            print(f"❌ Context file not found at {args.context}")
            print("💡 Make sure the file path is correct.")
            sys.exit(1)
        context_data = prompt_parser.load_context_file(args.context)
    
    if args.shell:
        # Interactive shell mode
        run_interactive_shell(args, llm_runner, prompt_parser, context_data)
    elif args.query:
        # Single command mode
        process_query(args.query, args, llm_runner, prompt_parser, context_data)
    else:
        parser.print_help()
        sys.exit(1)


def process_query(query: str, args, llm_runner: LLMRunner, prompt_parser: PromptParser, context_data=None):
    """Process a single natural language query"""
    try:
        # Generate prompt with context
        prompt = prompt_parser.generate_prompt(query, context_data)
        
        # Get response from LLM
        print("🤔 Thinking...")
        raw_response = llm_runner.generate(prompt)
        
        # Parse commands
        commands = prompt_parser.parse_commands(raw_response)
        
        if not commands:
            print("❌ Could not generate valid commands for that query.")
            print("💡 Try rephrasing or being more specific.")
            return
        
        # Execute commands in the original working directory
        executor = CommandExecutor(
            dry_run=args.dry_run, 
            no_confirm=args.no_confirm,
            working_directory=ORIGINAL_CWD
        )
        executor.execute_commands(commands)
        
    except Exception as e:
        print(f"❌ Error processing query: {e}")
        print("💡 Try a simpler query or check if you're in a git repository.")


def run_interactive_shell(args, llm_runner: LLMRunner, prompt_parser: PromptParser, context_data=None):
    """Run interactive shell mode"""
    print("🌟 Welcome to giti interactive mode!")
    print("💡 Describe what you want to do in natural language")
    print("⌨️  Type 'exit', 'quit', or 'q' to leave\n")
    
    while True:
        try:
            query = input("giti> ").strip()
            
            if query.lower() in ['exit', 'quit', 'q']:
                print("👋 Thanks for using giti!")
                break
                
            if not query:
                continue
                
            process_query(query, args, llm_runner, prompt_parser, context_data)
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Thanks for using giti!")
            break
        except EOFError:
            print("\n👋 Thanks for using giti!")
            break


if __name__ == "__main__":
    main() 