from app.models.agents_model import Agents
from app.core.kbSetUP import get_context_from_knowledge_base
from app.models.llmmodels_models import llmcompany, LLMModel
from bson import ObjectId
from openai import OpenAI
from google import genai
from app.utils.config import ENV_PROJECT
from typing import Any


async def get_gemini_model_name():
    client = genai.Client(api_key=ENV_PROJECT.GEMINI_API_KEY)
    model_names = []
    async for model in await client.aio.models.list():
        if "generateContent" in getattr(model, "supported_actions", []):
            cleaned_models = model.name.split("/")[-1]
            model_names.append(cleaned_models)
    return model_names


async def get_openai_model_name():
    client = OpenAI(api_key=ENV_PROJECT.OPENAI_API_KEY)
    models = client.models.list()
    model_names = []
    for model in models:
        model_names.append(model.id)
    return model_names


async def get_gemini_answers(api_key, prompt, model_name):
    client = genai.Client(api_key=api_key)

    print(model_name)
    response = client.models.generate_content(model=model_name, contents=prompt)
    answer = response.candidates[0].content.parts[0].text
    print("the answser is", answer)
    # async for job in await client.aio.models.list():
    #     print(job)
    return answer


async def get_openai_response(api_key, model, prompt, max_tokens, temperature):
    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a validation assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        answer = response.choices[0].message.content.strip()
        usage = response.usage
        step_total = usage.total_tokens
        return answer
    except Exception as e:
        print(f"[OpenAI Error]: {e}")
        return None, 0


async def get_response_from_agent(
    agent_id, user_input: Any, expected_input=None, expected_output=None
):
    agent = await Agents.find_one(Agents.id == ObjectId(agent_id))
    context = ""
    if isinstance(agent.agentKBID, list):
        if len(agent.agentKBID) != 0:
            for kbid in agent.agentKBID:
                context += await get_context_from_knowledge_base(kbid, user_input)
    print("the context is ", context)

    if expected_input:
        exp = ""
        for e in expected_input:
            exp += e
        out = ""
        for e in expected_output:
            out += e
        prompt = (
            agent.agentPrompt
            + "The Expected Input should be "
            + exp
            + "and the expected_output is"
            + out
        )
    else:
        prompt = agent.agentPrompt
    llm = await LLMModel.find_one(
        LLMModel.llmcompanyname == agent.agentLLMModelcompany,
        LLMModel.basemodelname == agent.agentLLMModelname,
    )
    if agent.agentLLMModelcompany == llmcompany.OpenAI:
        prompt = (
            prompt
            + "The context from knowledge base is "
            + context
            + "the question by the user is"
            + user_input
        )
        response = await get_openai_response(
            llm.llmapikey, llm.agentLLMModelname, prompt, 500, 0
        )
    elif agent.agentLLMModelcompany == llmcompany.GoogleGemini:
        prompt = (
            prompt
            + "The context from knowledge base is "
            + context
            + "the question by the user is"
            + user_input
        )
        response = await get_gemini_answers(
            llm.llmapikey, prompt, agent.agentLLMModelname
        )
    return response


async def generate_agent_approval(content: Any, expectedoutput, valid_condition):
    client = OpenAI(api_key=ENV_PROJECT.OPENAI_API_KEY)
    prompt = """You are a Validation Agent.
                Your only job is to decide whether the given response is valid (True) or invalid (False) based on the expected output and valid conditions.
                
                Inputs
                {content}: This is the actual output received from the process or model.
                {expectedoutput}: This is the ideal or correct result the response should match or satisfy.
                {valid_condition}: this is the textual or logical condition describing what makes the response valid.

                Task
                Compare the response with the expected_output and evaluate whether it satisfies the valid_condition.
                Do not provide reasoning or explanation — only return a boolean:
                    Return True → if the response is valid.
                    Return False → if the response is invalid.
                Output Format
                Return only from these two either: True or False
            """
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": "You are a validation assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=10,
        temperature=0,
    )
    answer = response.choices[0].message.content.strip()
    return answer
