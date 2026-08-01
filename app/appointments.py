from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from app.database import SessionLocal
from app.models import Appointment
from app.auth import get_current_admin

router = APIRouter()


@router.get('/admin/appointments')
def admin_appointments(request: Request, user=Depends(get_current_admin)):
    db = SessionLocal()
    try:
        appts = db.query(Appointment).order_by(Appointment.appointment_datetime.desc()).all()
    finally:
        db.close()
    from fastapi.templating import Jinja2Templates
    import os
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    templates = Jinja2Templates(directory=os.path.join(BASE_DIR, 'templates'))
    return templates.TemplateResponse(request, 'admin_appointments.html', {"request": request, "appointments": appts, "user": user})


@router.post('/admin/appointments/delete/{appointment_id}')
def delete_appointment(appointment_id: int, user=Depends(get_current_admin)):
    db = SessionLocal()
    try:
        a = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if a:
            db.delete(a)
            db.commit()
    finally:
        db.close()
    return RedirectResponse(url='/admin/appointments', status_code=303)
