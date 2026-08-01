from app.database import SessionLocal
from app.models import Service

db = SessionLocal()
try:
    services = db.query(Service).filter(Service.name.ilike('%mens%') | Service.name.ilike('%men%')).all()
    if not services:
        print('No mens services found')
    else:
        for s in services:
            print('Deleting:', s.name)
            db.delete(s)
        db.commit()
        print('Deleted mens services')
finally:
    db.close()
