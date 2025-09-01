from app.config import ENV_PROJECT

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=ENV_PROJECT.PORT,
        reload=True,
        loop="asyncio",
    )
