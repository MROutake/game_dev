"""
Hister 2.0 - FastAPI Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
from .core.config import settings
from .api import auth, playlist, game, lobby
from .services.websocket_service import sio

# FastAPI App
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="🎵 Music Quiz Game - Rate Titel, Interpret & Jahrzehnt!",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Socket.IO ASGI App
socket_app = socketio.ASGIApp(
    sio,
    other_asgi_app=app,
    socketio_path='/socket.io'
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(playlist.router)
app.include_router(game.router)
app.include_router(lobby.router)


@app.get("/")
async def root():
    """
    Root Endpoint
    """
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "message": "🎵 Hister 2.0 - Music Quiz Game"
    }


@app.get("/health")
async def health_check():
    """
    Health Check
    """
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:socket_app", host="0.0.0.0", port=8000, reload=True)
