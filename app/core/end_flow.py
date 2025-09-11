from app.models.threads import Thread
from bson import ObjectId
from app.core.boto3client import bot_generate
import json


async def end_flow(
    thread_id: str, language: str
):
   
    thread_obj_id = ObjectId(thread_id)
    thread = await Thread.find_one(Thread.id == thread_obj_id)

    messages = ["I understand your query, but I can only help with topics related to fertility, IVF, and Indira IVF services",
        {"first_text":"For more specific information, please connect with our call center between 9 AM and 6 PM.","second_text":"CUSTOMER CARE NUMBER","phone_number":"1800 3092429"},
        "Hope this helps! You can come back anytime to explore  or get more info"
    ]

    prompt=f"""You are a helpful assistant. 
Your only task is to respond with {messages}
translated into user language - {language}.
the first and second text in dictionary should also be translated

Return the result strictly as a JSON list of strings,  
keeping the same number of items as input.


Output Format Example:
["<translated message 1>","dict","<translated message 3>"] """
    response= await bot_generate(prompt,500)
    thread.flow_id=None
    thread.step_id=None
    await thread.save()
    try:
        answer = json.loads(response)  # will give list
    except:
        answer = [response] 
    return answer



