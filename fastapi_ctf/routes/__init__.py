from fastapi import APIRouter

from .content import router as content_router
from .profile import router as profile_router
from .security import router as security_router
from .user import router as user_router
from .ctf import router as ctf_router
from .forensicSecurity import router as forensic_router

main_router = APIRouter()

# main_router.include_router(content_router, prefix="/content", tags=["content"])
# main_router.include_router(profile_router, tags=["user"])
# main_router.include_router(security_router, tags=["security"])
# main_router.include_router(user_router, prefix="/user", tags=["user"])
main_router.include_router(ctf_router, prefix='/ctf', tags=["Capture the Flag"])
main_router.include_router(forensic_router, prefix='/forensic', tags=["Forensic Security"])


@main_router.get("/")
async def index():
    return {"message": "Hello World!"}
