# Python 3.11 Setup Guide for All Labs

## Recommended Python Version

**Python 3.11** is the recommended version for all labs. It provides:
- ✅ Excellent stability with LangChain
- ✅ Full package compatibility
- ✅ No compatibility warnings
- ✅ Best performance

## Installation

### Windows
1. Download Python 3.11 from: https://www.python.org/downloads/release/python-3110/
2. During installation, check "Add Python to PATH"
3. Verify installation:
   ```bash
   python --version
   # Should show: Python 3.11.x
   ```

### Mac/Linux
```bash
# Using Homebrew (Mac)
brew install python@3.11

# Using pyenv (recommended)
pyenv install 3.11.9
pyenv global 3.11.9
```

## Setup for Each Lab

### 1. Create Virtual Environment
```bash
# Navigate to lab directory
cd labs/Day1_Medium  # or any other lab

# Create venv with Python 3.11
python3.11 -m venv venv

# Or if python3.11 is your default
python -m venv venv
```

### 2. Activate Virtual Environment
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Upgrade pip
```bash
pip install --upgrade pip
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Create .env File
```bash
# Create .env file with your OpenAI API key
OPENAI_API_KEY=your_key_here
```

### 6. Run the Lab
```bash
python main.py
```

## Verification

After setup, verify everything works:
```bash
python -c "import langchain; print('LangChain:', langchain.__version__)"
python -c "import langchain_openai; print('LangChain OpenAI: OK')"
python -c "import langchain_community; print('LangChain Community: OK')"
```

## Troubleshooting

### Issue: "python3.11: command not found"
**Solution:** 
- Windows: Use `py -3.11` instead
- Mac/Linux: Install Python 3.11 or use `python3` if it's 3.11

### Issue: Package installation errors
**Solution:**
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt --no-cache-dir
```

### Issue: Import errors
**Solution:**
```bash
# Reinstall all packages
pip uninstall -y langchain langchain-openai langchain-community
pip install -r requirements.txt
```

## All Labs Tested With Python 3.11

✅ Day1_Medium - Fully compatible  
✅ Day1_Advanced - Fully compatible  
✅ Day2_Medium - Fully compatible  
✅ Day2_Advanced - Fully compatible  
✅ Day3_Medium - Fully compatible  
✅ Day3_Advanced - Fully compatible  

## Quick Start Script

Create a `setup.sh` (Mac/Linux) or `setup.bat` (Windows) in each lab:

**setup.sh:**
```bash
#!/bin/bash
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "Setup complete! Activate with: source venv/bin/activate"
```

**setup.bat:**
```batch
@echo off
python -m venv venv
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo Setup complete! Activate with: venv\Scripts\activate
```

