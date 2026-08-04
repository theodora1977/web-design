from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from starlette.status import HTTP_302_FOUND
import os

from app.database import SessionLocal
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(db, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


@router.get('/signup')
def signup_page(request: Request):
    return templates.TemplateResponse(request, 'signup.html', {"request": request})


@router.post('/signup')
def signup(request: Request, username: str = Form(...), password: str = Form(...), confirm_password: str = Form(...)):
    if password != confirm_password:
        return templates.TemplateResponse(request, 'signup.html', {"request": request, "error": "Passwords do not match."})

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            return templates.TemplateResponse(request, 'signup.html', {"request": request, "error": "Username already taken."})
        user = User(username=username, hashed_password=get_password_hash(password), is_admin=True)
        db.add(user)
        db.commit()
    finally:
        db.close()

    return RedirectResponse(url='/admin/login', status_code=HTTP_302_FOUND)


@router.get('/admin/login')
def login_page(request: Request):
    return templates.TemplateResponse(request, 'login.html', {"request": request})


@router.post('/admin/login')
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    db = SessionLocal()
    try:
        user = authenticate_user(db, username, password)
    finally:
        db.close()

    if not user or not user.is_admin:
        return templates.TemplateResponse(request, 'login.html', {"request": request, "error": "Invalid credentials"})

    request.session['admin_user'] = user.username
    return RedirectResponse(url='/admin/dashboard', status_code=HTTP_302_FOUND)


@router.get('/admin/logout')
def logout(request: Request):
    request.session.pop('admin_user', None)
    return RedirectResponse(url='/', status_code=HTTP_302_FOUND)


def get_current_admin(request: Request):
    username = request.session.get('admin_user')
    if not username:
        raise HTTPException(status_code=401, detail='Not authenticated')
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
    finally:
        db.close()
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail='Forbidden')
    return user
