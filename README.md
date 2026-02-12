# 🤖 AI Test Agent

Automatically generates pytest tests for your Python code using local AI (Ollama)

## What It Does

1. Scans your Python files
2. Finds functions without tests
3. Generates tests automatically using AI
4. Adds imports automatically
5. Validates that tests work
6. Creates a detailed report

## Quick Start

```bash
# 1. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Download AI model (~2GB)
ollama pull llama3.2

# 3. Clone and setup
git clone https://github.com/yourusername/test-agent.git
cd test-agent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 4. Run
python test_agent.py
```

## Example

**Your code:**
```python
# calculator.py
def power(a, b):
    return a ** b
```

**Generated test:**
```python
# test_calculator.py
import pytest
from calculator import power

def test_power():
    assert power(2, 3) == 8
    assert power(-1, 2) == 1
    assert power(0, 5) == 0
```

## How It Works

```
Your Code → AI Analyzes → Generates Tests → Validates → Done!
```

1. **Scan**: Finds all functions in your `.py` files
2. **Identify**: Checks which functions lack tests
3. **Generate**: AI creates pytest tests with proper assertions
4. **Import**: Automatically adds `import` statements
5. **Validate**: Runs tests to ensure they pass
6. **Report**: Creates `test_report_*.md` with results

## Configuration

Change AI model in `test_agent.py` (line 496):
```python
agent = TestAgent(model="mistral")  # or "llama3.2:1b"
```

## Requirements

- Python 3.12+
- Ollama (local AI server)
- 2-4GB disk space for AI model

## Results
- ✅ 5-10 tests generated per minute
- ✅ Saves 70% time vs manual testing