# Obsidian Vocabulary Card Generator

A Flask web application that takes text input, uses AI to generate detailed vocabulary cards, and saves them as Markdown files compatible with Obsidian.

## Table of Contents

* [About the Project](#about-the-project)
  * [Features](#features)
  * [Built With](#built-with)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
  * [Configuration](#configuration)
* [Usage](#usage)
  * [Web Interface](#web-interface)
  * [API Endpoint](#api-endpoint)
* [File Structure](#file-structure)
* [Roadmap](#roadmap)
* [Acknowledgments](#acknowledgments)

## About The Project

This project provides a simple way to automatically create vocabulary flashcards in Markdown format. You input a piece of text containing words you want to learn, and the application leverages Google's Gemini AI to generate comprehensive cards for each word, including definitions, pronunciation, examples, synonyms, and contextual usage. These cards are then saved as individual `.md` files in a specified folder, ready to be integrated into your Obsidian vault or any other Markdown-based note-taking system.

### Features

*   **AI-Powered Vocabulary Generation:** Uses Google Gemini to create rich vocabulary cards.
*   **Structured Output:** Generates cards with fields for Word, Explanation, Pronunciation, Examples, Registers, Synonyms, and In-Context usage.
*   **Markdown Format:** Saves vocabulary cards as `.md` files, perfect for Obsidian.
*   **Web Interface:** Easy-to-use web page to input text and trigger generation.
*   **API Endpoint:** Provides a `/api/vocab` endpoint for programmatic access.
*   **Configurable Output:** Specify the output folder for your Markdown files.

### Built With

*   Python
*   Flask
*   Google Generative AI (Gemini)
*   Pydantic
*   OpenAI Python Client (used for Perplexity AI, though Perplexity specific calls are not in the current `app.py` logic beyond client initialization)

## Getting Started

Follow these instructions to get a local copy up and running.

### Prerequisites

*   Python 3.8+
*   pip (Python package installer)
*   Git (for cloning the repository)

### Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/your_username/Obsidian-automation.git
    cd Obsidian-automation
    ```
    *(Replace `your_username` with your actual GitHub username if you've forked/cloned it under your account)*

2.  **Create and activate a virtual environment** (recommended):
    ```sh
    python -m venv myenv
    # On Windows
    myenv\Scripts\activate
    # On macOS/Linux
    source myenv/bin/activate
    ```

3.  **Install dependencies:**
    ```sh
    pip install Flask google-generativeai pydantic openai
    ```

### Configuration

1.  **API Keys:**
    This application requires API keys for Google Gemini and (optionally, as per current code structure) Perplexity AI. These are loaded from a `pyvenv.cfg` file within your virtual environment directory (`myenv/pyvenv.cfg`).

    *   **Important Note:** Storing secrets directly in `myenv/pyvenv.cfg` is not a standard practice for `venv` which auto-generates this file. A more common approach is using a `.env` file and a library like `python-dotenv`, or environment variables. However, following the current project structure:

    Edit/Create `myenv/pyvenv.cfg` and add a `[settings]` section (or modify it if it exists) with your API keys:
    ```ini
    [settings]
    gemini_client_api_key = YOUR_GEMINI_API_KEY
    sonar_client_api_key = YOUR_PERPLEXITY_AI_API_KEY
    # Optional: Specify the output folder for Markdown files
    # vault_folder = path/to/your/obsidian_subfolder
    ```
    Replace `YOUR_GEMINI_API_KEY` and `YOUR_PERPLEXITY_AI_API_KEY` with your actual keys.
    If `vault_folder` is not specified, it defaults to a folder named `vault` in the project root.

2.  **Gemini Prompt:**
    The application uses a system prompt for the Gemini AI, which is read from `prompt.vocab.txt`. Create this file in the root of your project directory.

## Usage

1.  **Run the Flask application:**
    ```sh
    python app.py
    ```
    The application will start, typically on `http://127.0.0.1:5000/`.

### Web Interface

*   Open your web browser and navigate to `http://127.0.0.1:5000/`.
*   Enter the text containing the vocabulary words you want to process into the input field.
*   Click "Submit".
*   The application will process the text, generate vocabulary cards, and save them as Markdown files in the configured `vault_folder`.
*   The web page will display the generated card data or any error messages.

### API Endpoint

You can also interact with the application programmatically via its API.

*   **Endpoint:** `POST /api/vocab`
*   **Request Body (JSON):**
    ```json
    {
      "input_text": "Your text containing words like serendipity, ephemeral, and elucidate."
    }
    ```
*   **Success Response (JSON):**
    ```json
    {
      "response": [
        {
          "Word": "serendipity",
          "Explanation": "The occurrence and development of events by chance in a happy or beneficial way.",
          // ... other fields ...
        }
        // ... other cards ...
      ]
    }
    ```
*   **Error Response (JSON):**
    ```json
    {
      "error": "Error message detailing the issue"
    }
    ```

## File Structure

```
Obsidian-automation/
├── myenv/                  # Virtual environment directory
│   └── pyvenv.cfg          # Configuration file (includes API keys)
├── vault/                  # Default output folder for Markdown vocabulary cards
├── app.py                  # Main Flask application logic
├── prompt.vocab.txt        # System prompt for Gemini AI
├── templates/
│   └── index.html          # HTML template for the web interface
└── README.md               # This file
```

## Roadmap

*   [ ] Add support for more AI models.
*   [ ] Improve error handling and user feedback.
*   [ ] Create a more robust configuration system (e.g., using `.env` files).

## Acknowledgments

*   Google Gemini
*   Flask
*   Pydantic
*   Img Shields (for any badges you might add later)
*   Choose an Open Source License
```