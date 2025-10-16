from beanie import Document

class RolePermissionMapping(Document):
    role_id: str
    permission_id: str

    class Settings:
        name = "RolePermissionMapping"
