from openai import OpenAI

from app.utils.config import ENV_PROJECT

# Use this client for all requests
client = OpenAI(api_key=ENV_PROJECT.OPENAI_API_KEY)

async def ask_openai_validation_assistant(prompt: str, model="gpt-4.1-nano", max_tokens=500, temperature=0):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a validation assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        answer = response.choices[0].message.content.strip()
        usage = response.usage
        step_total = usage.total_tokens
        print(
            f"[Token Usage] Prompt: {usage.prompt_tokens}, "
            f"Completion: {usage.completion_tokens}, "
            f"Total: {step_total}"
        )
        return answer
    except Exception as e:
        print(f"[OpenAI Error]: {e}")
        return None, 0
    
token_tracker = {}

def update_token_usage(thread_id: str, tokens: int):
    token_tracker[thread_id] = token_tracker.get(thread_id, 0) + tokens
    return token_tracker[thread_id]

