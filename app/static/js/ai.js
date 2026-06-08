// ── Existing: AI Coach ───────────────────────────────────────────────
async function getCoachAdvice() {
  const btn = document.getElementById('coach-btn');
  const resp = document.getElementById('coach-response');
  btn.disabled = true;
  btn.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
  resp.classList.remove('visible');
  try {
    const res = await fetch('/api/ai/coach');
    if (!res.ok) throw new Error(`Server error: ${res.status}`);
    const data = await res.json();
    resp.textContent = data.advice;
    resp.classList.add('visible');
  } catch (err) {
    resp.textContent = '⚠️ ' + err.message;
    resp.classList.add('visible');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="ti ti-sparkles"></i> Refresh advice';
  }
}

// ── Existing: AI Create Habits ───────────────────────────────────────
async function aiCreateHabits() {
  const goal = document.getElementById('goal-input').value.trim();
  if (!goal) return;
  const btn = document.getElementById('goal-btn');
  const result = document.getElementById('goal-result');
  btn.disabled = true;
  btn.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
  result.innerHTML = '';
  try {
    const res = await fetch('/api/ai/create-habits', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({goal})
    });
    if (!res.ok) throw new Error(`Server error: ${res.status}`);
    const data = await res.json();
    result.innerHTML = `<div style="background:rgba(61,186,126,.1);border:0.5px solid #3dba7e;border-radius:10px;padding:12px;font-size:13px;color:#3dba7e">
      <i class="ti ti-check"></i> Created ${data.created.length} habits: ${data.created.join(', ')}
    </div>`;
    loadHabits();
    setTimeout(() => closeModal('goal-modal'), 2000);
  } catch (err) {
    result.innerHTML = `<div style="background:rgba(226,85,85,.1);border:0.5px solid #e25555;border-radius:10px;padding:12px;font-size:13px;color:#e25555">⚠️ ${err.message}</div>`;
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="ti ti-sparkles"></i> Create my habit plan';
  }
}

// ── Existing: Mood Correlation ───────────────────────────────────────
async function getMoodCorrelation() {
  const el = document.getElementById('mood-insight');
  el.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
  try {
    const res = await fetch('/api/ai/mood-correlation');
    if (!res.ok) throw new Error(`Server error: ${res.status}`);
    const data = await res.json();
    el.innerHTML = `<p style="font-size:13px;color:#c8c8e0;line-height:1.7">${data.insight}</p>`;
  } catch (err) {
    el.innerHTML = `<p style="font-size:13px;color:#e25555">⚠️ ${err.message}</p>`;
  }
}

// ── Existing: Journal ────────────────────────────────────────────────
async function submitNote() {
  const content = document.getElementById('note-content').value.trim();
  if (!content) return;
  const btn = document.getElementById('note-btn');
  const resp = document.getElementById('note-ai-response');
  btn.disabled = true;
  btn.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
  resp.classList.remove('visible');
  try {
    const res = await fetch('/api/ai/journal', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({habit_id: noteHabitId, content})
    });
    if (!res.ok) throw new Error(`Server error: ${res.status}`);
    const data = await res.json();
    resp.textContent = '🤖 ' + data.ai_response;
    resp.classList.add('visible');
  } catch (err) {
    resp.textContent = '⚠️ ' + err.message;
    resp.classList.add('visible');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="ti ti-send"></i> Save & get AI response';
  }
}

// ── NEW: Daily Intention ─────────────────────────────────────────────
async function loadDailyIntention() {
  const box = document.getElementById('daily-intention');
  if (!box) return;
  box.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
  try {
    const res = await fetch('/api/ai/daily-intention');
    if (!res.ok) throw new Error(`Server error: ${res.status}`);
    const data = await res.json();
    box.innerHTML = `<i class="ti ti-sun" style="color:#f0a630;margin-right:8px"></i>${data.intention}`;
  } catch (err) {
    box.innerHTML = `<span style="color:#e25555">⚠️ ${err.message}</span>`;
  }
}

