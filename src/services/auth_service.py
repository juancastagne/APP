from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from src.models.user_model import User, UserCreate, UserInDB
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

class AuthService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
        self.secret_key = os.getenv("JWT_SECRET")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        
        # MongoDB
        self.mongo_client = AsyncIOMotorClient(os.getenv('MONGODB_URI'))
        self.db = self.mongo_client.stream_views
        self.users = self.db.users

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica si la contraseña coincide con el hash"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Genera el hash de una contraseña"""
        return self.pwd_context.hash(password)

    async def create_user(self, user: UserCreate) -> User:
        """Crea un nuevo usuario"""
        # Verificar si el email ya existe
        if await self.users.find_one({"email": user.email}):
            raise HTTPException(status_code=400, detail="Email ya registrado")
        
        # Verificar si el username ya existe
        if await self.users.find_one({"username": user.username}):
            raise HTTPException(status_code=400, detail="Username ya existe")

        # Crear usuario en la base de datos
        user_in_db = UserInDB(
            email=user.email,
            username=user.username,
            hashed_password=self.get_password_hash(user.password),
            favorite_streams=user.favorite_streams
        )

        await self.users.insert_one(user_in_db.dict())
        return User(**user_in_db.dict(exclude={'hashed_password'}))

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Autentica un usuario"""
        user = await self.users.find_one({"email": email})
        if not user:
            return None
        if not self.verify_password(password, user["hashed_password"]):
            return None
        
        # Actualizar último login
        await self.users.update_one(
            {"email": email},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        return User(**user)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Crea un token JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    async def get_current_user(self, token: str = Security(OAuth2PasswordBearer(tokenUrl="token"))) -> User:
        """Obtiene el usuario actual desde el token"""
        credentials_exception = HTTPException(
            status_code=401,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
        except jwt.PyJWTError:
            raise credentials_exception
            
        user = await self.users.find_one({"email": email})
        if user is None:
            raise credentials_exception
            
        return User(**user)

    async def add_favorite_stream(self, user_id: str, stream_id: str) -> bool:
        """Agrega un stream a favoritos"""
        try:
            result = await self.users.update_one(
                {"_id": user_id},
                {"$addToSet": {"favorite_streams": stream_id}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error al agregar stream favorito: {str(e)}")
            return False

    async def remove_favorite_stream(self, user_id: str, stream_id: str) -> bool:
        """Elimina un stream de favoritos"""
        try:
            result = await self.users.update_one(
                {"_id": user_id},
                {"$pull": {"favorite_streams": stream_id}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error al eliminar stream favorito: {str(e)}")
            return False

    async def get_favorite_streams(self, user_id: str) -> list:
        """Obtiene los streams favoritos de un usuario"""
        try:
            user = await self.users.find_one({"_id": user_id})
            return user.get("favorite_streams", []) if user else []
        except Exception as e:
            print(f"Error al obtener streams favoritos: {str(e)}")
            return [] 