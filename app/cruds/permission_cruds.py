from app.models.permission_model import Permissions
from app.schemas.permission_schemas import permission
from fastapi import HTTPException


async def create_permission_cruds(permission_info: permission):
    try:
        permissions = Permissions(
            permissionname=permission_info.permissionname,
            description=permission_info.description,
            ispublic=permission_info.ispublic,
        )
        await permissions.insert()
        return permissions
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


async def get_permission_id_crud(permissionname: str):
    try:
        permission = await Permissions.find_one(
            Permissions.permissionname == permissionname
        )
        if not permission:
            raise HTTPException(
                status_code=404,
                detail="Permission not found",
            )
        return str(permission.id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


async def get_permission_ids_cruds():
    try:
        print("in permission cruds")
        roles = await Permissions.find().to_list()
        role_ids = []
        for role in roles:
            a = {}
            a["PermissionName"] = role.permissionname
            a["PermissionID"] = role.id
            role_ids.append(a)
        return role_ids
    except:
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )
