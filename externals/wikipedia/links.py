import json
from typing import Any
from pathlib import Path
from fsl_openai import start_openai, upload_json_openai, prompt_openai

# Whether to call into OpenAI API
openai = True

# Controling during development
control = False
control_group = [
        "pe:Java",
#        "pe:Haskell",
#        "te:Reasoner",
    ]

# Some params
contexts_folder = "../../queries/entities/contexts"
prompts_folder = "links"
contexts_folder = Path(contexts_folder).expanduser().resolve()
prompts_folder = Path(prompts_folder).expanduser().resolve()
template = Path("links.prompt.template").read_text(encoding="utf-8")
ontology_link = "https://github.com/softlang/fsl/tree/main/ontologies"

# Model configuration
config = {
#   "model": "gpt-5.6-terra",
   "model": "gpt-5.6-luna",
#    "model": "gpt-5-nano",
    "reasoning": {"effort": "medium"},
    "tools": [
        {
            "type": "web_search",
            "filters": {
                "allowed_domains": [
                    "en.wikipedia.org",
                    "github.com"
                    ]
                }
        }
        ],
#    "tool_choice": "required"
    "tool_choice": "auto"
  }

# Create an OpenAI client
client = start_openai() if openai else None

import json
from typing import Any

# Helpers for OpenAI response validation (keys)
VALID_ASSESSMENTS = {"support", "replace", "resolve"}
VALID_PREDICATES = {"foaf:isPrimaryTopicOf", "foaf:page"}


# Helper for OpenAI response validation (link format)
def _is_link(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and set(value) == {"predicate", "url"}
        and value["predicate"] in VALID_PREDICATES
        and isinstance(value["url"], str)
    )

# OpenAI response validation
def check_response(data: Any, resource: str) -> bool:
    if not isinstance(data, dict):
        return False
    if data.get("resource") != resource:
        return False
    assessment = data.get("assessment")
    if assessment not in VALID_ASSESSMENTS:
        return False
    expected_keys = {"resource", "assessment", "links_found"}
    if assessment != "support":
        expected_keys.add("link_proposed")
    if set(data) != expected_keys:
        return False
    links_found = data["links_found"]
    if not isinstance(links_found, list):
        return False
    if not all(_is_link(link) for link in links_found):
        return False
    if assessment != "support" and not _is_link(data["link_proposed"]):
        return False
    valid_count = {
        "support": len(links_found) == 1,
        "replace": len(links_found) >= 1,
        "resolve": len(links_found) == 0,
        }
    if not valid_count[assessment]:
        return False
    return True

# Count API calls
api_calls = 0
max_api_calls = 100

# Create and run all prompts
for context_file in sorted(
    contexts_folder.rglob("*.json"),
    key=lambda path: path.name.casefold(),
):
    if api_calls >= max_api_calls:
        print("Exhausted OpenAI API calls for this script; use restart to continue.")
        quit()

    # Read context file to validate format
    with context_file.open("r", encoding="utf-8") as file:
        context = json.load(file)
        resource = context["resource"]
    
    # Be very selective in control mode
    if control and resource not in control_group:
        continue
    
    # Instantiate template
    prompt = template.format(
        ontology=ontology_link,
        resource=resource,
    )

    # Create prompt file, but don't bother to overwrite
    relative_path = context_file.relative_to(contexts_folder)
    prompt_file = (prompts_folder / relative_path).with_suffix(".prompt")
    if not prompt_file.is_file():
        prompt_file.parent.mkdir(parents=True, exist_ok=True)
        prompt_file.write_text(
            prompt,
            encoding="utf-8",
            )

    # Get response, but only if there is no stored response yet
    response_file = (prompts_folder / relative_path).with_suffix(".response")
    if not response_file.is_file():
        print("Prompting `{resource}`.".format(resource=resource))
        context_file_uploadid = upload_json_openai(client, context_file) if openai else None
        content = [
            { "type": "input_file", "file_id": context_file_uploadid },
            { "type": "input_text", "text": prompt }
        ]
        if openai:
            response_text = prompt_openai(client, config, content)
            api_calls += 1
        else:
            response_text = None
        try:
            data = json.loads(response_text) if openai else {}
        except (json.JSONDecodeError, TypeError):
            print("response_text: " + response_text)
            raise
        if openai:
            with response_file.open("w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            assert check_response(data, resource), "Response format error for resource `" + resource + "`" 