// ── NEW: Weekly Report Card ──────────────────────────────────────────
async function loadWeeklyReport() {
  const container = document.getElementById('report-container');
  const btn = document.getElementById('report-btn');
  if (!container) return;
  btn.disabled = true;
  btn.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
  container.innerHTML = '';
  try {
    const res = await fetch('/api/ai/weekly-report');
    if (!res.ok) throw new Error(`Server error: ${res.status}`);
    const r = await res.json();

    const gradeColor = g => {
      if (g.startsWith('A')) return '#3dba7e';
      if (g.startsWith('B')) return '#7c6af7';
      if (g.startsWith('C')) return '#f0a630';
      return '#e25555';
    };

    const habitCards = r.habit_grades.map(h => `
      <div style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid #2a2a3d">
        <div style="font-size:22px;font-weight:700;color:${gradeColor(h.grade)};min-width:36px">${h.grade}</div>
        <div>
          <div style="font-size:13px;font-weight:600;color:#e8e8f0">${h.name}</div>
          <div style="font-size:12px;color:#8888a0;margin-top:2px">${h.comment}</div>
        </div>
      </div>`).join('');

    container.innerHTML = `
      <div style="text-align:center;padding:20px 0 12px">
        <div style="font-size:56px;font-weight:800;color:${gradeColor(r.overall_grade)}">${r.overall_grade}</div>
        <div style="font-size:13px;color:#8888a0;margin-top:4px">Overall this week</div>
        <p style="font-size:13px;color:#c8c8e0;line-height:1.7;margin-top:12px">${r.overall_summary}</p>
      </div>
      <div style="margin:8px 0 16px">${habitCards}</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:8px">
        <div style="background:rgba(61,186,126,.08);border:0.5px solid #3dba7e33;border-radius:10px;padding:12px">
          <div style="font-size:11px;color:#3dba7e;font-weight:600;margin-bottom:4px">🏆 TOP WIN</div>
          <div style="font-size:12px;color:#c8c8e0">${r.top_win}</div>
        </div>
        <div style="background:rgba(124,106,247,.08);border:0.5px solid #7c6af733;border-radius:10px;padding:12px">
          <div style="font-size:11px;color:#7c6af7;font-weight:600;margin-bottom:4px">🎯 NEXT WEEK</div>
          <div style="font-size:12px;color:#c8c8e0">${r.focus_next_week}</div>
        </div>
      </div>
      <p style="font-size:13px;color:#8888a0;text-align:center;margin-top:16px;font-style:italic">${r.motivational_close}</p>`;
  } catch (err) {
    container.innerHTML = `<p style="color:#e25555;font-size:13px">⚠️ ${err.message}</p>`;
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="ti ti-refresh"></i> Regenerate report';
  }
}

// ── NEW: AI Chat Assistant ───────────────────────────────────────────
let chatHistory = [];

function toggleChat() {
  const win = document.getElementById('chat-window');
  win.classList.toggle('open');
  if (win.classList.contains('open') && chatHistory.length === 0) {
    appendChatMsg('assistant', "Hi! I'm your HabitAI coach 👋 Ask me anything about your habits, routines, or how to stay motivated!");
  }
}

function appendChatMsg(role, text) {
  const feed = document.getElementById('chat-feed');
  const div = document.createElement('div');
  div.className = `chat-msg ${role}`;
  div.textContent = text;
  feed.appendChild(div);
  feed.scrollTop = feed.scrollHeight;
}

async function sendChatMessage() {
  const input = document.getElementById('chat-input');
  const text = input.value.trim();
  if (!text) return;
  input.value = '';
  appendChatMsg('user', text);
  chatHistory.push({role: 'user', content: text});

  const feed = document.getElementById('chat-feed');
  const typingDiv = document.createElement('div');
  typingDiv.className = 'chat-msg assistant';
  typingDiv.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
  feed.appendChild(typingDiv);
  feed.scrollTop = feed.scrollHeight;

  try {
    const res = await fetch('/api/ai/chat', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({messages: chatHistory})
    });
    if (!res.ok) throw new Error(`Server error: ${res.status}`);
    const data = await res.json();
    typingDiv.remove();
    appendChatMsg('assistant', data.reply);
    chatHistory.push({role: 'assistant', content: data.reply});
  } catch (err) {
    typingDiv.remove();
    appendChatMsg('assistant', '⚠️ ' + err.message);
  }
}

function chatKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendChatMessage();
  }
}