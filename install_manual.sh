#!/bin/bash

# Simple manual installation for giti

echo "Installing giti - Natural Language Git CLI"
echo "========================================"

# Get the absolute path of the current directory
GITI_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if Python 3.8+ is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    echo "Please install Python 3.8 or later and try again."
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip3 install llama-cpp-python

# Make main.py executable
chmod +x "$GITI_DIR/main.py"

# Create global command to make 'giti' available globally
if [ ! -f "/usr/local/bin/giti" ]; then
    echo "Creating global 'giti' command..."
    echo "#!/bin/bash" > /tmp/giti
    echo "cd \"$GITI_DIR\"" >> /tmp/giti
    echo "python3 \"$GITI_DIR/main.py\" \"\$@\"" >> /tmp/giti
    chmod +x /tmp/giti
    sudo mv /tmp/giti /usr/local/bin/giti
    echo "✓ 'giti' command installed to /usr/local/bin/giti"
else
    echo "✓ 'giti' command already exists"
fi

# Download model if not present
model_file="$GITI_DIR/models/phi-1_5-Q4_K_M.gguf"
if [ ! -f "$model_file" ]; then
    echo "Downloading language model (~875MB)..."
    cd "$GITI_DIR/models"
    if command -v wget &> /dev/null; then
        wget https://huggingface.co/TKDKid1000/phi-1_5-GGUF/resolve/main/phi-1_5-Q4_K_M.gguf
    elif command -v curl &> /dev/null; then
        curl -L -o phi-1_5-Q4_K_M.gguf https://huggingface.co/TKDKid1000/phi-1_5-GGUF/resolve/main/phi-1_5-Q4_K_M.gguf
    else
        echo "Warning: Neither wget nor curl found."
        echo "Please manually download the model:"
        echo "https://huggingface.co/TKDKid1000/phi-1_5-GGUF/resolve/main/phi-1_5-Q4_K_M.gguf"
        exit 1
    fi
    cd "$GITI_DIR"
    echo "✓ Model downloaded successfully!"
else
    echo "✓ Model file already exists"
fi

echo ""
echo "Installation complete!"
echo ""
echo "Usage examples:"
echo "  giti \"commit all changes with message fix bugs\""
echo "  giti --dry-run \"push to main branch\""
echo "  giti --shell"
echo ""
echo "For help: giti --help" 