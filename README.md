# Infosys Agentic AI Training - Labs Repository

## Overview

This repository contains the complete lab exercises for the **3-Day Agentic AI Training Program**, covering LangChain, LangGraph, and FastAPI deployment.

## Repository Structure

```
labs/
├── Day1_Medium/          # Day 1: Basic Conversational Agent
├── Day1_Advanced/        # Day 1: Multi-Tool Agent with RAG
├── Day2_Medium/          # Day 2: Multi-Agent Research System
├── Day2_Advanced/        # Day 2: Complex Multi-Agent System
├── Day3_Medium/          # Day 3: FastAPI Deployment
└── Day3_Advanced/        # Day 3: Production-Ready API
```

## Quick Start

### Prerequisites

- Python 3.11 or higher
- OpenAI API Key
- Git

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/VinayKDH/Infosys_Agentic.git
   cd Infosys_Agentic
   ```

2. **Navigate to a lab:**
   ```bash
   cd labs/Day1_Medium
   ```

3. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables:**
   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=your_key_here" > .env
   ```

6. **Run the lab:**
   ```bash
   python main.py
   ```

## Lab Overview

### Day 1: Foundation
- **Medium Lab:** Basic conversational agent with tools (calculator, web search)
- **Advanced Lab:** Multi-tool agent with RAG (Retrieval-Augmented Generation)

### Day 2: Multi-Agent Systems
- **Medium Lab:** Two-agent research and summarization system
- **Advanced Lab:** Four-agent collaborative system with planning and review

### Day 3: Production Deployment
- **Medium Lab:** FastAPI service with async endpoints and streaming
- **Advanced Lab:** Production-ready API with authentication, caching, and monitoring

## Features

- ✅ Complete working code for all labs
- ✅ Step-by-step implementations
- ✅ Production-ready examples
- ✅ Comprehensive error handling
- ✅ Best practices included

## Requirements

Each lab includes its own `requirements.txt` with all necessary dependencies.

## Usage

Each lab directory contains:
- `README.md` - Lab-specific instructions
- `requirements.txt` - Python dependencies
- `main.py` or `app/` - Application code
- `.env.example` - Environment variable template

## Important Notes

- **This is a read-only repository** - You can clone and use the code, but cannot push changes
- **API Keys Required:** You'll need your own OpenAI API key for the labs
- **Python Version:** Recommended Python 3.11 or higher

## Support

For issues or questions, please refer to the lab-specific README files in each directory.

## License

This repository is for educational purposes as part of the Infosys Agentic AI Training Program.

---

**Note:** This repository is public and read-only. All code is provided for learning and reference purposes.

