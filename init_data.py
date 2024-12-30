from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User
from auth import create_user

def init_default_users(db_url):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    # Check if admin user exists
    admin_exists = db.query(User).filter(User.username == "admin").first()
    if not admin_exists:
        create_user(
            db=db,
            username="admin",
            password="admin123",
            email="admin@homecredit.vn",
            full_name="Admin",
            department="HR",
            role="admin"
        )
    
    # Create default user ngoc.truc
    user_exists = db.query(User).filter(User.username == "ngoc.truc").first()
    if not user_exists:
        create_user(
            db=db,
            username="ngoc.truc",
            password="ngoctruc",
            email="ngoc.truc@homecredit.vn",
            full_name="Ngoc Truc",
            department="HR",
            role="admin"
        )
    
    db.close()

if __name__ == "__main__":
    init_default_users("sqlite:///360review.db") 