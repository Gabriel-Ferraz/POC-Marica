from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes_auth import router as auth_router
from app.api.routes_users import router as users_router, dept_router
from app.api.routes_workflows import router as workflows_router
from app.api.routes_processes import router as processes_router
from app.api.routes_dlt import router as dlt_router
from app.api.routes_chatbots import router as chatbots_router, nlp_router
from app.api.routes_voice import router as voice_router
from app.api.routes_idp import router as idp_router
from app.api.routes_automations import router as automations_router

app = FastAPI(
    title="POC ICTIM",
    description="Plataforma DLT, Workflows, Chatbot, IDP e Automação",
    version="1.0.0",
)

origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(dept_router)
app.include_router(workflows_router)
app.include_router(processes_router)
app.include_router(dlt_router)
app.include_router(chatbots_router)
app.include_router(nlp_router)
app.include_router(voice_router)
app.include_router(idp_router)
app.include_router(automations_router)


@app.get("/health")
def health():
    return {"status": "ok"}
