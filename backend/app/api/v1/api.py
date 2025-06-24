# backend/app/api/v1/api.py

from fastapi import APIRouter

from .endpoints import auth, ontology, files 

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(ontology.router, prefix="/ontology", tags=["ontology"])
api_router.include_router(files.router, prefix="/files", tags=["files"]) 