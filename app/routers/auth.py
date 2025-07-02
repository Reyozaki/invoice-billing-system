from fastapi import APIRouter, HTTPException, Depends, status, Security
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer, SecurityScopes    #type:ignore
from typing import Annotated
from pydantic import BaseModel

from ..database import db_dependency
from app.config import ALGORITHM, SECRET_KEY
import models

router= APIRouter(
    prefix= '/auth',    
    tags= ["auth"],
    responses= {404: {"description": "Not found"}}
)

bcrypt_context= CryptContext(schemes= ['bcrypt'], deprecated= 'auto')
user_oauth2_bearer= OAuth2PasswordBearer(tokenUrl= 'auth/token', 
                                         scopes={'admin': "Admin access", 'customer': "Customer access"}, 
                                         scheme_name= "UserToken")

class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/token", response_model= Token)
async def login_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                             db: db_dependency):
    user= authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED, 
            detail= "Could not validate User."
        )
    scopes= [user.role]
    token= create_access_token(user.username, user.user_id, scopes, timedelta(minutes= 60))
    return {"access_token": token, "token_type": 'bearer'}


def create_access_token(username: str, user_id: int, scopes: list[str], expires_in: timedelta):
    encode= {
        'sub': username, 
        'id': user_id, 
        'scopes': scopes, 
        'exp': datetime.now() + expires_in
    }
    return jwt.encode(encode, SECRET_KEY, algorithm= ALGORITHM)


def authenticate_user(username: str, password: str, db):
    user= db.query(models.Users).filter(models.Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.password):
        return False
    return user


async def get_current_user(security_scopes: SecurityScopes,
                           token: Annotated[str, Security(user_oauth2_bearer)]):
    
    authenticate_value = f'Required role: "{security_scopes.scope_str}"'
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail= "Could not validate credentials",
        headers= {"WWW-Authenticate": authenticate_value}
    )
    
    try:
        payload= jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str= payload.get('sub')
        user_id: int= payload.get('id')
        token_scopes: list[str] = payload.get("scopes", [])
        
        if username is None or user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code= status.HTTP_403_FORBIDDEN,
                detail= "Not enough permissions",
                headers= {"WWW-Authenticate": authenticate_value}
            )
    return {"id": user_id, "username": username, "scopes": token_scopes}

customer_perm= Annotated[dict, Security(get_current_user, scopes=["customer"])]
admin_perm= Annotated[dict, Security(get_current_user, scopes=["admin"])]
either_perm= Annotated[dict, Security(get_current_user, scopes=[])]

