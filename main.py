import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import re

MCP_URL = "http://localhost:8000"


# LOCAL MEMORY

local_memory = []

def save_memory_mcp(text):
    try:
        requests.post(f"{MCP_URL}/memory/add", params={"text": text})
    except:
        pass


# ML INTENT CLASSIFIER

train_texts = [
    "hello",
    "hi",
    "what is artificial intelligence",
    "what is machine learning",
    "what is ai",
    "tell me about neural networks",
    "compare iphone and samsung",
    "compare two products",
    "plan my day",
    "plan my schedule",
    "latest news"
]

train_labels = [
    "chat",
    "chat",
    "define",
    "define",
    "define",
    "define",
    "compare",
    "compare",
    "plan",
    "plan",
    "chat"
]

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(train_texts)

model = LogisticRegression()
model.fit(X, train_labels)

def predict_intent(text):
    probs = model.predict_proba(vectorizer.transform([text]))[0]
    max_prob = max(probs)
    intent = model.classes_[probs.argmax()]
    return intent, max_prob



# MCP TOOL CALLS

def call_tool(intent):
    try:
        r = requests.post(
            f"{MCP_URL}/tools/respond",
            params={"intent": intent}
        )
        return r.json().get("result", "")
    except:
        return "Tool call failed."

def get_definition(question):
    topic = question.lower().strip()

    # Remove common prefixes
    for prefix in ["what is", "who is", "explain", "define", "tell me about"]:
        if topic.startswith(prefix):
            topic = topic.replace(prefix, "", 1).strip()

    # Remove punctuation
    topic = re.sub(r"[^\w\s]", "", topic)

    # Handle known aliases (VERY IMPORTANT)
    alias_map = {
        "transformers": "Transformer_(machine_learning)",
        "transformer": "Transformer_(machine_learning)",
        "ai": "Artificial_intelligence",
        "ml": "Machine_learning"
    }

    topic = alias_map.get(topic, topic.replace(" ", "_"))

    try:
        r = requests.get(
            f"{MCP_URL}/tools/wiki",
            params={"topic": topic},
            timeout=5
        )
        return r.json().get("result", "")
    except:
        return ""


def looks_like_definition(text):
    triggers = [
        "what is",
        "who is",
        "define",
        "explain",
        "tell me about"
    ]
    return any(text.startswith(t) for t in triggers)


# AGENT LOGIC

def agent(user_input):
    intent, confidence = predict_intent(user_input)
    text = user_input.lower().strip()

    local_memory.append(user_input)
    save_memory_mcp(user_input)

    # RULE-BASED GENERALIZATION (UNSEEN QUESTIONS)
    if looks_like_definition(text):
        answer = get_definition(user_input)
        if answer:
            return answer
        return "I tried to fetch information, but couldn't find a reliable source."

    # ML-BASED ROUTING
    if intent == "chat":
        return "Hello! You can ask me to explain, compare, or plan."

    if intent in ["compare", "plan"]:
        return call_tool(intent)

    # CONFIDENCE FALLBACK
    if confidence < 0.4:
        return "I'm not fully sure, but I can try to research this if you rephrase."

    return "I'm not sure how to handle that request."





# CHAT LOOP

if __name__ == "__main__":
    print("Agent started. Type 'exit' to quit.\n")

    while True:
        msg = input("You: ")

        if msg.lower() == "exit":
            break

        print("Bot:", agent(msg))

