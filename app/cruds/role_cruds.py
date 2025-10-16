from app.models.role_master import Role
from app.schemas.role_schema import role
from fastapi import HTTPException


async def create_role(role_info: role):
    try:
        roles = Role(
            rolename=role_info.rolename,
            roledescription=role_info.roledescription,
        )
        await roles.insert()
        return roles
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


async def get_role_id(role_name: str):
    try:
        role = await Role.find_one(Role.rolename == role_name)
        role_id = str(role.id)
        return role_id
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


async def get_role_ids_cruds():
    try:
        roles = await Role.find().to_list()
        role_ids = []
        for role in roles:
            a = {}
            a["RoleID"] = role.id
            a["RoleName"] = role.rolename
            role_ids.append(a)
        return role_ids
    except:
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )
