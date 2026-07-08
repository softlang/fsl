import re
import json
import ollama

# -----------------------------------
# Extract JSON from LLM output
# -----------------------------------

def safe_parse_llm_output(raw):
    try:
        return json.loads(raw)

    except:
        match = re.search(r"\{.*\}", raw, re.DOTALL)

        if match:
            try:
                return json.loads(match.group(0))
            except:
                return {
                    "error": "invalid_json",
                    "raw": raw
                }

        return {
            "error": "no_json_found",
            "raw": raw
        }


# -----------------------------------
# Files containing SHACL violations
# -----------------------------------

from pathlib import Path

files = sorted(Path("results").glob("*.txt"))

if not files:
    raise FileNotFoundError("No validation reports found in results/")
# -----------------------------------
# Parse SHACL report
# -----------------------------------

def parse(report):

    focus = re.search(r"Focus Node:\s*(.*)", report)

    message = re.search(
        r'sh:message Literal\("(.*?)"\)',
        report,
        re.DOTALL
    )

    shape = re.search(
        r"Source Shape:\s*(.*)",
        report
    )

    return {
        "focus_node": focus.group(1) if focus else None,
        "message": message.group(1) if message else None,
        "shape": shape.group(1) if shape else None
    }


# -----------------------------------
# Ask LLM
# -----------------------------------

def explain_with_llm(v):

    prompt = f"""
You are an ontology validation assistant.

You MUST return ONLY valid JSON.

Focus Node: {v['focus_node']}
Shape: {v['shape']}
Message: {v['message']}

Return ONLY valid JSON.

Rules:
- Do NOT include markdown
- Do NOT include explanations outside JSON
- fix_rdf must contain Turtle RDF
- Do NOT return JSON inside fix_rdf

Format:

{{
  "focus_node": "...",
  "shape": "...",
  "issue": "...",
  "why_it_matters": "...",
  "fix_rdf": "..."
}}
"""

    response = ollama.chat(
        model="llama3.1",
        messages=[
            {
                "role": "system",
                "content": "Return only valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


# -----------------------------------
# Quality checks
# -----------------------------------

def evaluate_output(parsed):

    warnings = []

    fix = parsed.get("fix_rdf", "")
    if fix.startswith("'") or fix.endswith("'"):
       warnings.append(
       	   "Fix RDF wrapped in quotes"
       )

    if "rdf:type ve:Class" in fix:
        warnings.append(
          "Fix recreates class instead of modifying existing class"
        )

    if fix.startswith("http://"):
       warnings.append(
           "Subject URI missing angle brackets"
       )

    if "<:" in fix:
        warnings.append(
            "Invalid Turtle syntax detected (<:Entity)"
        )

    if "example.org" in fix:
        warnings.append(
            "Placeholder URI detected"
        )

    if parsed.get("why_it_matters", "") == "":
        warnings.append(
            "Empty explanation"
        )

    if fix == "":
        warnings.append(
            "Missing RDF fix"
        )

    return warnings


# -----------------------------------
# Main execution
# -----------------------------------

results = []

for file in files:

    print("\n==============================")

    report = open(file).read()

    v = parse(report)

    print("\nParsed:")
    print(v)

    # -------------------------------
    # Skip incomplete SHACL reports
    # -------------------------------
    if not all([v["focus_node"], v["shape"], v["message"]]):

        print("\nSkipping incomplete validation report.")

        results.append({
            "file": str(file),
            "parsed_violation": v,
            "llm_output": None,
            "warnings": ["Incomplete SHACL report"]
        })

        continue

    # -------------------------------
    # Call the LLM only for valid reports
    # -------------------------------
    # -------------------------------
    # Call the LLM only for valid reports
    # -------------------------------
    raw = explain_with_llm(v)

    parsed = safe_parse_llm_output(raw)

    if "error" in parsed:
        warnings = [
            f"LLM parsing failed ({parsed['error']})"
        ]
    else:
        warnings = evaluate_output(parsed)

    print("\nLLM Output:\n")
    print(json.dumps(parsed, indent=2))

    if warnings:

        print("\nWarnings:")

        for w in warnings:
            print("-", w)

    else:
        print("\nNo warnings detected.")

    results.append({
        "file": str(file),
        "parsed_violation": v,
        "llm_output": parsed,
        "warnings": warnings
	
    })
# -----------------------------------
# Save results
# -----------------------------------

with open("results_output.json", "w") as f:
    json.dump(results, f, indent=2)

print("\n====================================")
print("Results saved to results_output.json")
print("====================================")
