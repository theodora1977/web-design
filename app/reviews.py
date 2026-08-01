from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from app.database import SessionLocal
from app.models import Review
from app.auth import get_current_admin

router = APIRouter()


@router.get('/admin/reviews')
def admin_reviews(request: Request, user=Depends(get_current_admin)):
    db = SessionLocal()
    try:
        reviews = db.query(Review).order_by(Review.id.desc()).all()
    finally:
        db.close()
    from fastapi.templating import Jinja2Templates
    import os
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    templates = Jinja2Templates(directory=os.path.join(BASE_DIR, 'templates'))
    return templates.TemplateResponse(request, 'admin_reviews.html', {"request": request, "reviews": reviews, "user": user})


@router.post('/admin/reviews/delete/{review_id}')
def delete_review(review_id: int, user=Depends(get_current_admin)):
    db = SessionLocal()
    try:
        r = db.query(Review).filter(Review.id == review_id).first()
        if r:
            db.delete(r)
            db.commit()
    finally:
        db.close()
    return RedirectResponse(url='/admin/reviews', status_code=303)
