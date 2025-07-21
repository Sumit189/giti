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
    
    def __init__(self, model_path: str, max_tokens: int = 512, temperature: float = 0.1):
        """
        Initialize the LLM runner
        
        Args:
            model_path: Path to the GGUF model file
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (lower = more deterministic)
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        self.model_path = model_path
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Initialize the model with optimized settings
        print(f"Loading model from {model_path}...")
        self.llm = Llama(
            model_path=model_path,
            n_ctx=2048,  # Context window
            n_threads=None,  # Use all available CPU threads
            verbose=False,  # Suppress llama.cpp logs
            seed=42  # For reproducible results
        )
        print("Model loaded successfully!")
    
    def generate(self, prompt: str) -> str:
        """
        Generate text from the given prompt
        
        Args:
            prompt: Input prompt for the model
            
        Returns:
            Generated text response
        """
        try:
            response = self.llm(
                prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=0.9,
                repeat_penalty=1.1,
                stop=["USER:", "ASSISTANT:", "\n\n"]  # Stop tokens
            )
            
            generated_text = response['choices'][0]['text'].strip()
            return generated_text
            
        except Exception as e:
            raise RuntimeError(f"Error generating response: {e}")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if hasattr(self, 'llm'):
            del self.llm 