from fastapi import HTTPException

async def openai_token_calculation(response):
    try:
        usage = response.usage
        step_total = usage.total_tokens
        print(
            f"[Token Usage] Prompt: {usage.prompt_tokens}, "
            f"Completion: {usage.completion_tokens}, "
            f"Total: {step_total}"
        )
        return usage.prompt_tokens,usage.completion_tokens,step_total
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )
    

async def update_token_usage(thread_id: str, tokens: int):
    token_tracker = {}
    token_tracker[thread_id] = token_tracker.get(thread_id, 0) + tokens
    return token_tracker[thread_id]

