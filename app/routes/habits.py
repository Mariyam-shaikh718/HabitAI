from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import date, timedelta
from app import db
from app.models.models import Habit, HabitLog, HabitNote, MoodLog

habits_bp = Blueprint('habits', __name__)

@habits_bp.route('/')
@login_required
def index():
    return render_template('index.html')

@habits_bp.route('/api/habits', methods=['GET'])
@login_required
def get_habits():
    habits = Habit.query.filter_by(user_id=current_user.id, is_active=True).all()
    today = date.today()
    result = []
    for h in habits:
        log = HabitLog.query.filter_by(habit_id=h.id, date=today).first()
        streak = get_streak(h.id)
        last7 = get_last7(h.id)
        result.append({
            'id': h.id, 'name': h.name, 'category': h.category,
            'frequency': h.frequency, 'color': h.color, 'icon': h.icon,
            'done_today': bool(log), 'streak': streak, 'last7': last7,
            'description': h.description or ''
        })
    return jsonify(result)

@habits_bp.route('/api/habits', methods=['POST'])
@login_required
def create_habit():
    data = request.json
    habit = Habit(
        user_id=current_user.id,
        name=data['name'],
        description=data.get('description', ''),
        category=data.get('category', 'other'),
        frequency=data.get('frequency', 'daily'),
        color=data.get('color', '#7c6af7'),
        icon=data.get('icon', 'ti-star')
    )
    db.session.add(habit)
    db.session.commit()
    return jsonify({'id': habit.id, 'name': habit.name, 'message': 'Habit created'})

@habits_bp.route('/api/habits/<int:habit_id>', methods=['DELETE'])
@login_required
def delete_habit(habit_id):
    habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first_or_404()
    habit.is_active = False
    db.session.commit()
    return jsonify({'message': 'Deleted'})

@habits_bp.route('/api/habits/<int:habit_id>/toggle', methods=['POST'])
@login_required
def toggle_habit(habit_id):
    habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first_or_404()
    today = date.today()
    log = HabitLog.query.filter_by(habit_id=habit_id, date=today).first()
    if log:
        db.session.delete(log)
        done = False
    else:
        log = HabitLog(habit_id=habit_id, date=today)
        db.session.add(log)
        done = True
    db.session.commit()
    return jsonify({'done': done, 'streak': get_streak(habit_id)})

@habits_bp.route('/api/habits/<int:habit_id>/note', methods=['POST'])
@login_required
def save_note(habit_id):
    data = request.json
    note = HabitNote(habit_id=habit_id, content=data['content'], date=date.today())
    db.session.add(note)
    db.session.commit()
    return jsonify({'id': note.id, 'message': 'Note saved'})

@habits_bp.route('/api/habits/<int:habit_id>/notes', methods=['GET'])
@login_required
def get_notes(habit_id):
    notes = HabitNote.query.filter_by(habit_id=habit_id).order_by(HabitNote.created_at.desc()).limit(5).all()
    return jsonify([{'id': n.id, 'content': n.content, 'ai_response': n.ai_response, 'date': str(n.date)} for n in notes])

@habits_bp.route('/api/mood', methods=['POST'])
@login_required
def log_mood():
    data = request.json
    today = date.today()
    mood = MoodLog.query.filter_by(user_id=current_user.id, date=today).first()
    if mood:
        mood.mood = data['mood']
        mood.note = data.get('note', '')
    else:
        mood = MoodLog(user_id=current_user.id, mood=data['mood'], note=data.get('note', ''), date=today)
        db.session.add(mood)
    db.session.commit()
    return jsonify({'message': 'Mood logged'})

@habits_bp.route('/api/analytics', methods=['GET'])
@login_required
def get_analytics():
    habits = Habit.query.filter_by(user_id=current_user.id, is_active=True).all()
    today = date.today()
    week_data = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        total = len(habits)
        done = HabitLog.query.filter(
            HabitLog.habit_id.in_([h.id for h in habits]),
            HabitLog.date == d
        ).count()
        week_data.append({'date': str(d), 'day': d.strftime('%a'), 'done': done, 'total': total,
                          'pct': round(done/total*100) if total else 0})
    moods = MoodLog.query.filter_by(user_id=current_user.id).order_by(MoodLog.date.desc()).limit(7).all()
    mood_data = [{'date': str(m.date), 'mood': m.mood} for m in reversed(moods)]
    habit_rates = []
    for h in habits:
        logs = HabitLog.query.filter(HabitLog.habit_id == h.id,
            HabitLog.date >= today - timedelta(days=30)).count()
        habit_rates.append({'name': h.name, 'color': h.color, 'rate': round(logs/30*100)})
    return jsonify({'week': week_data, 'moods': mood_data, 'habit_rates': habit_rates})

def get_streak(habit_id):
    streak = 0
    d = date.today()
    while True:
        log = HabitLog.query.filter_by(habit_id=habit_id, date=d).first()
        if log:
            streak += 1
            d -= timedelta(days=1)
        else:
            break
        if streak > 365:
            break
    return streak

def get_last7(habit_id):
    today = date.today()
    result = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        log = HabitLog.query.filter_by(habit_id=habit_id, date=d).first()
        result.append({'date': str(d), 'done': bool(log)})
    return result