from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from src.services.auth_service import AuthService
from src.models.user_model import UserCreate, User
from typing import List

router = APIRouter(prefix="/auth", tags=["auth"])
auth_service = AuthService()

@router.post("/register", response_model=User)
async def register(user: UserCreate):
    """Registra un nuevo usuario"""
    try:
        return await auth_service.create_user(user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Inicia sesión y devuelve un token JWT"""
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_service.create_access_token(
        data={"sub": user.email}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """Obtiene la información del usuario actual"""
    return current_user

@router.post("/favorites/{stream_id}")
async def add_favorite(
    stream_id: str,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Agrega un stream a favoritos"""
    success = await auth_service.add_favorite_stream(current_user.id, stream_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo agregar el stream a favoritos"
        )
    return {"message": "Stream agregado a favoritos"}

@router.delete("/favorites/{stream_id}")
async def remove_favorite(
    stream_id: str,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Elimina un stream de favoritos"""
    success = await auth_service.remove_favorite_stream(current_user.id, stream_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo eliminar el stream de favoritos"
        )
    return {"message": "Stream eliminado de favoritos"}

@router.get("/favorites", response_model=List[str])
async def get_favorites(current_user: User = Depends(auth_service.get_current_user)):
    """Obtiene los streams favoritos del usuario"""
    return await auth_service.get_favorite_streams(current_user.id) 