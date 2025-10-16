from fastapi import FastAPI
from app.api_configure import configure_app, configure_database,configure_scheduler
import os

os.environ["GRPC_VERBOSITY"] = "NONE"
os.environ["GRPC_LOG_SEVERITY_LEVEL"] = "ERROR"

configs = [
    configure_app,
    configure_database,
    configure_scheduler
]

app = FastAPI()

for config in configs:
    config(app)
