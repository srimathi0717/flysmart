# flysmart

To set up environment variables for the FlySmart application, you need to store sensitive information like API keys securely. Here's a guide on how to do this:

## Setting Up Environment Variables

### 1. Create a `.env` File

Create a `.env` file in the root directory of your project. This file will store your environment variables. Add the following lines to the `.env` file:

```
RAPIDAPI_HOST=sky-scanner3.p.rapidapi.com
RAPIDAPI_KEY=your_rapidapi_key
SKY_SCANNER_URL=https://sky-scanner3.p.rapidapi.com/flights/price-calendar-web
```

Replace `your_rapidapi_key` with your actual RapidAPI key.

### 2. Install `python-dotenv`

You need the `python-dotenv` package to load the environment variables from the `.env` file. Install it using pip:

```bash
pip install python-dotenv
```

### 3. Load Environment Variables in Your Application

Modify the `config.py` file to load the environment variables using `python-dotenv`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

HEADERS = {
    'x-rapidapi-host': os.getenv("RAPIDAPI_HOST"),
    'x-rapidapi-key': os.getenv("RAPIDAPI_KEY")
}

SKY_SCANNER_URL = os.getenv("SKY_SCANNER_URL")
```

### 4. Update Your README

Add instructions for setting up environment variables in the README file:

---

## Setting Up Environment Variables

1. **Create a `.env` file:**

    In the root directory of your project, create a file named `.env` and add the following lines:

    ```
    RAPIDAPI_HOST=sky-scanner3.p.rapidapi.com
    RAPIDAPI_KEY=your_rapidapi_key
    SKY_SCANNER_URL=https://sky-scanner3.p.rapidapi.com/flights/price-calendar-web
    ```

    Replace `your_rapidapi_key` with your actual RapidAPI key.

2. **Install `python-dotenv`:**

    ```bash
    pip install python-dotenv
    ```

3. **Ensure your application loads environment variables:**

    Your `config.py` should look like this:

    ```python
    import os
    from dotenv import load_dotenv

    load_dotenv()

    HEADERS = {
        'x-rapidapi-host': os.getenv("RAPIDAPI_HOST"),
        'x-rapidapi-key': os.getenv("RAPIDAPI_KEY")
    }

    SKY_SCANNER_URL = os.getenv("SKY_SCANNER_URL")
    ```

---

This setup ensures that sensitive information like API keys is not hard-coded into your application and can be easily managed using environment variables.
