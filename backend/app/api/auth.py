"""
Spotify Authentication Endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from ..services.spotify_service import spotify_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/login")
async def spotify_login():
    """
    Starte Spotify OAuth Flow
    Returns: Authorization URL
    """
    try:
        auth_url = spotify_service.get_auth_url()
        return {
            "auth_url": auth_url,
            "message": "Öffne diese URL im Browser zum Login"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auth URL Error: {str(e)}")


@router.get("/callback")
async def spotify_callback(code: str = Query(...)):
    """
    Spotify OAuth Callback
    Wird von Spotify nach erfolgreichem Login aufgerufen
    """
    try:
        token_info = spotify_service.authenticate_with_code(code)
        return {
            "message": "Login erfolgreich!",
            "access_token": token_info['access_token'],
            "expires_in": token_info['expires_in']
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Auth Error: {str(e)}")


@router.post("/set-token")
async def set_user_token(access_token: str):
    """
    Setze User Access Token manuell
    """
    try:
        spotify_service.set_user_token(access_token)
        return {"message": "Token gesetzt"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
