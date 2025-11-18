# Python 3.14 Compatibility Guide

## Overview

All lab projects have been updated to be compatible with Python 3.14 and use the latest compatible package versions. This document outlines the changes made and any considerations for Python 3.14.

## Package Updates

### LangChain Ecosystem
- **langchain**: Updated from 0.1.0 to >=0.3.0
- **langchain-openai**: Updated from 0.0.5 to >=0.2.0
- **langchain-community**: Updated from 0.0.20 to >=0.3.0
- **langgraph**: Updated from 0.0.20 to >=0.2.0
- **langchain-experimental**: Updated from 0.0.50 to >=0.1.0
- **langchain-text-splitters**: Added as separate package (>=0.3.0)

### FastAPI & Web Framework
- **fastapi**: Updated from 0.104.1 to >=0.115.0
- **uvicorn**: Updated from 0.24.0 to >=0.32.0
- **pydantic**: Updated from 2.5.0 to >=2.9.0
- **pydantic-settings**: Updated from 2.1.0 to >=2.6.0

### Other Dependencies
- **duckduckgo-search**: Updated from 4.1.1 to >=6.0.0
- **pypdf**: Updated from 3.17.0 to >=5.0.0
- **faiss-cpu**: Updated from 1.7.4 to >=1.8.0
- **tiktoken**: Updated from 0.5.1 to >=0.8.0
- **redis**: Updated from 5.0.1 to >=5.2.0
- **prometheus-client**: Updated from 0.19.0 to >=0.21.0

## Code Changes

### Import Updates

#### LangChain Core Imports
Changed from:
```python
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
```

To:
```python
from langchain_core.tools import Tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
```

#### Community Tools
Changed from:
```python
from langchain_community.utilities import DuckDuckGoSearchRun
```

To:
```python
from langchain_community.tools import DuckDuckGoSearchRun
```

### RAG Implementation (Day 1 Advanced)

The `RetrievalQA` chain has been replaced with LangChain Expression Language (LCEL) for better compatibility:

**Old Implementation:**
```python
self.qa_chain = RetrievalQA.from_chain_type(
    llm=self.llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)
```

**New Implementation:**
```python
self.qa_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough()
    }
    | prompt
    | self.llm
    | StrOutputParser()
)
```

### Pydantic v2 Compatibility

All Pydantic models are already using v2 syntax:
- `model_dump_json()` instead of `json()` (already in use)
- Field definitions remain compatible

## Installation Notes

### Python 3.14 Specific Considerations

1. **Virtual Environment**: Always use a virtual environment:
   ```bash
   python3.14 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Package Installation**: Use pip with the updated requirements:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Potential Issues**:
   - Some packages may need to be compiled from source
   - If you encounter build errors, ensure you have:
     - `gcc` or `clang` (for C extensions)
     - `python3.14-dev` headers
     - `build-essential` (Linux) or Xcode Command Line Tools (macOS)

### FAISS Installation

If `faiss-cpu` installation fails on Python 3.14:
```bash
# Try installing from conda-forge instead
conda install -c conda-forge faiss-cpu

# Or use pip with pre-built wheels
pip install faiss-cpu --no-cache-dir
```

## Testing Compatibility

To verify your installation:

```bash
python --version  # Should show Python 3.14.x
python -c "import langchain; print(langchain.__version__)"
python -c "import fastapi; print(fastapi.__version__)"
python -c "import pydantic; print(pydantic.__version__)"
```

## Known Issues & Workarounds

### Issue 1: LangChain Agent Initialization
**Symptom**: `AgentType` enum not found or deprecated
**Solution**: The code uses `AgentType.CONVERSATIONAL_REACT_DESCRIPTION` which is still supported in newer versions

### Issue 2: DuckDuckGo Search
**Symptom**: Search tool not working
**Solution**: Ensure `duckduckgo-search>=6.0.0` is installed. The API has changed in newer versions.

### Issue 3: FAISS Vector Store
**Symptom**: Import errors or runtime issues
**Solution**: 
- Use `faiss-cpu>=1.8.0` for CPU-only systems
- For GPU support, use `faiss-gpu` (requires CUDA)

## Version Pinning (Optional)

If you encounter specific compatibility issues, you can pin to exact versions. However, the current setup uses `>=` to allow for updates while ensuring minimum compatibility.

For production deployments, consider pinning exact versions:
```txt
langchain==0.3.15
langchain-openai==0.2.8
# etc.
```

## Support

If you encounter Python 3.14-specific issues:

1. Check package documentation for Python 3.14 support
2. Verify all dependencies are installed correctly
3. Check for error messages in the terminal
4. Review the package changelogs for breaking changes

## Migration Checklist

- [x] Updated all requirements.txt files
- [x] Updated LangChain imports to use `langchain_core`
- [x] Updated RAG implementation to use LCEL
- [x] Updated tool imports
- [x] Verified Pydantic v2 compatibility
- [x] Updated FastAPI and related packages
- [x] Added langchain-text-splitters dependency

All labs are now compatible with Python 3.14!

