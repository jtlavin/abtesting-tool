# AB Testing Calculator

A Streamlit application for conducting and analyzing AB tests. This tool helps you design, run, and analyze AB experiments with comprehensive statistical analysis.

## Installation

You can install the dependencies using either `pip` (with requirements.txt) or `uv`:

### Using pip (requirements.txt)

1. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Using uv

1. Install uv if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create a virtual environment and install dependencies:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

## Running the Application

After installing dependencies, run the application with:

```bash
streamlit run app.py
```

## Maintaining Dependencies

### When Adding New Libraries

1. Install the new library:
```bash
# Using pip
pip install new-library

# Or using uv
uv pip install new-library
```

2. Update requirements.txt:
```bash
# Using pip
pip freeze > requirements.txt

# Or using uv
uv pip freeze > requirements.txt
```

### Best Practices

- Always update requirements.txt after adding new dependencies
- Review the generated requirements.txt to ensure only necessary packages are included
- Consider using specific versions for critical dependencies
- Document major dependency changes in commit messages

## Project Structure

- `app.py`: Main Streamlit application
- `requirements.txt`: Project dependencies
- `README.md`: This documentation file

## Features

- Data upload and preview
- Experiment setup and parameter configuration
- Sample size calculation
- Statistical analysis
- Results visualization
