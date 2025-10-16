import json
from bson import ObjectId
from fastapi.responses import JSONResponse
from typing import Any
from app.schemas.response import responsemodel
from datetime import datetime, date

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

def create_response(success: bool,result: Any = None,error_message: str = None,error_detail: str = None,status_code: int = 200,):
    content = responsemodel(success=success,result=result,message=error_message,detail=error_detail,status_code=status_code,).model_dump()
    jsoncontent = json.loads(json.dumps(content, cls=JSONEncoder))
    response = JSONResponse(content=jsoncontent, status_code=status_code)
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response
