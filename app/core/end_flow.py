from app.models.threads import Thread
from bson import ObjectId
from app.core.boto3client import bot_generate


async def end_flow(
    thread_id: str, language: str
):
   
    thread_obj_id = ObjectId(thread_id)
    thread = await Thread.find_one(Thread.id == thread_obj_id)

    prompt=f"""You are a helpful assistant. 
Your only task is to respond with the exact phrase "Anything else you want to know" 
translated into user language - {language}. """
    response= await bot_generate(prompt,100)
    thread.flow_id=None
    thread.step_id=None
    await thread.save()
    return response



