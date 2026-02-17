# handlers/__init__.py

from .start import router as start_router
from .profile import router as profile_router
from .wallet import router as wallet_router
from .user import router as user_router

# Routerlar ro'yxati
routers = [
    start_router,
    profile_router,
    wallet_router,
    user_router
]