from app.database import SessionLocal, engine
from app.models import Base, Service, Gallery, Review
import os

# Ensure tables exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    # Add sample services if none
    if db.query(Service).count() == 0:
        services = [
            Service(name='Ankara Dress (Tailor-made)', description='Custom ankara dress tailored to your measurements.', price=8000.0),
            Service(name='Alteration & Repair', description='Quick alteration, hemming, and repairs.', price=2000.0),
            Service(name='Bridal Gown', description='Full bridal gown design and stitching.', price=35000.0),
        ]
        db.add_all(services)
        db.commit()
        print('Added sample services')

    # Add sample gallery items if none
    if db.query(Gallery).count() == 0:
        upload_dir = os.path.join(os.path.dirname(__file__), 'uploads')
        samples = [
            {'title':'Ankara Blue', 'category':'Ankara', 'price':5000.0, 'description':'Classic blue ankara', 'image':'ankara 2.jpn'},
            {'title':'Ankara Pink', 'category':'Ankara', 'price':6500.0, 'description':'Vibrant pink ankara', 'image':'ankara 3.jpn'},
        ]
        for s in samples:
            # only add if file exists
            path = os.path.join(upload_dir, s['image'])
            if os.path.exists(path):
                g = Gallery(title=s['title'], category=s['category'], price=s['price'], description=s['description'], image=s['image'])
                db.add(g)
        db.commit()
        print('Added sample gallery items')

    # Add sample reviews if none
    if db.query(Review).count() == 0:
        revs = [
            Review(reviewer_name='Ada', reviewer_email='ada@example.com', rating=5, message='Lovely workmanship!'),
            Review(reviewer_name='Ngozi', reviewer_email='ngozi@example.com', rating=4, message='Great fit and fast turnaround.'),
        ]
        db.add_all(revs)
        db.commit()
        print('Added sample reviews')

finally:
    db.close()

print('Seeding complete')
