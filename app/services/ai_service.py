from openai import OpenAI
from config import Config
import json

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=Config.OPENROUTER_API_KEY,
)

MODEL = "openai/gpt-oss-120b:free"

def _chat(system, user, max_tokens=500):
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user}
        ]
    )
    return response.choices[0].message.content.strip()


def get_ai_coach(habits_data, analytics_data, mood_data):
    summary = f"""
User habit data:
Habits: {[h['name'] for h in habits_data]}
Today's completion: {sum(1 for h in habits_data if h['done_today'])}/{len(habits_data)}
Streaks: {[(h['name'], h['streak']) for h in habits_data]}
Weekly completion rates: {analytics_data.get('week', [])}
Recent moods (1-5): {[m['mood'] for m in mood_data]}
Habit rates (30 days): {analytics_data.get('habit_rates', [])}
"""
    return _chat(
        system="""You are a warm, insightful habit coach. Analyze the user's habit data and give:
1. One specific strength you notice
2. One honest, actionable improvement tip
3. A personalized motivational insight connecting their mood and habits
Keep it under 150 words. Be specific, not generic. Use the actual habit names.""",
        user=summary,
        max_tokens=500
    )


def create_habits_from_goal(goal_text):
    text = _chat(
        system="""You are a habit design expert. When given a goal, create 3-5 specific, actionable daily habits.
Respond ONLY with a valid JSON array. No markdown, no explanation, no code fences. Just raw JSON.
Format:
[{"name": "habit name", "description": "why this helps", "category": "health|fitness|mindfulness|learning|productivity|social|other", "frequency": "daily|weekdays|weekends|3x|2x", "icon": "ti-droplet|ti-run|ti-book|ti-moon|ti-barbell|ti-apple|ti-pencil|ti-music|ti-heart|ti-code|ti-brain|ti-sun", "color": "#7c6af7|#3dba7e|#e25555|#f0a630|#4d9de0|#e06bac|#2ec4b6|#e8714a"}]""",
        user=f"Create habits for this goal: {goal_text}",
        max_tokens=800
    )
    text = text.replace('```json', '').replace('```', '').strip()
    return json.loads(text)


def journal_ai_response(habit_name, note_content, recent_streak):
    return _chat(
        system="""You are an empathetic habit journal coach. Read the user's note about their habit and respond with:
- Acknowledge what they wrote specifically
- One insight or reflection
- One small encouragement
Keep it under 80 words. Warm and personal, not generic.""",
        user=f"Habit: {habit_name} (current streak: {recent_streak} days)\nJournal entry: {note_content}",
        max_tokens=200
    )


def get_mood_correlation(habits_data, mood_logs):
    if len(mood_logs) < 3:
        return "Log your mood for a few more days and I'll find patterns between your habits and how you feel!"
    summary = f"Habits: {[h['name'] for h in habits_data]}\nMood history (1=low, 5=great): {mood_logs}\nHabit completion history: {[(h['name'], h['last7']) for h in habits_data]}"
    return _chat(
        system="Analyze correlations between the user's mood and habit completion. Be specific about which habits seem to boost or correlate with better mood. Under 100 words, conversational tone.",
        user=summary,
        max_tokens=250
    )
# ── NEW: AI Daily Intention ──────────────────────────────────────────
 
def get_daily_intention(habits_data, last_mood):
    habits_today = [h['name'] for h in habits_data]
    mood_text = f"{last_mood}/5" if last_mood else "not logged yet"
    return _chat(
        system="""You are a mindful morning coach. Write a short, personal daily intention for the user.
- Exactly 2 sentences
- Reference 1-2 of their actual habit names naturally
- Make it feel warm, energizing, and specific to them
- Do NOT use generic phrases like 'seize the day' or 'make it count'
- Write as if speaking directly to them""",
        user=f"Today's habits to work on: {habits_today}\nYesterday's mood: {mood_text}\nWrite their morning intention.",
        max_tokens=100
    )
 
 
# ── NEW: Weekly Report Card ──────────────────────────────────────────
 
def get_weekly_report(habits_data, week_logs, mood_data):
    summary = f"""
Habits and their last 7 days completion:
{[(h['name'], h['last7']) for h in habits_data]}
 
Daily completion rates this week: {week_logs}
Mood this week (1-5): {[m['mood'] for m in mood_data]}
Streaks: {[(h['name'], h['streak']) for h in habits_data]}
"""
    text = _chat(
        system="""You are a habit coach writing a weekly report card. Respond ONLY with valid JSON, no markdown, no explanation.
Format:
{
  "overall_grade": "B+",
  "overall_summary": "2-3 sentence overall week summary",
  "habit_grades": [
    {"name": "habit name", "grade": "A", "comment": "one specific sentence about this habit"}
  ],
  "top_win": "The single best thing they did this week",
  "focus_next_week": "One specific thing to improve next week",
  "motivational_close": "One warm closing sentence"
}""",
        user=summary,
        max_tokens=700
    )
    text = text.replace('```json', '').replace('```', '').strip()
    return json.loads(text)
 
 
# ── NEW: AI Chat Assistant ───────────────────────────────────────────
 
def chat_with_assistant(messages_history, habits_data, mood_data):
    habits_context = f"""
You have full context about this user's habits:
Habits: {[(h['name'], h['category'], 'done today' if h['done_today'] else 'not done') for h in habits_data]}
Streaks: {[(h['name'], h['streak']) for h in habits_data]}
Recent moods (1-5): {[m['mood'] for m in mood_data[-5:]]}
Today's completion: {sum(1 for h in habits_data if h['done_today'])}/{len(habits_data)} habits done
"""
    system = f"""You are a friendly, knowledgeable habit coach assistant inside a habit tracking app called HabitAI.
{habits_context}
Rules:
- Keep responses concise (under 120 words) unless asked for detail
- Be warm, personal, and encouraging
- Reference their actual habit names when relevant
- You can help with: habit advice, motivation, creating routines, explaining habit science, analyzing their data
- If asked something unrelated to habits/wellbeing, gently redirect"""
 
    api_messages = [{"role": "system", "content": system}]
    for msg in messages_history:
        api_messages.append({"role": msg["role"], "content": msg["content"]})
 
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=300,
        messages=api_messages
    )
    return response.choices[0].message.content.strip()