# Super-Python-Coder

## Description
**Super-Python-Coder** is an intelligent Python code generation tool that leverages OpenAI's GPT models to create, test, and optimize Python programs. It includes error handling, runtime optimization, and linting to ensure high-quality code.

## Features
- Generates Python code based on user input or random selection from predefined programs.
- Includes unit tests to validate the generated code.
- Identifies errors in the generated code and iteratively fixes them using GPT.
- Optimizes code runtime performance while retaining functionality.
- Performs linting to adhere to coding best practices.

### Prerequisites
- Python 3.8 or higher
- A `.env` file containing your OpenAI API key:
OPENAI_API_KEY=your_openai_api_key

### Dependencies
Install the required Python libraries using pip:
```bash
pip install openai python-dotenv colorama tqdm pylint

