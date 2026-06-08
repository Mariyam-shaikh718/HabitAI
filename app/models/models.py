from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime, date

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    habits = db.relationship('Habit', backref='user', lazy=True, cascade='all, delete-orphan')
    moods = db.relationship('MoodLog', backref='user', lazy=True, cascade='all, delete-orphan')

class Habit(db.Model):
    __tablename__ = 'habits'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), default='other')
    frequency = db.Column(db.String(20), default='daily')
    color = db.Column(db.String(10), default='#7c6af7')
    icon = db.Column(db.String(50), default='ti-star')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    logs = db.relationship('HabitLog', backref='habit', lazy=True, cascade='all, delete-orphan')
    notes = db.relationship('HabitNote', backref='habit', lazy=True, cascade='all, delete-orphan')

class HabitLog(db.Model):
    __tablename__ = 'habit_logs'
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habits.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    completed = db.Column(db.Boolean, default=True)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('habit_id', 'date'),)

class HabitNote(db.Model):
    __tablename__ = 'habit_notes'
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habits.id'), nullable=False)
    date = db.Column(db.Date, default=date.today)
    content = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MoodLog(db.Model):
    __tablename__ = 'mood_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, default=date.today, nullable=False)
    mood = db.Column(db.Integer, nullable=False)  # 1-5
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'date'),)