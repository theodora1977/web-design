from fastapi import FastAPI, UploadFile, File, Form, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import shutil
import os
import logging

# Database imports
from app.database import engine, SessionLocal
from app.models import Base, Gallery

# Create all database tables
try:
    Base.metadata.create_all(bind=engine)
except Exception:
    logging.exception("Database initialization failed during startup")

app = FastAPI()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Session middleware for simple form-based admin sessions
from starlette.middleware.sessions import SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key=os.getenv('SESSION_SECRET', 'change-this-secret'))

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

templates = Jinja2Templates(directory=TEMPLATE_DIR)
app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")
STATIC_DIR = os.path.join(BASE_DIR, "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# mount auth router
from app.auth import router as auth_router, get_current_admin
app.include_router(auth_router)
from app.images import router as images_router
app.include_router(images_router)
from app.services import router as services_router
app.include_router(services_router)
from app.reviews import router as reviews_router
app.include_router(reviews_router)
from app.appointments import router as appointments_router
app.include_router(appointments_router)


@app.get('/admin')
async def admin_root():
    return RedirectResponse(url='/admin/login')


@app.get('/admin/dashboard')
def admin_dashboard(request: Request, user=Depends(get_current_admin)):
    return templates.TemplateResponse(request, 'admin_dashboard.html', {"request": request, "user": user})


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    db = SessionLocal()
    try:
        featured = db.query(Gallery).order_by(Gallery.id.desc()).limit(6).all()
        services = db.query(Service).order_by(Service.id.asc()).limit(4).all()
    except Exception:
        logger.exception("Failed to load homepage data")
        featured = []
        services = []
    finally:
        db.close()
    return templates.TemplateResponse(request, "index.html", {"request": request, "gallery": featured, "services": services})

@app.get("/upload-page")
async def upload_page(request: Request):
    return templates.TemplateResponse(request, "upload.html", {"request": request})


@app.get('/about', response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse(request, 'about.html', {"request": request})


@app.get('/gallary', response_class=HTMLResponse)
async def gallary(request: Request):
    db = SessionLocal()
    try:
        items = db.query(Gallery).order_by(Gallery.id.desc()).limit(48).all()
    except Exception:
        logger.exception("Failed to load gallery data")
        items = []
    finally:
        db.close()
    return templates.TemplateResponse(request, 'gallary.html', {"request": request, "gallery": items})


from app.models import Service, Review

@app.get('/services', response_class=HTMLResponse)
async def public_services(request: Request):
    db = SessionLocal()
    try:
        services = db.query(Service).all()
    except Exception:
        logger.exception("Failed to load services data")
        services = []
    finally:
        db.close()
    return templates.TemplateResponse(request, 'services.html', {"request": request, "services": services})


@app.get('/contact', response_class=HTMLResponse)
async def contact(request: Request):
    return templates.TemplateResponse(request, 'contact.html', {"request": request})


@app.post('/contact/send')
async def contact_send(name: str = Form(None), email: str = Form(None), message: str = Form(None)):
    # placeholder - in real app this would send email or store message
    return {"status": "ok", "message": "Thanks for contacting us."}


@app.get('/reviews', response_class=HTMLResponse)
async def public_reviews(request: Request):
    db = SessionLocal()
    try:
        reviews = db.query(Review).order_by(Review.id.desc()).all()
    except Exception:
        logger.exception("Failed to load reviews data")
        reviews = []
    finally:
        db.close()
    return templates.TemplateResponse(request, 'reviews.html', {"request": request, "reviews": reviews})


@app.post("/upload")
async def upload(
    title: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    description: str = Form(...),
    image: UploadFile = File(...)
):
    file_location = os.path.join(UPLOAD_FOLDER, image.filename)

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    db = SessionLocal()
    try:
        gallery_item = Gallery(
            title=title,
            category=category,
            price=price,
            description=description,
            image=image.filename,
        )
        db.add(gallery_item)
        db.commit()
        db.refresh(gallery_item)
    finally:
        db.close()

    return {
        "id": gallery_item.id,
        "title": gallery_item.title,
        "category": gallery_item.category,
        "price": gallery_item.price,
        "description": gallery_item.description,
        "image": gallery_item.image
    }
