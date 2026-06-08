const COLORS = ['#7c6af7','#3dba7e','#e25555','#f0a630','#4d9de0','#e06bac','#2ec4b6','#e8714a'];
const ICONS = ['ti-droplet','ti-run','ti-book','ti-moon','ti-barbell','ti-apple','ti-pencil','ti-music','ti-heart','ti-code','ti-brain','ti-sun'];
const FREQ_LABELS = {daily:'Daily',weekdays:'Weekdays',weekends:'Weekends','3x':'3×/week','2x':'2×/week'};

let selColor = COLORS[0], selIcon = ICONS[0], noteHabitId = null;

function init() {
  const now = new Date();
  const hr = now.getHours();
 document.getElementById('greeting-time').textContent = hr < 5 ? 'night' : hr < 12 ? 'morning' : hr < 17 ? 'afternoon' : hr < 21 ? 'evening' : 'night';
  document.getElementById('today-date').textContent = now.toLocaleDateString('en-US',{weekday:'long',month:'long',day:'numeric',year:'numeric'});
  renderPickers();
  loadHabits();
  loadDailyIntention();
}

function renderPickers() {
  document.getElementById('color-picker').innerHTML = COLORS.map(c =>
    `<div class="c-dot${c===selColor?' sel':''}" style="background:${c}" onclick="selColor='${c}';renderPickers()"></div>`
  ).join('');
  document.getElementById('icon-picker').innerHTML = ICONS.map(ic =>
    `<div class="i-opt${ic===selIcon?' sel':''}" onclick="selIcon='${ic}';renderPickers()"><i class="ti ${ic}"></i></div>`
  ).join('');
}

async function loadHabits() {
  const res = await fetch('/api/habits');
  const habits = await res.json();
  renderHabits(habits);
  const done = habits.filter(h => h.done_today).length;
  const due = habits.length;
  document.getElementById('s-done').textContent = done;
  document.getElementById('s-total').textContent = due;
  const best = habits.length ? Math.max(0, ...habits.map(h => h.streak)) : 0;
  document.getElementById('s-streak').textContent = best;
}

function renderHabits(habits) {
  const grid = document.getElementById('habits-grid');
  if (!habits.length) {
    grid.innerHTML = `<div class="empty-state" style="grid-column:1/-1"><i class="ti ti-sparkles"></i><h3>No habits yet</h3><p>Add your first habit or let AI create a plan for you.</p></div>`;
    return;
  }
  grid.innerHTML = habits.map(h => {
    const cal = h.last7.map(d => `<div class="cal-dot${d.done?' done':''}" style="${d.done?`background:${h.color};opacity:1`:''}"></div>`).join('');
    return `<div class="habit-card cat-${h.category}" id="hcard-${h.id}" style="--hcolor:${h.color}">
  <div class="habit-top">
    <div class="habit-icon-wrap" style="background:${h.color}22"><i class="ti ${h.icon}" style="color:${h.color}"></i></div>
    <div class="habit-info">
      <div class="habit-name">${h.name}</div>
      <div class="habit-cat">${h.category} · ${FREQ_LABELS[h.frequency]||h.frequency}</div>
    </div>
    <button class="check-btn${h.done_today?' done':''}" onclick="toggleHabit(${h.id},this)" aria-label="Toggle habit">
      <i class="ti ${h.done_today?'ti-check':'ti-circle'}"></i>
    </button>
  </div>
  ${h.streak>0?`<div class="streak-row"><i class="ti ti-flame"></i>${h.streak}-day streak</div>`:''}
  <div class="mini-cal">${cal}</div>
  <div class="habit-actions">
    <button class="btn-ghost" onclick="openNote(${h.id},'${h.name}')"><i class="ti ti-notes"></i> Journal</button>
    <button class="btn-del" onclick="deleteHabit(${h.id})" aria-label="Delete"><i class="ti ti-trash"></i></button>
  </div>
</div>`;
  }).join('');
}

async function toggleHabit(id, btn) {
  const res = await fetch(`/api/habits/${id}/toggle`, {method:'POST'});
  const data = await res.json();
  btn.classList.toggle('done', data.done);
  btn.querySelector('i').className = `ti ${data.done?'ti-check':'ti-circle'}`;
  btn.classList.add('pop');
  setTimeout(()=>btn.classList.remove('pop'),300);
  loadHabits();
}

async function addHabit() {
  const name = document.getElementById('new-name').value.trim();
  if (!name) return;
  await fetch('/api/habits', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({name, description:document.getElementById('new-desc').value,
      category:document.getElementById('new-cat').value, frequency:document.getElementById('new-freq').value,
      color:selColor, icon:selIcon})
  });
  closeModal('add-modal');
  document.getElementById('new-name').value = '';
  loadHabits();
}

async function deleteHabit(id) {
  if (!confirm('Delete this habit?')) return;
  await fetch(`/api/habits/${id}`, {method:'DELETE'});
  loadHabits();
}

async function logMood(val) {
  document.querySelectorAll('.mood-btns button').forEach((b,i)=>b.classList.toggle('selected',i+1===val));
  await fetch('/api/mood', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mood:val})});
}

function openNote(id, name) {
  noteHabitId = id;
  document.getElementById('note-modal-title').textContent = `Journal — ${name}`;
  document.getElementById('note-content').value = '';
  document.getElementById('note-ai-response').classList.remove('visible');
  openModal('note-modal');
}

async function submitNote() {
  const content = document.getElementById('note-content').value.trim();
  if (!content) return;
  const btn = document.getElementById('note-btn');
  btn.disabled = true;
  btn.innerHTML = `<div class="typing-dots"><span></span><span></span><span></span></div>`;
  const res = await fetch('/api/ai/journal', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({habit_id:noteHabitId, content})
  });
  const data = await res.json();
  const resp = document.getElementById('note-ai-response');
  resp.textContent = '🤖 ' + data.ai_response;
  resp.classList.add('visible');
  btn.disabled = false;
  btn.innerHTML = '<i class="ti ti-send"></i> Save & get AI response';
}

function switchTab(id, tabId) {
  document.querySelectorAll('.tab-content').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.getElementById('tab-'+id).classList.add('active');
  event.currentTarget.classList.add('active');
  if (id === 'analytics') loadAnalytics();
}

function openModal(id){ document.getElementById(id).classList.add('open'); }
function closeModal(id){ document.getElementById(id).classList.remove('open'); }
function openAddModal(){ renderPickers(); openModal('add-modal'); }
function openGoalModal(){ openModal('goal-modal'); }

document.addEventListener('DOMContentLoaded', init);
