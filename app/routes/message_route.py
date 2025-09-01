from fastapi import APIRouter, HTTPException, Depends,status
from app.cruds.message_cruds import create_message, get_all_messages
from app.auth.auth import get_current_user
from pydantic import ValidationError
from app.schemas.message_schemas import MessageCreate
from pymongo.errors import PyMongoError
import boto3
import time
import json
from openai import AsyncOpenAI
from app.config import ENV_PROJECT
from app.core.chroma_db_init import collections
from pydantic import BaseModel
import requests
from geopy.distance import geodesic
from requests.exceptions import RequestException
client = AsyncOpenAI(
    api_key=ENV_PROJECT.OPENAI_API_KEY, default_headers={"OpenAI-Beta": "assistants=v2"}
)

bedrock_client = boto3.client('bedrock-runtime')


# class MessageCreate(BaseModel):
#     content: Union[str, List[str]]
#     sender: str


router = APIRouter()


@router.get("/get_all_messages/")
async def get_all_messages_route(current_user: dict = Depends(get_current_user)):
    try:
        thread_id = current_user["thread_id"]
        if not thread_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Thread ID not found in token",
            )

        messages = await get_all_messages(thread_id)
        return {"messages": messages}

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve messages"
        )


@router.post("/messages/")
async def post_message(
    msg: MessageCreate, current_user: dict = Depends(get_current_user)
):
    try:

        user_id = current_user["thread_id"]
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Thread ID missing in token"
            )

        message = await create_message(
            content=msg.content, sender=msg.sender, thread_id=user_id
        )

        return {"message": "Message created successfully", "data": message}

    except ValidationError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid message data"
        )

    except HTTPException as http_exc:
        raise http_exc

    except PyMongoError as db_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while creating message"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while posting message"
        )
    

# @router.post("/flow_check/")
# async def post_message(
#     question: str, current_user: dict = Depends(get_current_user)
# ):
  



#     # First, check using Chroma for nearby clinics in your dataset
#     response = await client.embeddings.create(
#         model="text-embedding-3-small",
#         input=[question]
#     )
#     question_embedding = response.data[0].embedding
#     collection = collections.get("clinic")
#     print(collection)
#     # Query the vector store (Chroma)
#     results = collection.query(
#         query_embeddings=[question_embedding],
#         n_results=5
#     )

#     context_chunks = results["documents"][0] if results["documents"] else []

#     if not context_chunks:
#         # Use AWS Bedrock NLP model to generate a fallback response
#         response = bedrock_client.invoke_model(
#             modelId="your-bedrock-model-id",
#             body=json.dumps({"query": question})
#         )
        
#         # Return a helpful response if no clinics are found
#         return "Sorry, we couldn't find any nearby clinics. Would you like to try another location?"
    
#     context = "\n---\n".join(context_chunks)
#     body = {
#         "inputText": f"""
# You are a helpful assistant. 
# From the following clinic addresses, select and return only the top 3 nearby clinics in a clean JSON list format.

# Question: {question}
# Clinic Addresses:
# {context}

# Return only JSON in this format:
# {{
#   "nearby_clinics": [
#     "Clinic 1 full address",
#     "Clinic 2 full address",
#     "Clinic 3 full address"
#   ]
# }}
#         """
#     }

#     response = bedrock_client.converse(
#         modelId="anthropic.claude-3-haiku-20240307-v1:0",
#         messages=[{"role": "user", "content": [body["inputText"]]}],
#         inferenceConfig={"maxTokens": 200, "temperature": 0},
#     )

#     # Step 5: Parse response
#     model_output = json.loads(response.get("body").read())
    
#     return model_output

# @router.post("/flow_check/")
# async def post_message(
#     question: str, current_user: dict = Depends(get_current_user)
# ):
#     # First, check using Chroma for nearby clinics in your dataset
#     response = await client.embeddings.create(
#         model="text-embedding-3-small",
#         input=[question]
#     )
#     question_embedding = response.data[0].embedding
#     collection = collections.get("clinic")
#     print(collection)
    
#     # Query the vector store (Chroma)
#     results = collection.query(
#         query_embeddings=[question_embedding],
#         n_results=5
#     )

#     context_chunks = results["documents"][0] if results["documents"] else []

#     if not context_chunks:
#         # Use AWS Bedrock NLP model to generate a fallback response
#         response = bedrock_client.invoke_model(
#             modelId="your-bedrock-model-id",
#             body=json.dumps({"query": question})
#         )
        
#         # Return a helpful response if no clinics are found
#         return {"response": "Sorry, we couldn't find any nearby clinics. Would you like to try another location?"}
    
#     context = " ".join(context_chunks)
#     print(context)
    
#     # Constructing the prompt in plain text for Bedrock API
#     prompt = f"""
# Rules: 
#  1. Always return exactly three nearby addresses along with the air to air distance between the user location and center location. 
#  2. Each address must be complete and include city, state, and postal code. 
#  3.if i give you postal code first you in query then find the city using postal code and find me three nearest center or you can find the nearest center fom postal code using knowledge base
#  4.now what i want is that if user gives the city or district name then check the center in that city or district and if it did not find then find the closest city or ditrict by calculating the air to air distance and same with postal code and i want 3 nearby center so please find out the pin code is the postal code so find the nearest postal code from the user given pin code
#  5.also give air to air distance from the current location along with three center
#  6.and if you don''t find that city just find the state and there find the nearest city and give  nearest center the user can give address which does not have centers in knowledge base you just have to find the bnearest center from the knowledge base 
#  7.give the centers which are are close from all the centers and take air from air distance from all the context and return nearest center
# Question: {question}
# Clinic Addresses:
# {context}

