# from langchain.prompts import PromptTemplate
# from langchain.chains.retrieval import create_retrieval_chain
# from langchain_openai import ChatOpenAI
# from app.core.kbSetUP import get_vectorstore
# from app.utils.config import ENV_PROJECT


# async def FAQFlow(user_message: str, language: str):

#     vectorstore = get_vectorstore()
#     custom_prompt = PromptTemplate(
#         template="""
# You are a helpful IVF assistant. Use the following context to answer the question.

# Instructions:
# - Preserve the grammatical style and phrasing of the knowledge base.
# - Summarize your answer in 10-50 words.
# - Answer in the following language: {language}

# Context:
# {context}

# Question:
# {question}

# Answer:""",
#         input_variables=["context", "question", "language"]
#     )

#     llm = ChatOpenAI(model="gpt-4.1-nano",openai_api_key=ENV_PROJECT.OPENAI_API_KEY)

#     qa_chain = RetrievalQAWithSourcesChain(
#         llm=llm,
#         retriever=vectorstore.as_retriever(),
#         chain_type="stuff",
#         chain_type_kwargs={"prompt": custom_prompt}
#     )

#     response = qa_chain.run({"question": user_message, "language": language})
#     return response
# from langchain.prompts import PromptTemplate
# from langchain.chains.retrieval import create_retrieval_chain
# from langchain_openai import ChatOpenAI
# from langchain.chains.combine_documents import create_stuff_documents_chain
# from app.core.kbSetUP import get_vectorstore
# from app.utils.config import ENV_PROJECT
# import json


# async def FAQFlow(user_message: str, language: str):
#     print("in faq flow")
#     # Get vectorstore retriever
#     vectorstore = get_vectorstore()
#     retriever = vectorstore.as_retriever()
#     messages = ["I understand your query, but is there any anything else you want to know",
#             {"first_text":"For more specific information, please connect with our call center between 9 AM and 6 PM.","second_text":"CUSTOMER CARE NUMBER","phone_number":"1800 3092429"},
#             "Hope this helps! You can come back anytime to explore  or get more info"
#         ]

#     # Define custom prompt
#     custom_prompt = PromptTemplate(
#     template="""
# You are a helpful IVF assistant. Use the following context to answer the question.

# Instructions:
# - Preserve the grammatical style and phrasing of the knowledge base.
# - Summarize your answer in 10-50 words.
# - Answer in the following language: {language}
# - if you don't find the answer then return {another_message} in the same structure with translated language not the number

# Context:
# {context}

# Question:
# {input}

# Answer:(as JSON): """,
#     input_variables=["context", "input", "language","another_message"]
# )

#     # Initialize LLM
#     llm = ChatOpenAI(
#         model="gpt-4.1-nano",
#         openai_api_key=ENV_PROJECT.OPENAI_API_KEY
#     )

#     # Step 1: Create a document-combining chain (stuff = simple concatenation)
#     combine_docs_chain = create_stuff_documents_chain(
#         llm=llm,
#         prompt=custom_prompt
#     )

#     # Step 2: Create retrieval chain
#     qa_chain = create_retrieval_chain(
#     retriever=retriever,
#     combine_docs_chain=combine_docs_chain
# )

#     # Run the chain
#     response = await qa_chain.ainvoke({
#         "input": user_message,
#         "language": language,
#         "another_message":messages
#     })
#     try:
#         answer_list = json.loads(response["answer"])
#     except:
#         answer_list=[response["answer"]]
#     print(answer_list)

#     return answer_list


# async def query_vectorstore(query: str, k: int = 3):
#     vs = get_vectorstore()
#     results = vs.similarity_search(query, k=k)
#     if not results:
#         return None
#     return results

from app.core.boto3client import bot_generate
from app.core.kbSetUP import get_vectorstore
import ast
from langchain_openai import OpenAIEmbeddings
from app.utils.config import ENV_PROJECT

async def FAQFlow(user_message: str, language: str,context=None):
    if not(context):
        context= await query_vectorstore(user_message)
    messages = ["I understand your query, but is there any anything else you want to know",
            {"first_text":"For more specific information, please connect with our call center between 9 AM and 6 PM.","second_text":"CUSTOMER CARE NUMBER","phone_number":"1800 3092429"},
            "Hope this helps! You can come back anytime to explore  or get more info"
        ]
    
    
    if isinstance(context, list):
        seen = set()
        unique_docs = []
        for doc in context:
            if doc.page_content not in seen:
                seen.add(doc.page_content)
                unique_docs.append(doc.page_content)
        context_text = " ".join(unique_docs)
    else:
        context_text = context
    print("context i'm sending",context_text)
    prompt = f"""
You are a helpful IVF assistant. Use the following context to answer the question.

Instructions:
Step 1: Translate the question into English.
- Preserve the grammatical style and phrasing of the knowledge base.
- Summarize your answer in 10-50 words.
- Answer in the following language: {language}
-i'm giving you {context_text} if you find the context right understand the semantic of context and try to find the answer in context for the question (question can be in any language try to translate question and then check with context) asked by user then return the answer based on the context and don't send anything else from the invalid message list.
- If you don't find the answer, return the following JSON exactly as-is (do not change structure or numbers): {messages} do not return this in string it should be in list and translate it into this {language}
-Strict Rule-don't merge both either the invalid message in which you will return list or either the answer regarding the context 


Question:
{user_message}

Answer (as JSON): 
"""
    answer = await bot_generate(prompt, 500)
    print(answer)

    try:
            # Try evaluating the string to an actual list
        answer = ast.literal_eval(answer)  # Safely evaluate the string to a list
    except (ValueError, SyntaxError) as e:
            print("Error evaluating the string to a list:", e)
            answer = [answer]

    print("Bedrock Response:", type(answer))
    return answer


# Optional helper function
async def query_vectorstore(query: str, k: int = 5):
    vs = get_vectorstore()
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small",api_key=ENV_PROJECT.OPENAI_API_KEY)
    results = vs.similarity_search_by_vector(embedding=embeddings.embed_query(query),k=k)
    if not results:
        return None
    return results
