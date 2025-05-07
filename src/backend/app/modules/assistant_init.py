import json
import os
import asyncio
import aiohttp

relative_path1 = ".//src//backend//app//datasets//ivf_clinic.json"
relative_path2 = ".//src//backend//app//datasets//faq.json"
relative_path3 = ".//src//backend//app//datasets//need.json"
absolute_path = os.path.abspath(relative_path1)
with open(absolute_path, "r") as f:
    dataset = json.load(f)
absolute_path2 = os.path.abspath(relative_path2)
with open(absolute_path2, "r") as fi:
    dataset2 = json.load(fi)

absolute_path3 = os.path.abspath(relative_path3)
with open(absolute_path3, "r", encoding="utf-8") as fii:
    dataset3 = json.load(fii)

centers = json.dumps(dataset)
faq = json.dumps(dataset2)
need = json.dumps(dataset3)


class IVFChatbot:
    def __init__(self, client):
        self.assistant = None
        self.instructions = ""
        self.client = client
        self.thread = None

    async def initialize_assistant(self):
        self.instructions = f"""Objective:
- You are IndiraBot, an AI assistant representing Indira IVF, a leading fertility clinic.
- You are engaging with potential clients through chat to answer FAQs, provide information about nearby Indira IVF centers, and help them understand potential treatment options based on their inputs and the dataset provided.
- You must use the dataset provided (in JSON format) as your knowledge base to ensure accurate responses.
- Your tone should be sweet, empathetic, and helpful, with occasional gentle humor and emojis to create a comforting experience. Keep responses less verbose.
- Responses must always be in the user’s last used language.

Allowed Actions:
1. **Introduction**: Greet warmly, introduce yourself as IndiraBot from Indira IVF, and state you’re here to help. This should only happen at the beginning.
2. **FAQ Resolution**: Answer user questions based on the FAQs section in the provided dataset. Respond in the user's last used language, providing the full answer from the dataset {faq}.
3. **Nearby Centers**: If asked for nearby Indira IVF centers, check the dataset’s location information to suggest the closest ones based on user-provided city/state. Acknowledge if additional tool/API might be required for precision. Provide the full address from the dataset {centers}. If user provides coordinates:
    3.1 **Coordinates**: Use the dataset to give the address of the nearest center.
    3.2 **Estimated Distances**: Calculate the approximate distance (in kilometers) and estimated travel time to the nearest center based on the provided coordinates and information in the dataset. Include this information in your response, along with the "Know More" link from the dataset. Keep this response concise and empathetic.
4. **Need Generation**: Understand user details (such as treatment interest, urgency, marital history, etc.) and respond with warm, general insights using the dataset (without offering medical advice). Provide the full answer given in the dataset {need}.
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
- Always match the client’s last used language in your response. Focus on the language of the most recent question.
"""

        if not self.assistant:
            self.assistant = self.client.beta.assistants.create(
                model="gpt-4-1106-preview", instructions=self.instructions
            )
            print("Assistant initialized!")
        else:
            print("Assistant already initialized.")

    async def get_response(self, question: str, chat_history: list) -> str:
        print("In get_response...")
        print("Printing question:", question)
        print("chat_history", chat_history)

        if self.assistant is None:
            print("Assistant initializing...")
            await self.initialize_assistant()

        try:

            if self.thread is None:
                self.thread = self.client.beta.threads.create()

            self.client.beta.threads.messages.create(
                thread_id=self.thread.id, role="user", content=question
            )

            run = self.client.beta.threads.runs.create(
                thread_id=self.thread.id, assistant_id=self.assistant.id
            )

            while True:
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread.id, run_id=run.id
                )
                if run_status.status == "completed":
                    break
                elif run_status.status == "failed":
                    print("❌ Assistant run failed. Reason:")
                    print(run_status.model_dump_json(indent=2))
                    return "The assistant failed to generate a response."
                await asyncio.sleep(0.1)

            messages = self.client.beta.threads.messages.list(
                thread_id=self.thread.id, run_id=run.id
            )

            assistant_answer = None
            for message in reversed(messages.data):
                if message.role == "assistant":
                    assistant_answer = message.content[0].text.value.strip()
                    chat_history.append(
                        {"role": "assistant", "content": assistant_answer}
                    )
                    break

            if not assistant_answer:
                return "No assistant response found."

            return assistant_answer

        except Exception as e:
            return f"An error occurred: {str(e)}"

    async def process_and_book_appointment(
        self, user_text: str, user_data: dict
    ) -> str:
        print("Processing appointment booking via assistant...")

        if self.assistant is None:
            await self.initialize_assistant()

        try:

            temp_thread = self.client.beta.threads.create()

            self.client.beta.threads.messages.create(
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

            run = self.client.beta.threads.runs.create(
                thread_id=temp_thread.id, assistant_id=self.assistant.id
            )

            while True:
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=temp_thread.id, run_id=run.id
                )
                if run_status.status == "completed":
                    break
                elif run_status.status == "failed":
                    print("❌ Assistant run failed.")
                    return "Sorry, I couldn't extract your appointment details. Please try again."
                await asyncio.sleep(0.2)

            messages = self.client.beta.threads.messages.list(thread_id=temp_thread.id)
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
                print("Error parsing JSON:", e)
                return "Failed to understand the appointment details. Please try again."

            print("Extracted:", extracted_data)

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
            print("chat_history", chat_history)

            history_text = "\n".join(
                [f"{message['role']}: {message['content']}" for message in chat_history]
            )
            prompt = f"Given the following chat history, generate an appropriate thread name:\n{history_text} and generate thread name in same language the user asked question in this is very important the chatname should be in same language the user asked question and for location generate thread name in english"

            thread = self.client.beta.threads.create()

            self.client.beta.threads.messages.create(
                thread_id=thread.id, role="user", content=prompt
            )

            run = self.client.beta.threads.runs.create(
                thread_id=thread.id, assistant_id=self.assistant.id
            )

            while True:
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=thread.id, run_id=run.id
                )
                if run_status.status == "completed":
                    break
                elif run_status.status == "failed":
                    return "The assistant failed to generate a thread name."
                await asyncio.sleep(0.1)

            messages = self.client.beta.threads.messages.list(thread_id=thread.id)

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
