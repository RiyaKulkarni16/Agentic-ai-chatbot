from fastapi import FastAPI
import requests

app = FastAPI()


# SIMPLE MEMORY

memory = []

@app.post("/memory/add")
def add_memory(text: str):
    memory.append(text)
    return {"status": "saved"}

@app.get("/memory/get")
def get_memory():
    return {"memory": memory}


# SIMPLE TOOL RESPONSES

@app.post("/tools/respond")
def tool_router(intent: str):
    if intent == "compare":
        return {
            "result": "Comparison: Product A focuses on performance, Product B on cost."
        }

    if intent == "plan":
        return {
            "result": "Step 1: Define goal\nStep 2: Break into tasks\nStep 3: Execute"
        }

    return {"result": "Intent recognized, but no action needed."}


# AUTO-GENERATION TOOL 

@app.get("/tools/wiki")
def wiki_summary(topic: str):
    try:
        url = "https://en.wikipedia.org/w/api.php"

        params = {
            "action": "query",
            "format": "json",
            "prop": "extracts",
            "exintro": True,
            "explaintext": True,
            "titles": topic
        }

        headers = {
            "User-Agent": "AgenticAI-Bot/1.0"
        }

        r = requests.get(url, params=params, headers=headers, timeout=5)

        pages = r.json()["query"]["pages"]
        page = next(iter(pages.values()))

        if "extract" not in page:
            return {"result": "No information found for this topic."}

        return {"result": page["extract"]}

    except Exception as e:
        return {"result": f"Failed to fetch information: {str(e)}"}
