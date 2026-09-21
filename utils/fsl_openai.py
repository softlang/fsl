from dotenv import load_dotenv
from openai import OpenAI

# Load the .gitignore-d OpenAI API key
load_dotenv()

# Create an OpenAI client/session
def start_openai():
    return OpenAI()

# Upload a JSON file to OpenAI
def upload_json_openai(client, filename):
    uploaded = client.files.create(
        file=open(filename, "rb"),
        purpose="user_data"
    )
    return uploaded.id

# Prompt OpenAI
def prompt_openai(client, config, content):
    response = client.responses.create(
        model=config["model"],
        reasoning=config["reasoning"],
        tools=config["tools"],
        tool_choice=config["tool_choice"],
        input=[{
            "role": "user",
            "content": content
        }])
    return response.output_text
