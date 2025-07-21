"""
LLM Runner - Interface for llama.cpp model inference
"""

import os
from typing import Optional

try:
    from llama_cpp import Llama
except ImportError:
    print("Error: llama-cpp-python not installed. Run: pip install llama-cpp-python")
    exit(1)


class LLMRunner:
    """Handles local LLM inference using llama.cpp"""
    
    def __init__(self, model_path: str, max_tokens: int = 100, temperature: float = 0.1):
        """
        Initialize the LLM runner for Qwen2.5-Coder
        
        Args:
            model_path: Path to the GGUF model file
            max_tokens: Maximum tokens to generate  
            temperature: Sampling temperature
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        self.model_path = model_path
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        print(f"Loading Qwen2.5-Coder model from {model_path}...")
        self.llm = Llama(
            model_path=model_path,
            n_ctx=4096,  # Good context window for examples
            n_threads=None,  # Use all available CPU threads
            verbose=False,  # Suppress llama.cpp logs
            seed=42,  # For reproducible results
            chat_format="chatml",  # Use ChatML format for Qwen models
        )
        print("Model loaded successfully!")
    
    def generate(self, prompt: str) -> str:
        """
        Generate git commands using Qwen2.5-Coder
        
        Args:
            prompt: Input prompt for the model
            
        Returns:
            Generated git command(s)
        """
        try:
            # Use chat completion for better instruction following
            response = self.llm.create_chat_completion(
                messages=[
                    {"role": "system", "content": "You are a Git command expert. Respond only with valid Git commands, nothing else."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=0.9,
                stream=False
            )
            
            generated_text = response['choices'][0]['message']['content'].strip()
            return generated_text
            
        except Exception as e:
            # Fallback to regular completion if chat format fails
            try:
                response = self.llm(
                    prompt,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    top_p=0.9,
                    stop=["Human:", "Assistant:", "\n\n"],
                    echo=False,
                    stream=False
                )
                return response['choices'][0]['text'].strip()
            except Exception as fallback_e:
                raise RuntimeError(f"Error generating response: {e}, Fallback error: {fallback_e}")

    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'llm'):
            del self.llm 