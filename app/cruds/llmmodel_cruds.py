from app.models.llmmodels_models import LLMModel, llmcompany
from app.schemas.llmmodel_schemas import llmmodel
from fastapi import HTTPException
from app.schemas.llmmodel_schemas import llmmodelfilter
from app.utils.config import ENV_PROJECT
from app.core.agents import get_gemini_model_name, get_openai_model_name


async def create_llmmodel_cruds(llmmodel_info: llmmodel):
    try:
        llmmodels = LLMModel(
            llmcompanyname=llmmodel_info.llmcompanyname,
            basemodelname=llmmodel_info.basemodelname,
            llmapikey=llmmodel_info.llmapikey,
            model_type=llmmodel_info.model_type.value,
            isapiexpired=llmmodel_info.isapiexpired,
            tokenused=llmmodel_info.tokenused,
        )
        await llmmodels.insert()
        return llmmodels
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


async def get_model_from_name(basemodelname: str):
    try:
        model = await LLMModel.find_one(LLMModel.basemodelname == basemodelname)
        return model
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


async def get_llm_models_crud(llm_filter: llmmodelfilter):
    try:
        query = {}
        if llm_filter.llmcompanyname:
            query["llmcompanyname"] = llm_filter.llmcompanyname.value
        if llm_filter.model_type:
            query["model_type"] = llm_filter.model_type.value

        models = await LLMModel.find(query).to_list()
        return models
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


async def get_model_name_crud(model_comapny: llmcompany):
    if model_comapny == llmcompany.GoogleGemini:
        model = await get_gemini_model_name()
    elif model_comapny == llmcompany.OpenAI:
        model = get_openai_model_name()
    return model
