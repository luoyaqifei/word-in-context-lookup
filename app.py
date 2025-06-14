from flask import Flask, render_template, request
from google import genai as genai_google # Renamed to avoid conflict with local 'genai' client variable if any
from google.genai import types
from pydantic import BaseModel
from openai import OpenAI
import requests
import os
import configparser

class VocabCard(BaseModel):
    Word: str
    Explanation: str
    Pronunciation: str
    Illustration_Link: str | None = None
    Examples: list[str]
    Registers: list[str]
    Synonyms: list[str]
    In_Context: str


# Load API keys from ./myenv/pyvenv.cfg
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "myenv", "pyvenv.cfg"))

gemini_client_api_key = config.get("settings", "gemini_client_api_key", fallback=None)
sonar_client_api_key = config.get("settings", "sonar_client_api_key", fallback=None)

gemini_client = genai_google.Client(api_key=gemini_client_api_key) # Use renamed import
sonar_client = OpenAI(api_key=sonar_client_api_key, base_url="https://api.perplexity.ai")
vault_folder = config.get("settings", "vault_folder", fallback="vault")

app = Flask(__name__)

def query_gemini(text):
    with open("prompt.vocab.txt", "r", encoding="utf-8") as f:
        prompt_text = f.read()
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=text,
            config={
                "response_mime_type": "application/json",
                "response_schema": list[VocabCard],
                "system_instruction":prompt_text,
            },
        )
    print(f"Raw response: {response.text}")  # Debug: Print raw response
    return response.parsed


def generate_vocabulary_cards(vocab_cards: list[VocabCard]):
    files = []
    for vocab_card in vocab_cards:
        if not isinstance(vocab_card, VocabCard):
            raise ValueError(f"Invalid vocab card object received: {type(vocab_card)}")
        
        print(f"Processing vocab card: {vocab_card.Word}")
        if vocab_card.Illustration_Link:
            # use native method to verify the illustration link to ensure it's valid
            try:                
                response = requests.head(vocab_card.Illustration_Link, allow_redirects=True)
                if response.status_code != 200:
                    print(f"Warning: Illustration link for '{vocab_card.Word}' is invalid (Status Code: {response.status_code})")
                    vocab_card.Illustration_Link = None # Remove invalid link
            except requests.exceptions.RequestException as e:
                print(f"Warning: Could not verify illustration link for '{vocab_card.Word}': {e}")
                vocab_card.Illustration_Link = None # Remove invalid link
                
        markdown = f"""# Word: {vocab_card.Word}
**Word:** {vocab_card.Word}

**Explanation:** {vocab_card.Explanation}

**Pronunciation:** {vocab_card.Pronunciation}

**Examples:**
{chr(10).join(f"- {ex}" for ex in vocab_card.Examples)}

**Registers:** {', '.join(vocab_card.Registers)}

**Synonyms:** {', '.join(vocab_card.Synonyms)}

**In Context:** {vocab_card.In_Context}
"""
        if vocab_card.Illustration_Link:
            markdown += f"\n\n![Illustration]({vocab_card.Illustration_Link})"
        print(markdown)
        files.append({"markdown": markdown, "filename": vocab_card.Word+".md"})
    # If vocab_cards (input) was empty, files will be empty.
    if not files and not vocab_cards: # Check if input was empty and no files were generated
        raise ValueError("No valid vocabulary cards found in the response.")
    return files

def insert_markdown_file(markdown, filename):
    os.makedirs(vault_folder, exist_ok=True)
    file_path = os.path.join(vault_folder, filename)
    print(f"Writing to file: {file_path}")
    # Ensure the file is written with UTF-8 encoding
    if os.path.exists(file_path):
        print(f"File {file_path} already exists. Overwriting.")
    else:
        print(f"Creating new file: {file_path}")
    # Write the markdown content to the file
    # Use 'w' mode to overwrite the file if it exists
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(markdown)
    
@app.route("/api/vocab", methods=["POST"])
def api_vocab():
    if not request.is_json:
        return {"error": "Request must be JSON"}, 415
    data = request.get_json()
    input_text = data.get("input_text", "")
    
    if not input_text:
        return {"error": "input_text cannot be empty"}, 400

    result = lookup_insert(input_text)

    if isinstance(result, str):  # Error message string from lookup_insert
        status_code = 400  # Default for client-side type errors or known issues
        if "unexpected error" in result.lower() or "traceback" in result.lower():
            status_code = 500
        elif "blocked by the content safety filter" in result.lower():
            status_code = 400 # Or a more specific code if available for content filtering
        elif "No vocabulary cards found" in result or "No response from the model" in result:
            # For "not found" type scenarios, you might return 200 with a message or 404
            # For this example, we'll treat it as a client-side issue (e.g. input yields no results)
            status_code = 200 # Or 404, depending on API design for "no results"
            return {"message": result, "response": []}, status_code

        return {"error": result}, status_code
    
    # Success case: result is list[dict]
    return {"response": result}


@app.route("/api/story", methods=["POST"])
def api_story():
    if not request.is_json:
        return {"error": "Request must be JSON"}, 415
    data = request.get_json()
    words = data.get("words", "")
    
    if not words:
        return {"error": "words cannot be empty"}, 400

    try:
        with open("prompt.story.txt", "r", encoding="utf-8") as f:
            prompt_text = f.read()
            response = gemini_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=words,
                config={
                    "response_mime_type": "text/plain",
                    "system_instruction":prompt_text,
                },
            )
        return response.text, 200
    except Exception as e:
        return {"error": str(e)}, 500
    
@app.route("/", methods=["GET", "POST"])
def index():
    response_data = None
    input_text = ""
    if request.method == "POST":
        input_text = request.form.get("input_text", "")
        if input_text:
            response_data = lookup_insert(input_text)
        else:
            response_data = "Please enter some text."
    return render_template("index.html", response=response_data, input_text=input_text)

def lookup_insert(input_text: str) -> list[dict] | str:
    if not input_text.strip():
        # This case should ideally be caught by the caller (e.g., api_vocab)
        return "Input text cannot be empty."

    try:
        raw_vocab_cards: list[VocabCard] | None = query_gemini(input_text)

        if not raw_vocab_cards:
            return "No vocabulary cards were generated by the model."

        generated_files_info: list[dict] = generate_vocabulary_cards(raw_vocab_cards)

        for card_file_info in generated_files_info:
            insert_markdown_file(card_file_info["markdown"], card_file_info["filename"])

        # Convert VocabCard objects to dictionaries for JSON serialization
        # Pydantic V2 uses model_dump(), V1 uses dict(). Assuming V2.
        serializable_cards = [card.model_dump() for card in raw_vocab_cards]
        return serializable_cards
    except ValueError as ve:
        app.logger.error(f"ValueError during vocabulary processing: {ve}", exc_info=True)
        return f"Error processing vocabulary: {str(ve)}"
    except Exception as e:
        app.logger.error(f"Unexpected error in lookup_insert: {e}", exc_info=True)
        return f"An unexpected error occurred. Please check the server logs. Traceback: {e}"
    
if __name__ == "__main__":
    app.run(debug=True)