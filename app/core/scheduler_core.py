from datetime import datetime, timezone, timedelta
from app.models.orchestration_instace import OrchestrationInstance, StepsStatus
from app.models.steps_model import Steps, TimeOutAction
from app.models.users import User
from bson import ObjectId
from app.auth.jwt_handler import generate_approval_token
from app.core.email_send import send_approval_email
from app.utils.config import ENV_PROJECT


async def check_step_timeouts():
    now = datetime.now(timezone.utc)
    pending_steps = await OrchestrationInstance.find(
        OrchestrationInstance.status == StepsStatus.PENDING
    ).to_list()
    for step in pending_steps:
        timeo = await Steps.find_one(Steps.id == ObjectId(step.currentstep))
        if step.approvalsentat and timeo.approvaltimeoutdays:
            expiry = step.approvalsentat + timedelta(days=step.approvaltimeoutdays)
            if now > expiry:
                if (
                    timeo.timeoutaction == TimeOutAction.ROLLBACK
                    and timeo.conditionmap.rollback_step
                ):
                    step.status = StepsStatus.FAILED
                    step.currentstep = timeo.conditionmap.rollback_step
                    step.previousstep = step.currentstep
                    await step.save()
                elif timeo.timeoutaction == TimeOutAction.NOTIFY:
                    admin = await User.find_one(User.id == ObjectId(timeo.adminid))
                    user = await User.find_one(User.id == ObjectId(step.user_id))
                    token = await generate_approval_token(
                        step.orchestration_id,
                        step.currentstep,
                        step.user_id,
                        timeo.approvaltimeoutdays,
                        ENV_PROJECT.EMAIL_SECRET_KEY,
                    )
                    await send_approval_email(
                        user.email, token, step.stepoutput, timeo.expectedoutput
                    )
                elif timeo.timeoutaction == TimeOutAction.SKIP:
                    step.status = StepsStatus.COMPLETED
                    if not (timeo.isfinalstep):
                        step.currentstep = timeo.NextStep
                    else:
                        step.currentstep = None
                    step.previousstep = step.currentstep
                    await step.save()
                else:
                    step.status = StepsStatus.FAILED
                    step.currentstep = None
                    await step.save()