# Please return the addresses of the top 3 clinics.
#     """
    
#     # Send the prompt directly as a string in the list
#     chat_response = await client.chat.completions.create(
#                     model="gpt-4-1106-preview",
#         messages=[{"role": "user", "content": prompt}],  # Pass the entire prompt as content
#     )

#     # Parse and return the model's response
    
    
#     return chat_response

# @router.post("/flow_check/")
# async def post_message(
#     question: str, current_user: dict = Depends(get_current_user)
# ):
#     # First, check using Chroma for nearby clinics in your dataset
#     response = bedrock_client.retrieve_and_generate(
#     input={
#         "text": f"""
# You are a helpful assistant.
# User's question: {question}

# You are an assistant that returns clinic addresses from the knowledge base. 
# Rules: 
# 1. Always return exactly three nearby addresses along with the air to air distance between the user location and center location. 
# 2. Each address must be complete and include city, state, and postal code. 
# 3. Do NOT generate or add extra details such as floor numbers, shop numbers, plot numbers, or building names unless they are explicitly present in the knowledge base. 
# 4. Output only the addresses, one per line. No extra text, no explanations. 
# 5.if i give you postal code in query then find the city using postal code and find me three nearest center or you can find the nearest center fom postal code using knowledge base
# 6.now what i want is that if user gives the city or district name then check the center in that city or district and if it did not find then find the closest city or ditrict by calculating the air to air distance and same with postal code and i want 3 nearby center so please find out the pin code is the postal code so find the nearest postal code from the user given pin code
# 7.also give air to air distance from the current location along with three center
# 8.and if you don''t find that city just find the state and there find the nearest city and give  nearest center the user can give address which does not have centers in knowledge base you just have to find the bnearest center from the knowledge base 
# Here are the search results in numbered order:
# """
#     },
#     retrieveAndGenerateConfiguration={
#         "type": "KNOWLEDGE_BASE",
#         "knowledgeBaseConfiguration": {
#             "knowledgeBaseId": "ZVGFUJOKBD",
#             "modelArn": "arn:aws:bedrock:ap-south-1:889060611419:inference-profile/apac.anthropic.claude-3-haiku-20240307-v1:0",
#             "retrievalConfiguration": {
#                 "vectorSearchConfiguration": {"numberOfResults": 15}
#             },
#         },
#     },
# )

#     # Parse and return the model's response
    
    
#     return response["output"]["text"]
# API_KEY=""
# def load_clinics_from_file(file_path):
#     with open(file_path, 'r') as file:
#         clinics = json.load(file)
#     return clinics
# clinics = load_clinics_from_file('src\\backend\\app\\datasets\\ivf_clinic.json')
# class PostalCodeRequest(BaseModel):
#     postal_code: str


# def get_geolocation(location):
#     try:
#         # Use OpenStreetMap's Nominatim service for geocoding
#         headers = {'User-Agent': 'YourAppName/1.0 (hozefaamar198@gmail.com)'}
#         response = requests.get(
#             f'https://nominatim.openstreetmap.org/search',
#             params={'q': location, 'format': 'json'},
#             headers=headers
#         )

#         if response.status_code == 200:
#             try:
#                 data = response.json()
#                 if len(data) > 0:
#                     lat = float(data[0]['lat'])
#                     lon = float(data[0]['lon'])
#                     return lat, lon
#                 else:
#                     return None
#             except ValueError:
#                 raise Exception("Error parsing the geolocation data.")
#         else:
#             raise Exception(f"Error: Received status code {response.status_code} from Nominatim API.")
#     except requests.exceptions.RequestException as e:
#         raise Exception(f"Error making the geocoding request: {str(e)}")
# def find_nearest_clinics(user_location, clinics):
#     user_lat, user_lon = user_location
#     distances = []
    
#     for clinic in clinics:
#         # Geocode the clinic's address if latitude and longitude are not available
#         clinic_location = get_geolocation(clinic['Address'])
#         if clinic_location:
#             clinic_lat, clinic_lon = clinic_location
#             # Calculate the distance between the user and the clinic
#             distance = geodesic(user_location, (clinic_lat, clinic_lon)).km
#             distances.append((clinic['Clinic Name'], distance))
    
#     # Sort by distance
#     distances.sort(key=lambda x: x[1])
    
#     # Return top 3 nearest clinics
#     return distances[:3]

    
#     # Return top 3 nearest clinics
#     return distances[:3]

# @router.post("/nearest_clinics/")
# async def get_nearest_clinics(request: PostalCodeRequest,current_user:dict=Depends(get_current_user)):
#     user_location = get_geolocation(request.postal_code)
    
#     if user_location:
#         nearest_clinics = find_nearest_clinics(user_location, clinics)
#         return {"nearest_clinics": nearest_clinics}
#     else:
#         raise HTTPException(status_code=400, detail="Could not geocode the postal code.")