from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from convergent.routers import conversation, auth, moderation, analysis, imports
from convergent.settings import settings
from convergent.database import db
from convergent.models import *


app = FastAPI()

allowed_origins = [settings.client_origin]

print("Allowed origins:", allowed_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


app.include_router(auth.router, tags=["auth"])
app.include_router(conversation.router, tags=["conversation"])
app.include_router(moderation.router, tags=["moderation"])
app.include_router(analysis.router, tags=["analysis"])
app.include_router(imports.router, tags=["import"])
