# Package initialization to group all routes
from fastapi import APIRouter
from app.api.routes import cv, jobs, matching

router = APIRouter()
router.include_router(cv.router)
router.include_router(jobs.router)
router.include_router(matching.router)