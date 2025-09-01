import asyncio
import aiohttp
from app.core.chroma_db_init import collections,detect_query_type

# relative_path1 = ".//src//backend//app//datasets//ivf_clinic.json"
# relative_path2 = ".//src//backend//app//datasets//faq.json"
# relative_path3 = ".//src//backend//app//datasets//need.json"
# absolute_path = os.path.abspath(relative_path1)
# with open(absolute_path, "r") as f:
#     dataset = json.load(f)
# absolute_path2 = os.path.abspath(relative_path2)
# with open(absolute_path2, "r") as fi:
#     dataset2 = json.load(fi)

# absolute_path3 = os.path.abspath(relative_path3)
# with open(absolute_path3, "r", encoding="utf-8") as fii:
#     dataset3 = json.load(fii)

# centers = json.dumps(dataset)
# faq = json.dumps(dataset2)
# need = json.dumps(dataset3)


class IVFChatbot:
    def __init__(self, client):
        self.assistant = None
        self.instructions = ""
        self.client = client
        # self.thread = None
        # self.file_ids = [faq_file_id, center_file_id, need_file_id]
        # self.collections={}

    async def initialize_assistant(self):
        # await initialize_chroma(self.collections)
        # upload_paths = [
        #         ".//src//backend//app//datasets//faq.json",
        #         ".//src//backend//app//datasets//ivf_clinic.json",
        #         ".//src//backend//app//datasets//need.json"
        #     ]

        # upload_tasks = [
        #         self.client.files.create(file=open(path, "rb"), purpose="assistants")
        #         for path in upload_paths
        #     ]
        # uploaded_files = await asyncio.gather(*upload_tasks)
        self.instructions = f"""Objective:
- You are IndiraBot, an AI assistant representing Indira IVF, a leading fertility clinic.
- You are engaging with potential clients through chat to answer FAQs, provide information about nearby Indira IVF centers, and help them understand potential treatment options based on their inputs and the dataset provided.
- You must use the dataset provided (in JSON format) as your knowledge base to ensure accurate responses.
- Your tone should be sweet, empathetic, and helpful, with occasional gentle humor and emojis to create a comforting experience. Keep responses less verbose.
- Responses must always be in the user’s last used language.

Allowed Actions:
1. **Introduction**: Greet warmly, introduce yourself as IndiraBot from Indira IVF, and state you’re here to help. This should only happen at the beginning.
2. **FAQ Resolution**: Answer user questions based on the FAQs section in the provided dataset. Respond in the user's last used language, providing the full answer from the dataset .
3. **Nearby Centers**: If asked for nearby Indira IVF centers, check the dataset’s location information to suggest the closest ones based on user-provided city/state. Acknowledge if additional tool/API might be required for precision. Provide the full address from the dataset . If user provides coordinates:
    3.1 **Coordinates**: Use the dataset to give the address of the nearest center.
    3.2 **Estimated Distances**: Calculate the approximate distance (in kilometers) and estimated travel time to the nearest center based on the provided coordinates and information in the dataset. Include this information in your response, along with the "Know More" link from the dataset. Keep this response concise and empathetic.
4. **Need Generation**: Understand user details (such as treatment interest, urgency, marital history, etc.) and respond with warm, general insights using the dataset (without offering medical advice). Provide the full answer given in the dataset .
5. **AI-Generated Answers**: If the answer isn’t directly available in the dataset, respond empathetically using your best knowledge and make it clear it is AI-generated, not medical advice. Keep this concise.
6. **Suggestion Solicitation**: After answering, gently ask if there’s anything else you can help with.
7. **End Conversation**: Politely end the chat when the user’s queries are resolved or if they wish to exit.
8. **Negative Feedback Handling**: If the user expresses negative opinions or talks against Indira IVF, do not engage with that specific query and do not provide a response.

Assistant's Guidelines:
- Strictly never give medical advice. Always suggest users consult Indira IVF doctors for personal guidance.
- Keep responses warm, concise, emotionally supportive, and clear.
- Use gentle emojis (e.g., 😊, 🌸, ✨) to enhance the tone, but not excessively.
- Never use URLs or lists in replies, except for the single "Know More" link in the nearby centers response with coordinates.
- Strictly respond to one user message at a time.
- Never ask the user to wait.
- Use only the dataset provided (via JSON) to answer questions unless a creative AI response is needed for unavailable information.
- Always match the client’s last used language in your response. Focus on the language of the most recent question and it can be there that the address is in english but the words are of hindi language but give response in english.
--please give the addres properly which i have given in the database as ivf_clicnic.json which is in vector store use that properly
--for nearby center fetch the appropriate center from vector stores which will be near to them and this is very important for eg if i'm sending corrdinates near udaipur city then find the centers in udaipur from vector stores and suggest me that center which are closet from my coordinates if coordinates are given
--ensure that you don't generate address and don't generate address on your own you should only use that address which is given in ivf_clinic.json in vector stores don't mismatch the two address also please ensure this and only take address from vector store given in file id which is ivf_clinic.json
--i'm giving the coordinates so suggest me near by center and the centers are available in ivf_clinic.json so see that dataset in vector store and according to the coordinates give me appropriate centers near by my coordinates and this is very important
--don't give my dataset name or etc just give gentle answer in sweet voice and in the same language in which the user have asked
-note if i ask for any faq search in faq.json in vector store that i have provided but if ask for any nearby center then search in ivf_clinic.json and of i ask for need generation then search in need.json
--give appropriated address don't give any vague adress
"""
    #     vector_store = await self.client.vector_stores.create(name="IVF Knowledge Base")

    # # Step 3: Attach all files concurrently to the vector store
    #     attach_tasks = [
    #         self.client.vector_stores.files.create(
    #             vector_store_id=vector_store.id,
    #             file_id=file.id
    #         )
    #         for file in uploaded_files
    #     ]
    #     await asyncio.gather(*attach_tasks)
        # if not self.assistant:
        #     self.assistant = await self.client.beta.assistants.create(
        #         model="gpt-4-1106-preview",
        #         instructions=self.instructions       )
        #     print("Assistant initialized!")
        # else:
        #     print("Assistant already initialized.")
    async def get_response(self, question: str, chat_history: list, query_type: str = "clinic") -> str:
        try:
            query_type=await detect_query_type(question)
            print("printing the query type")
            if query_type == "clinic":
                short_question = question.split(',')
                collection = collections.get(query_type)
                if not collection:
                    return f"No knowledge base loaded for: {query_type}"

                # Safe fallback: check for sufficient parts
                if len(short_question) >= 3:
                    city = short_question[-3].strip()
                    state = short_question[-2].strip()
                    embed_input = f"City:{city} State:{state}"
                else:
                    embed_input = question  # use full question if city/state can't be extracted

                # Step 2: Get embedding for the extracted or full query
                response = await self.client.embeddings.create(
                    model="text-embedding-3-small",
                    input=[embed_input]
                )
                question_embedding = response.data[0].embedding

                # Step 3: Query Chroma for top relevant chunks
                results = collection.query(
                    query_embeddings=[question_embedding],
                    n_results=10
                )
                print(results)
                context_chunks = results["documents"][0] if results["documents"] else []
                context = "\n---\n".join(context_chunks)

                # Step 4: Prepare messages for OpenAI Chat API
                messages = [
                    {"role": "system", "content": self.instructions},
                    {"role": "user", "content": f"Use the following context to answer the question.\n\nContext:\n{context}\n\nQuestion: {question}"}
                ]

                # Step 5: Generate the response
                chat_response = await self.client.chat.completions.create(
                    model="gpt-4-1106-preview",
                    messages=messages
                )

                assistant_answer = chat_response.choices[0].message.content.strip()
                # chat_history.append({"role": "assistant", "content": assistant_answer})

                return assistant_answer
            else:
            # Step 1: Get the relevant Chroma collection
                collection = collections.get(query_type)
                if not collection:
                    return f"No knowledge base loaded for: {query_type}"

                # Step 2: Get embedding for the user's question
                response = await self.client.embeddings.create(
                    model="text-embedding-3-small",
                    input=[question]
                )
                question_embedding = response.data[0].embedding

                # Step 3: Query Chroma for top relevant chunks
                results =  collection.query(
                    query_embeddings=[question_embedding],
                    n_results=5
                )

                context_chunks = results["documents"][0] if results["documents"] else []
                context = "\n---\n".join(context_chunks)

                # Step 4: Prepare the messages for OpenAI Chat API
                messages = [
                    {"role": "system", "content": self.instructions},
                    {"role": "user", "content": f"Use the following context to answer the question.\n\nContext:\n{context}\n\nQuestion: {question}"}
                ]

                # Step 5: Generate the response using GPT
                chat_response =  await self.client.chat.completions.create(
                    model="gpt-4-1106-preview",
                    messages=messages
                )

                assistant_answer = chat_response.choices[0].message.content.strip()
                # chat_history.append({"role": "assistant", "content": assistant_answer})

                return assistant_answer

        except Exception as e:
            return f"An error occurred: {str(e)}"


    # async def get_response(self, question: str, chat_history: list) -> str:
    #     print("In get_response...")
    #     print("Printing question:", question)
    #     print("chat_history", chat_history)

    #     if self.assistant is None:
    #         print("Assistant initializing...")
    #         await self.initialize_assistant()

    #     try:

    #         if self.thread is None:
    #             self.thread =  await self.client.beta.threads.create()

    #         await self.client.beta.threads.messages.create(
    #             thread_id=self.thread.id, role="user", content=question
    #         )

    #         run = await self.client.beta.threads.runs.create(
    #             thread_id=self.thread.id, assistant_id=self.assistant.id
    #         )

    #         while True:
    #             run_status = await self.client.beta.threads.runs.retrieve(
    #                 thread_id=self.thread.id, run_id=run.id
    #             )
    #             if run_status.status == "completed":
    #                 break
    #             elif run_status.status == "failed":
    #                 print("❌ Assistant run failed. Reason:")
    #                 print(run_status.model_dump_json(indent=2))
    #                 return "The assistant failed to generate a response."
    #             await asyncio.sleep(0.4)

    #         messages = await self.client.beta.threads.messages.list(
    #             thread_id=self.thread.id, run_id=run.id
    #         )

    #         assistant_answer = None
    #         for message in reversed(messages.data):
    #             if message.role == "assistant":
    #                 assistant_answer = message.content[0].text.value.strip()
    #                 chat_history.append(
    #                     {"role": "assistant", "content": assistant_answer}
    #                 )
    #                 break

    #         if not assistant_answer:
    #             return "No assistant response found."

    #         return assistant_answer

    #     except Exception as e:
    #         return f"An error occurred: {str(e)}"

    async def process_and_book_appointment(
        self, user_text: str, user_data: dict
    ) -> str:


        if self.assistant is None:
            await self.initialize_assistant()

        try:

            temp_thread = await self.client.beta.threads.create()

            await self.client.beta.threads.messages.create(
                thread_id=temp_thread.id,
                role="user",
                content=f"""
    You are an expert form extractor.

    From the following user message, extract ONLY this information:
    - Full Name
    - Email Address
    - Phone Number
    - Preferred Center
    - Appointment Date (YYYY-MM-DD format)
    - Appointment Time (e.g., 10:00 AM, 2:00 PM)

    Strictly reply ONLY in JSON like this:
    {{
    "name": "...",
    "email": "...",
    "phone": "...",
    "center": "...",
    "date": "...",
    "time": "..."
    }}

    If any field is missing, leave it as null.

    Here is the user input:
    \"\"\"{user_text}\"\"\"
    """,
            )

            run = await self.client.beta.threads.runs.create(
                thread_id=temp_thread.id, assistant_id=self.assistant.id
            )

            while True:
                run_status = await self.client.beta.threads.runs.retrieve(
                    thread_id=temp_thread.id, run_id=run.id
                )
                if run_status.status == "completed":
                    break
                elif run_status.status == "failed":
                    return "Sorry, I couldn't extract your appointment details. Please try again."
                await asyncio.sleep(0.2)

            messages = await self.client.beta.threads.messages.list(thread_id=temp_thread.id)
            assistant_response = None
            for message in reversed(messages.data):
                if message.role == "assistant":
                    assistant_response = message.content[0].text.value.strip()
                    break

            if not assistant_response:
                return "Sorry, I couldn't extract your appointment details."

            import json

            try:
                extracted_data = json.loads(assistant_response)
            except Exception as e:
                return "Failed to understand the appointment details. Please try again."

            

            missing_fields = []
            if not extracted_data.get("name"):
                missing_fields.append("Name")
            if not extracted_data.get("email"):
                missing_fields.append("Email")
            if not extracted_data.get("phone"):
                missing_fields.append("Phone Number")
            if not extracted_data.get("center"):
                missing_fields.append("Preferred Center")
            if not extracted_data.get("date"):
                missing_fields.append("Appointment Date")
            if not extracted_data.get("time"):
                missing_fields.append("Appointment Time")

            if missing_fields:
                missing_list = ", ".join(missing_fields)
                return f"Please provide the following missing details to complete your appointment booking: {missing_list}."

            appointment_payload = {
                "name": extracted_data["name"],
                "email": extracted_data["email"],
                "phone": extracted_data["phone"],
                "preferred_center": extracted_data["center"],
                "appointment_date": extracted_data["date"],
                "appointment_time": extracted_data["time"],
            }

            api_url = (
                "https://your.api.endpoint/appointments"  # ⬅️ replace with your API
            )
            headers = {"Content-Type": "application/json"}

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    api_url, json=appointment_payload, headers=headers
                ) as response:
                    if response.status == 200:
                        api_response = await response.json()
                        return f"🎉 Appointment booked successfully! {api_response.get('message', 'Confirmation received.')}"
                    else:
                        error_text = await response.text()
                        return (
                            f"❌ Failed to book appointment. Server said: {error_text}"
                        )

        except Exception as e:
            return f"An error occurred: {str(e)}"

    async def get_thread_name(self, chat_history: list) -> str:
        """Generate a thread name based on the chat history."""
        if self.assistant is None:
            print("Assistant initializing...")

        try:

            history_text = "\n".join(
                [f"{message['role']}: {message['content']}" for message in chat_history]
            )
            prompt = f"Given the following chat history, generate an appropriate thread name:\n{history_text} and generate thread name in same language the user asked question in this is very important the chatname should be in same language the user asked question and for location generate thread name in english"

            thread = await self.client.beta.threads.create()

            await self.client.beta.threads.messages.create(
                thread_id=thread.id, role="user", content=prompt
            )

            run = await self.client.beta.threads.runs.create(
                thread_id=thread.id, assistant_id=self.assistant.id
            )

            while True:
                run_status = await self.client.beta.threads.runs.retrieve(
                    thread_id=thread.id, run_id=run.id
                )
                if run_status.status == "completed":
                    break
                elif run_status.status == "failed":
                    return "The assistant failed to generate a thread name."
                await asyncio.sleep(0.1)

            messages = await self.client.beta.threads.messages.list(thread_id=thread.id)

            assistant_answer = None
            for message in reversed(messages.data):
                if message.role == "assistant":
                    assistant_answer = message.content[0].text.value.strip()
                    break

            if not assistant_answer:
                return "No thread name generated."

            return assistant_answer

        except Exception as e:
            return f"An error occurred: {str(e)}"
