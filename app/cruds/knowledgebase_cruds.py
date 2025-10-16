from app.models.knowledgebase_model import KnowledgeBase
from app.schemas.knowledgebase_schema import knowledgebase
from fastapi import HTTPException
from bson import ObjectId


async def create_knowledge_base_cruds(knowledgebase_info: knowledgebase):
    try:
        kb = KnowledgeBase(
            KBName=knowledgebase_info.KBName,
            KBDecription=knowledgebase_info.KBDecription,
            KBEmbeddingModelcompany=knowledgebase_info.KBEmbeddingModelcompany.value,
            KBEmbeddingModelname=knowledgebase_info.KBEmbeddingModelname,
            KBMetadata=knowledgebase_info.KBMetadata,
            chunksize=knowledgebase_info.chunksize,
            chunkoverlap=knowledgebase_info.chunkoverlap,
        )
        await kb.insert()
        return kb
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


async def save_kb_file_path(file_paths: list, knowledge_base_id: str):
    try:
        knowledge_base_id = ObjectId(knowledge_base_id)
        kb = await KnowledgeBase.find_one(KnowledgeBase.id == knowledge_base_id)
        if not kb:
            raise HTTPException(
                status_code=404,
                detail="Knowledge Base not found",
            )
        kb.KbFilename = file_paths
        await kb.save()
        return kb
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


async def get_admin_kb(kb_ids: list):
    try:
        kbs = []
        if kb_ids:
            for kb_id in kb_ids:
                kb = await KnowledgeBase.find_one(KnowledgeBase.id == ObjectId(kb_id))
                if not kb:
                    raise HTTPException(
                        status_code=404,
                        detail="Agent not found",
                    )
                kbs.append(kb)
        return kbs
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )
