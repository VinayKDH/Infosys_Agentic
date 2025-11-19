# Installation Guide for Day1_Advanced

## Quick Setup

1. **Make sure you're in the Day1_Advanced directory:**
   ```bash
   cd labs/Day1_Advanced
   ```

2. **Activate your virtual environment:**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install all dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Verify installation:**
   ```bash
   python -c "import langchain_openai; print('✓ langchain-openai installed')"
   python -c "import langchain_community; print('✓ langchain-community installed')"
   python -c "import langchain_experimental; print('✓ langchain-experimental installed')"
   python -c "import faiss; print('✓ faiss-cpu installed')"
   ```

5. **Create .env file:**
   ```bash
   # Create .env file with:
   OPENAI_API_KEY=your_key_here
   ```

6. **Run the application:**
   ```bash
   python main.py
   ```

## Troubleshooting

### "ModuleNotFoundError: No module named 'langchain_openai'"

**Solution:**
```bash
pip install langchain-openai
```

Or reinstall all packages:
```bash
pip install -r requirements.txt --force-reinstall
```

### "ModuleNotFoundError: No module named 'faiss'"

**Solution:**
```bash
pip install faiss-cpu
```

### "ModuleNotFoundError: No module named 'langchain_experimental'"

**Solution:**
```bash
pip install langchain-experimental
```

### All packages missing

**Solution:**
```bash
# Remove old venv and create new one
deactivate
rm -rf venv  # or rmdir /s venv on Windows
python3.11 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install --upgrade pip
pip install -r requirements.txt
```

## Required Packages

Make sure these are installed:
- langchain
- langchain-openai
- langchain-community
- langchain-experimental
- langchain-text-splitters
- langchain-core
- faiss-cpu
- pypdf
- python-dotenv
- duckduckgo-search
- tiktoken

