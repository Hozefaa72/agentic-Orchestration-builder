from pydantic import BaseModel
from typing import Optional
from app.models.steps_model import ConditionRule,TimeOutAction

class Step(BaseModel):

    StepName: str
    StepDescription:Optional[str]=None
    PreviousStep:Optional[str]=None
    NextStep:Optional[str]=None
    AgentID:Optional[str]=None
    canhumanintrupt:Optional[bool]=False
    expectedinput:list[str]
    expectedoutput:list[str]
    ispriorstep:Optional[bool]=False
    validconditions:Optional[list[str]]=None
    isactivestep:Optional[bool]=False
    adminid:Optional[str]=None
    isinitialstep:Optional[bool]=False
    isfinalstep:Optional[bool]=False
    canrollback_agent:Optional[bool]=False
    rollbackstep_agent:Optional[str]=None
    userapprovalrequired:Optional[bool]=True
    adminapprovalrequired:Optional[bool]=False
    conditionmap:Optional[list[ConditionRule]]=None
    approvaltimeoutdays:Optional[int]=7
    timeout_action:Optional[TimeOutAction]=TimeOutAction.ROLLBACK