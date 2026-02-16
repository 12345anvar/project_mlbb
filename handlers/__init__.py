from .start import router as start_router
from .user import router as user_router
from .profile import router as profile_router
from .wallet import router as wallet_router

routers = [
    start_router,
    user_router,
    profile_router,
    wallet_router
]