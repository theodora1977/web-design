from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from app.database import SessionLocal
from app.models import Service
from app.auth import get_current_admin
import os
from fastapi.templating import Jinja2Templates

router = APIRouter()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, 'templates'))


@router.get('/admin/services')
def admin_services(request: Request, user=Depends(get_current_admin)):
    db = SessionLocal()
    try:
        services = db.query(Service).order_by(Service.id.desc()).all()
    finally:
        db.close()
    return templates.TemplateResponse(request, 'admin_services.html', {"request": request, "services": services, "user": user})


@router.post('/admin/services/add')
def add_service(name: str = Form(...), description: str = Form(''), price: float = Form(...), user=Depends(get_current_admin)):
    db = SessionLocal()
    try:
        svc = Service(name=name, description=description, price=price)
        db.add(svc)
        db.commit()
    finally:
        db.close()
    return RedirectResponse(url='/admin/services', status_code=303)


@router.get('/admin/services/edit/{service_id}')
def edit_service_page(request: Request, service_id: int, user=Depends(get_current_admin)):
    db = SessionLocal()
    try:
        svc = db.query(Service).filter(Service.id == service_id).first()
    finally:
        db.close()
    if not svc:
        return RedirectResponse(url='/admin/services')
    return templates.TemplateResponse(request, 'edit_service.html', {"request": request, "service": svc, "user": user})


@router.post('/admin/services/edit/{service_id}')
def edit_service(service_id: int, name: str = Form(...), description: str = Form(''), price: float = Form(...), user=Depends(get_current_admin)):
    db = SessionLocal()
    try:
        svc = db.query(Service).filter(Service.id == service_id).first()
        if not svc:
            return RedirectResponse(url='/admin/services')
        svc.name = name
        svc.description = description
        svc.price = price
        db.add(svc)
        db.commit()
    finally:
        db.close()
    return RedirectResponse(url='/admin/services', status_code=303)


@router.post('/admin/services/delete/{service_id}')
def delete_service(service_id: int, user=Depends(get_current_admin)):
    db = SessionLocal()
    try:
        svc = db.query(Service).filter(Service.id == service_id).first()
        if svc:
            db.delete(svc)
            db.commit()
    finally:
        db.close()
    return RedirectResponse(url='/admin/services', status_code=303)
