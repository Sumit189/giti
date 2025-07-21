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
    
    def __init__(self, model_path: str, max_tokens: int = 50, temperature: float = 0.1):
        """
        Initialize the LLM runner for Qwen2.5-Coder with speed optimizations
        
        Args:
            model_path: Path to the GGUF model file
            max_tokens: Maximum tokens to generate (reduced for speed)
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
            n_ctx=1024,  # Smaller context for speed
            n_threads=None,  # Use all available CPU threads
            verbose=False,  # Suppress llama.cpp logs
            seed=42,  # For reproducible results
            chat_format="chatml",  # Use ChatML format for Qwen models
            n_batch=256,  # Smaller batch for speed
            use_mmap=True,  # Memory mapping for faster loading
            use_mlock=False,  # Don't lock memory for faster startup
            n_gpu_layers=0,  # CPU only for consistency
        )
        print("Model loaded!")
    
    def generate(self, prompt: str) -> str:
        """
        Generate git commands using Qwen2.5-Coder (optimized for speed)
        
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
                top_p=0.8,  # Slightly higher for speed
                top_k=20,   # Lower for faster sampling
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
                    top_p=0.8,
                    top_k=20,
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