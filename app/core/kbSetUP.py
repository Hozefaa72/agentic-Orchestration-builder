from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredWordDocumentLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.utils.config import ENV_PROJECT
from app.models.llmmodels_models import llmcompany, LLMModel
import chromadb
from chromadb.utils.embedding_functions import (
    GoogleGenerativeAiEmbeddingFunction,
    OpenAIEmbeddingFunction,
)
from fastapi import HTTPException
import json
from langchain.schema import Document
from app.models.knowledgebase_model import KnowledgeBase
from bson import ObjectId


async def extract_text(obj):
    texts = []
    if isinstance(obj, dict):
        for value in obj.values():
            texts.extend(await extract_text(value))
    elif isinstance(obj, list):
        for item in obj:
            texts.extend(await extract_text(item))
    elif isinstance(obj, str):
        texts.append(obj.strip())
    return texts


async def setup_from_json(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    docs = []
    all_texts = await extract_text(data)
    for i, text in enumerate(all_texts):
        if text:
            docs.append(
                Document(page_content=text, metadata={"source": file_path, "index": i})
            )
    return docs


async def setup_from_pdf(file_path):
    loader = PyPDFLoader(file_path)
    return loader.load()


async def setup_from_docx(file_path):
    loader = UnstructuredWordDocumentLoader(file_path)
    return loader.load()


def get_vectorstore():
    global vectorstore
    if vectorstore is None:
        raise RuntimeError("Vectorstore not initialized yet")
    return vectorstore


async def KBSetup(kb, file_paths):
    try:
        global vectorstore
        alldocs = []
        print("the file paths are", file_paths)
        for file_path in file_paths:
            if file_path.endswith(".json"):
                docs = await setup_from_json(file_path)
            elif file_path.endswith(".pdf"):
                docs = await setup_from_pdf(file_path)
            elif file_path.endswith(".docx"):
                docs = await setup_from_docx(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
            alldocs.extend(docs)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        docs = text_splitter.split_documents(alldocs)
        llm = await LLMModel.find_one(
            LLMModel.llmcompanyname == kb.KBEmbeddingModelcompany,
            LLMModel.basemodelname == kb.KBEmbeddingModelname,
        )
        if kb.KBEmbeddingModelcompany == llmcompany.OpenAI:
            embeddings = OpenAIEmbeddingFunction(
                model_name=kb.KBEmbeddingModelname, api_key=llm.llmapikey
            )
        elif kb.KBEmbeddingModelcompany == llmcompany.GoogleGemini:
            embeddings = GoogleGenerativeAiEmbeddingFunction(
                model_name=kb.KBEmbeddingModelname, api_key=llm.llmapikey
            )

        client = chromadb.CloudClient(
            api_key=ENV_PROJECT.CHROMA_DB_KEY,
            tenant=ENV_PROJECT.CHROMA_DB_TENANT,
            database="orchestration",
        )
        if client:
            collection = client.get_or_create_collection(
                name=kb.KBName, embedding_function=embeddings
            )
            documents = [doc.page_content for doc in docs]
            metadata = [
                {"source": doc.metadata.get("source", "unknown")} for doc in docs
            ]
            ids = [str(i) for i in range(len(docs))]
            collection.add(documents=documents, metadatas=metadata, ids=ids)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error setting up knowledge base: {str(e)}"
        )


async def get_context_from_knowledge_base(kbid: str, user_question: str):
    kb = await KnowledgeBase.find_one(KnowledgeBase.id == ObjectId(kbid))
    client = chromadb.CloudClient(
        api_key=ENV_PROJECT.CHROMA_DB_KEY,
        tenant=ENV_PROJECT.CHROMA_DB_TENANT,
        database="orchestration",
    )
    collection = client.get_collection(name=kb.KBName)
    llm = await LLMModel.find_one(
        LLMModel.llmcompanyname == kb.KBEmbeddingModelcompany,
        LLMModel.basemodelname == kb.KBEmbeddingModelname,
    )
    if kb.KBEmbeddingModelcompany == llmcompany.OpenAI:
        embeddings = OpenAIEmbeddingFunction(
            model_name=kb.KBEmbeddingModelname, api_key=llm.llmapikey
        )
    elif kb.KBEmbeddingModelcompany == llmcompany.GoogleGemini:
        embeddings = GoogleGenerativeAiEmbeddingFunction(
            model_name=kb.KBEmbeddingModelname, api_key=llm.llmapikey
        )
    context = collection.query(
        query_embeddings=embeddings([user_question]), n_results=3
    )
    context = context["documents"][0][0]
    print("the context is ", context)
    return context
