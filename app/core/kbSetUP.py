from langchain_community.document_loaders import JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from app.utils.config import ENV_PROJECT

vectorstore=None

def get_vectorstore():
    global vectorstore
    if vectorstore is None:
        raise RuntimeError("Vectorstore not initialized yet")
    return vectorstore

async def KBSetup():
    # JSON (you need to tell which field to extract)
    global vectorstore
    json_loader = JSONLoader(
        file_path="app/datasets/faq.json",
        jq_schema=".[] | {text: (.question + \"\\n\" + .answer)}",  # adjust depending on your JSON structure
        content_key="text" 
    )
    json_docs = json_loader.load()

    if not json_docs:
        raise ValueError("No documents loaded! Check your jq_schema or JSON structure.")

    text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
    )
    docs = text_splitter.split_documents(json_docs)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small",api_key=ENV_PROJECT.OPENAI_API_KEY)

# Store in ChromaDB
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory="chroma_db"  # folder to save
    )
