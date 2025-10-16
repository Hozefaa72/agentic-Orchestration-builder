from fastapi import APIRouter,Depends,UploadFile, File,Form
from app.auth.auth import get_current_user
from app.schemas.knowledgebase_schema import knowledgebase
from app.schemas.response import responsemodel
from app.utils.response import create_response
from app.utils.config import ENV_PROJECT
import os
from app.cruds.knowledgebase_cruds import create_knowledge_base_cruds,save_kb_file_path,get_admin_kb
import json
from app.core.kbSetUP import KBSetup,get_context_from_knowledge_base
from app.cruds.permission_cruds import get_permission_id_crud
from app.cruds.rolepermissionmapping_cruds import has_permission
from app.cruds.user_cruds import add_knowledgebase_to_user_cruds,get_user_role_id_cruds,get_user_by_id
from app.cruds.orchestration_cruds import add_kbid_orchestration
router = APIRouter()



@router.post("/create_knowledgebase",response_model=responsemodel)
async def create_knowledge_base(knowledge_base: str = Form(...),knowledge_base_file:list[UploadFile]=File(...),current_user: dict = Depends(get_current_user)):
    try:
        print("i'm inside the api")
        user_id=current_user.get("user_id")
        orchestration_id=current_user.get("orchestration_id")
        print("user_id",user_id)
        role_id=await get_user_role_id_cruds(user_id)
        print("role id")
        permission_id=await get_permission_id_crud("Create Knowledge Base")
        print("permission id",permission_id)
        if await has_permission(role_id,permission_id):
            print("permission granted")
            kb_data = json.loads(knowledge_base)
            kb_model = knowledgebase(**kb_data)
            kb=await create_knowledge_base_cruds(kb_model)
            if orchestration_id:
                await add_kbid_orchestration(orchestration_id,kb.id)

            print(f"ENV_PROJECT.UPLOAD_DIR/{str(kb.id)}")
            os.makedirs(f"{ENV_PROJECT.UPLOAD_DIR}/{str(kb.id)}", exist_ok=True)
            saved_paths = []

            for file in knowledge_base_file:
                file_path = os.path.join(f"{ENV_PROJECT.UPLOAD_DIR}/{str(kb.id)}", file.filename)
                with open(file_path, "wb") as f:
                    f.write(await file.read())
                saved_paths.append(file_path)
            await KBSetup(kb,saved_paths)
            kb=await save_kb_file_path(saved_paths,str(kb.id))
            await add_knowledgebase_to_user_cruds(str(kb.id),user_id)
            print("everything is done")

            return create_response(
                success=True,
                result={"message":"Knowledge Base created successfully","knowledge_base": kb},
                status_code=201
                )
        else:
            return create_response(
                success=False,
                error_message="You do not have permission to create knowledge base",
                status_code=403
                )
    except Exception as e:
        print(e)
        return create_response(
            success=False,
            error_message="Internal Server error during agent creation",
            error_detail=str(e),
            status_code=500
            )
    
@router.get("/get_knowledge_base",response_model=responsemodel)
async def get_knowledge_base(current_user:dict=Depends(get_current_user)):
    try:
        user_id=current_user.get("user_id")
        role_id=await get_user_role_id_cruds(user_id)
        print(role_id)
        permission_id=await get_permission_id_crud("Get Knowledge Base")
        if await has_permission(role_id,permission_id):
            user=await get_user_by_id(user_id)
            kb=await get_admin_kb(user.knowledgebase_id)
            
            return create_response(
                    success=True,
                    result={"knowledge_base": kb},
                    status_code=201
                    )
        else:
                return create_response(
                    success=False,
                    error_message="You do not have permission to get knowledge base",
                    status_code=403
                    )
    except Exception as e:
        print(e)
        return create_response(
            success=False,
            error_message="Internal Server error during getting knowledge base",
            error_detail=str(e),
            status_code=500
            )


@router.get("/get_context_from_kb",response_model=responsemodel)
async def get_answer_from_knowledge_base(kbid:str,user_question:str,current_user:dict=Depends(get_current_user)):
    try:

        context=await get_context_from_knowledge_base(kbid,user_question)
            
        return create_response(
                    success=True,
                    result={"Context": context},
                    status_code=201
                    )

    except Exception as e:
        print(e)
        return create_response(
            success=False,
            error_message="Internal Server error during getting knowledge base",
            error_detail=str(e),
            status_code=500
            )

