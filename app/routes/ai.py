from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import date, timedelta
from app.models.models import Habit, HabitLog, MoodLog, HabitNote
from app.services.ai_service import (
    get_ai_coach, create_habits_from_goal, journal_ai_response,
    get_mood_correlation, get_daily_intention, get_weekly_report,
    chat_with_assistant
)
from app import db

ai_bp = Blueprint('ai', __name__)


def _build_habits_data(habits):
    from app.routes.habits import get_streak, get_last7
    return [
        {
            'name': h.name,
            'category': h.category,
            'done_today': bool(HabitLog.query.filter_by(habit_id=h.id, date=date.today()).first()),
            'streak': get_streak(h.id),
            'last7': get_last7(h.id)
        }
        for h in habits
    ]


def _build_week_logs(habits):
    today = date.today()
    week = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        done = HabitLog.query.filter(
            HabitLog.habit_id.in_([h.id for h in habits]),
            HabitLog.date == d
        ).count()
        week.append({'day': d.strftime('%a'), 'pct': round(done / len(habits) * 100) if habits else 0})
    return week


# ── Existing routes ──────────────────────────────────────────────────

@ai_bp.route('/api/ai/coach', methods=['GET'])
@login_required
def coach():
    habits = Habit.query.filter_by(user_id=current_user.id, is_active=True).all()
    habits_data = _build_habits_data(habits)
    week = _build_week_logs(habits)
    moods = MoodLog.query.filter_by(user_id=current_user.id).order_by(MoodLog.date.desc()).limit(7).all()
    mood_data = [{'date': str(m.date), 'mood': m.mood} for m in moods]
    tip = get_ai_coach(habits_data, {'week': week}, mood_data)
    return jsonify({'advice': tip})


@ai_bp.route('/api/ai/create-habits', methods=['POST'])
@login_required
def ai_create_habits():
    data = request.json
    goal = data.get('goal', '')
    habits = create_habits_from_goal(goal)
    created = []
    for h in habits:
        habit = Habit(
            user_id=current_user.id,
            name=h['name'],
            description=h.get('description', ''),
            category=h.get('category', 'other'),
            frequency=h.get('frequency', 'daily'),
            color=h.get('color', '#7c6af7'),
            icon=h.get('icon', 'ti-star')
        )
        db.session.add(habit)
        created.append(h['name'])
    db.session.commit()
    return jsonify({'created': created, 'message': f'{len(created)} habits created!'})


@ai_bp.route('/api/ai/journal', methods=['POST'])
@login_required
def journal_response():
    data = request.json
    habit_id = data.get('habit_id')
    note_content = data.get('content', '')
    from app.routes.habits import get_streak
    habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first_or_404()
    streak = get_streak(habit_id)
    ai_reply = journal_ai_response(habit.name, note_content, streak)
    note = HabitNote(habit_id=habit_id, content=note_content, ai_response=ai_reply, date=date.today())
    db.session.add(note)
    db.session.commit()
    return jsonify({'ai_response': ai_reply, 'note_id': note.id})


@ai_bp.route('/api/ai/mood-correlation', methods=['GET'])
@login_required
def mood_correlation():
    from app.routes.habits import get_last7
    habits = Habit.query.filter_by(user_id=current_user.id, is_active=True).all()
    habits_data = [{'name': h.name, 'last7': get_last7(h.id)} for h in habits]
    moods = MoodLog.query.filter_by(user_id=current_user.id).order_by(MoodLog.date.desc()).limit(14).all()
    mood_list = [{'date': str(m.date), 'mood': m.mood} for m in moods]
    result = get_mood_correlation(habits_data, mood_list)
    return jsonify({'insight': result})


# ── NEW: Daily Intention ─────────────────────────────────────────────

@ai_bp.route('/api/ai/daily-intention', methods=['GET'])
@login_required
def daily_intention():
    habits = Habit.query.filter_by(user_id=current_user.id, is_active=True).all()
    habits_data = _build_habits_data(habits)
    yesterday = date.today() - timedelta(days=1)
    last_mood_log = MoodLog.query.filter_by(user_id=current_user.id, date=yesterday).first()
    last_mood = last_mood_log.mood if last_mood_log else None
    intention = get_daily_intention(habits_data, last_mood)
    return jsonify({'intention': intention})


# ── NEW: Weekly Report Card ──────────────────────────────────────────

@ai_bp.route('/api/ai/weekly-report', methods=['GET'])
@login_required
def weekly_report():
    habits = Habit.query.filter_by(user_id=current_user.id, is_active=True).all()
    habits_data = _build_habits_data(habits)
    week_logs = _build_week_logs(habits)
    moods = MoodLog.query.filter_by(user_id=current_user.id).order_by(MoodLog.date.desc()).limit(7).all()
    mood_data = [{'date': str(m.date), 'mood': m.mood} for m in moods]
    report = get_weekly_report(habits_data, week_logs, mood_data)
    return jsonify(report)


# ── NEW: AI Chat Assistant ───────────────────────────────────────────

@ai_bp.route('/api/ai/chat', methods=['POST'])
@login_required
def chat():
    data = request.json
    messages_history = data.get('messages', [])
    habits = Habit.query.filter_by(user_id=current_user.id, is_active=True).all()
    habits_data = _build_habits_data(habits)
    moods = MoodLog.query.filter_by(user_id=current_user.id).order_by(MoodLog.date.desc()).limit(7).all()
    mood_data = [{'date': str(m.date), 'mood': m.mood} for m in moods]
    reply = chat_with_assistant(messages_history, habits_data, mood_data)
    return jsonify({'reply': reply})