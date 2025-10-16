from fastapi import APIRouter, Depends
from app.auth.auth import get_current_user
from app.cruds.llmmodel_cruds import create_llmmodel_cruds,get_model_from_name,get_llm_models_crud,get_model_name_crud
from app.schemas.llmmodel_schemas import llmmodel,llmmodelfilter
from app.schemas.response import responsemodel
from app.utils.response import create_response
from app.models.llmmodels_models import llmcompany


router = APIRouter()



@router.post("/create_llmmodel",response_model=responsemodel)
async def create_llmmodel(llmmodel_info:llmmodel,current_user: dict = Depends(get_current_user)):
    try:
        existing_llm_model=await get_model_from_name(llmmodel_info.basemodelname)
        if existing_llm_model:
            return create_response(
                success=False,
                error_message="Model with this base model name already exists",
                status_code=400
            )
        llmmodels=await create_llmmodel_cruds(llmmodel_info)

        return create_response(
            success=True,
            result={"message": "LLM Model created successfully","model_detail":llmmodels},
            status_code=201
            )
    except Exception as e:
        print(e)
        return create_response(
            success=False,
            error_message="Internal Server error during LLM model creation",
            error_detail=str(e),
            status_code=500
            )

@router.get("/get_llm_models",response_model=responsemodel)
async def get_llm_models(llm_filter:llmmodelfilter=Depends(),current_user: dict = Depends(get_current_user)):
    try:
        print("the filter is",llm_filter)
        llm_models=await get_llm_models_crud(llm_filter)
        return create_response(
            success=True,
            result={"message": "LLM Models fetched successfully","models":llm_models},
            status_code=200
            )
    except Exception as e:
        print(e)
        return create_response(
            success=False,
            error_message="Internal Server error during fetching LLM models",
            error_detail=str(e),
            status_code=500
            )
@router.get("/get_model_name",response_model=responsemodel)
async def get_model_name(model_company:llmcompany,current_user:dict=Depends(get_current_user)):
    try:
        llm_models=await get_model_name_crud(model_company)
        return create_response(
            success=True,
            result={"message": "LLM Models Name fetched successfully","models":llm_models},
            status_code=200
            )
    except Exception as e:
        print(e)
        return create_response(
            success=False,
            error_message="Internal Server error during fetching LLM models",
            error_detail=str(e),
            status_code=500
            )
