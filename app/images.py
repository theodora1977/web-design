from fastapi import APIRouter, Request, Depends, UploadFile, File, Form
from fastapi.responses import RedirectResponse
import os
import shutil

from app.database import SessionLocal
from app.models import Gallery
from app.auth import get_current_admin

router = APIRouter()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, 'templates'))


@router.get('/admin/images')
def admin_images(request: Request, user=Depends(get_current_admin)):
    db = SessionLocal()
    try:
        images = db.query(Gallery).order_by(Gallery.id.desc()).all()
    finally:
        db.close()
    return templates.TemplateResponse(request, 'admin_images.html', {"request": request, "images": images, "user": user})


@router.get('/admin/images/edit/{image_id}')
def edit_image_page(request: Request, image_id: int, user=Depends(get_current_admin)):
    db = SessionLocal()
    try:
        img = db.query(Gallery).filter(Gallery.id == image_id).first()
    finally:
        db.close()
    if not img:
        return RedirectResponse(url='/admin/images')
    return templates.TemplateResponse(request, 'edit_image.html', {"request": request, "image": img, "user": user})


@router.post('/admin/images/edit/{image_id}')
def edit_image(image_id: int, title: str = Form(...), category: str = Form(...), price: float = Form(...), description: str = Form(''), image: UploadFile = File(None), user=Depends(get_current_admin)):
    db = SessionLocal()
    try:
        img = db.query(Gallery).filter(Gallery.id == image_id).first()
        if not img:
            return RedirectResponse(url='/admin/images')

        img.title = title
        img.category = category
        img.price = price
        img.description = description

        if image is not None:
            # save new file
            dest = os.path.join(UPLOAD_FOLDER, image.filename)
            with open(dest, 'wb') as buffer:
                shutil.copyfileobj(image.file, buffer)
            # remove old file
            old_path = os.path.join(UPLOAD_FOLDER, img.image)
            try:
                if os.path.exists(old_path):
                    os.remove(old_path)
            except Exception:
                pass
            img.image = image.filename

        db.add(img)
        db.commit()
    finally:
        db.close()
    return RedirectResponse(url='/admin/images', status_code=303)


@router.post('/admin/images/delete/{image_id}')
def delete_image(image_id: int, user=Depends(get_current_admin)):
    db = SessionLocal()
    try:
        img = db.query(Gallery).filter(Gallery.id == image_id).first()
        if img:
            # delete file
            try:
                fp = os.path.join(UPLOAD_FOLDER, img.image)
                if os.path.exists(fp):
                    os.remove(fp)
            except Exception:
                pass
            db.delete(img)
            db.commit()
    finally:
        db.close()
    return RedirectResponse(url='/admin/images', status_code=303)
