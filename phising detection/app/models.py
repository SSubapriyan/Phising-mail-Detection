from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    reports = db.relationship('ScamReport', backref='author', lazy='dynamic')
    feedbacks = db.relationship('UserFeedback', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

import json

class ScamReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=True)
    content = db.Column(db.Text, nullable=False)
    ocr_text = db.Column(db.Text, nullable=True)
    
    # ML Results
    is_scam = db.Column(db.Boolean, default=False)
    confidence_score = db.Column(db.Float, default=0.0)
    scam_type = db.Column(db.String(50))
    
    # Professional Upgrades
    safety_grade = db.Column(db.String(5)) # A, B, C, D
    risk_factors = db.Column(db.Text) # JSON string of detected factors
    explanation = db.Column(db.Text) # AI generated explanation
    company_name = db.Column(db.String(120))
    company_status = db.Column(db.String(50)) # Verified, Suspicious, Unknown
    
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    files = db.relationship('ScanFile', backref='report', lazy='dynamic')
    
    # Metadata
    report_file_path = db.Column(db.String(255), nullable=True)

    def set_risk_factors(self, factors):
        self.risk_factors = json.dumps(factors)

    def get_risk_factors(self):
        return json.loads(self.risk_factors) if self.risk_factors else []

    def __repr__(self):
        return f'<ScamReport {self.id} - Grade {self.safety_grade}>'

class ScanFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(10)) # png, pdf, etc.
    report_id = db.Column(db.Integer, db.ForeignKey('scam_report.id'))

    def __repr__(self):
        return f'<ScanFile {self.filename}>'

class UserFeedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('scam_report.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_correct = db.Column(db.Boolean) # User's confirmation if the AI was right
    comments = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<UserFeedback {self.id} for Report {self.report_id}>'
