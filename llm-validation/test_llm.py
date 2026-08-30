import ollama

resp = ollama.chat(
    model="llama3.1",
    messages=[
        {"role": "user", "content": "Explain SHACL in 1 sentence"}
    ]
)

print(resp["message"]["content"])
