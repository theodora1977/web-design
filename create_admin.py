import argparse
from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash

parser = argparse.ArgumentParser()
parser.add_argument('--username', default='admin')
parser.add_argument('--password', default='admin123')
args = parser.parse_args()

db = SessionLocal()
try:
    if db.query(User).filter(User.username == args.username).first():
        print('User already exists')
    else:
        user = User(username=args.username, hashed_password=get_password_hash(args.password), is_admin=True)
        db.add(user)
        db.commit()
        print('Created admin user:', args.username)
finally:
    db.close()
