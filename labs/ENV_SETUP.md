# Environment Setup Guide

## Creating .env Files

For each lab, create a `.env` file in the lab directory with the following content:

### Day 1 Medium & Day 2 Medium
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Day 1 Advanced
```env
OPENAI_API_KEY=your_openai_api_key_here
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=agentic-ai-lab
```

### Day 2 Advanced
```env
OPENAI_API_KEY=your_openai_api_key_here
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=
```

### Day 3 Medium
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Day 3 Advanced
```env
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your-secret-key-change-in-production
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_ENABLED=true
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=agentic-ai-production
```

## Getting Your OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key and paste it in your `.env` file

## Important Notes

- Never commit `.env` files to version control
- Keep your API keys secure
- The `.env` file should be in the same directory as `main.py` or the entry point

