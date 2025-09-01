from openai import AsyncOpenAI
import json
import chromadb
from app.config import ENV_PROJECT

client_oa = AsyncOpenAI(
    api_key=ENV_PROJECT.OPENAI_API_KEY,
)
chroma_client = chromadb.Client()
collections = {}


async def initialize_chroma():
    def load_json(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    faq_data = load_json("./app/datasets/faq.json")
    clinic_data = load_json("./app/datasets/ivf_clinic.json")
    need_data = load_json("./app/datasets/need.json")

    await store_data("faq", faq_data, "faq.json")
    await store_data("clinic", clinic_data, "ivf_clinic.json")
    await store_data("need", need_data, "need.json")


async def store_data(name, data, source):
    collection = chroma_client.get_or_create_collection(name=name)
    documents, ids = [], []

    # for i, item in enumerate(data):
    #     text = item.get("answer") or item.get("description") or json.dumps(item)
    #     documents.append(text)
    #     ids.append(f"{name}_{i}")
    for i, item in enumerate(data):
        question = item.get("question", "")
        answer = item.get("answer", "") or item.get("description", "")
        if not question and not answer:
            text = json.dumps(item)
        else:
            text = f"Question: {question}\nAnswer: {answer}"
        
        documents.append(text)
        ids.append(f"{name}_{i}")

    embeds = await embed_texts(documents)
    collection.add(documents=documents, embeddings=embeds, ids=ids)

    collections[name] = collection


async def embed_texts(texts):
    batch_size = 100
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = await client_oa.embeddings.create(
            model="text-embedding-3-small", input=batch
        )
        embeddings += [e.embedding for e in response.data]
    return embeddings


async def detect_query_type(question: str) -> str:
    messages = [
        {
            "role": "system",
            "content": "Classify the user question into one of the following: faq, clinic, need.",
        },
        {"role": "user", "content": f"Question: {question}"},
    ]
    response = await client_oa.chat.completions.create(
        model="gpt-4-1106-preview", messages=messages
    )
    answer = response.choices[0].message.content.strip().lower()
    if "clinic" in answer:
        return "clinic"
    elif "faq" in answer:
        return "faq"
    elif "need" in answer:
        return "need"
    return "faq"
