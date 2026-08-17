from app import create_app, db
from app.models import User, ScamReport, ScanFile, UserFeedback

app = create_app()

def init_db():
    with app.app_context():
        db.create_all()
        print("Database initialized.")
        
        # Create admin user
        if not User.query.filter_by(username='admin').first():
            user = User(username='admin', email='admin@scamguard.ai')
            user.set_password('admin123')
            db.session.add(user)
            db.session.commit()
            print("Admin user created.")

if __name__ == '__main__':
    init_db()
