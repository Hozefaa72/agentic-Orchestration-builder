from app.models.role_permission_model import RolePermissionMapping
from app.schemas.role_permission_schema import rolepermissionmapping
from fastapi import HTTPException


async def create_rolePermissionMapping_cruds(mapping_info: rolepermissionmapping):
    try:
        mapping = RolePermissionMapping(
            role_id=mapping_info.role_id,
            permission_id=mapping_info.permission_id,
        )
        await mapping.insert()
        return mapping
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


async def has_permission(role_id: str, permission_id: str):
    try:
        mapping = await RolePermissionMapping.find_one(
            RolePermissionMapping.role_id == role_id,
            RolePermissionMapping.permission_id == permission_id,
        )
        if mapping:
            return True
        return False
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )
