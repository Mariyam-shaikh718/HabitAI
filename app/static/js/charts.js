let weekChart = null, moodChart = null;

async function loadAnalytics() {
  const res = await fetch('/api/analytics');
  const data = await res.json();
  renderWeekChart(data.week);
  renderMoodChart(data.moods);
  renderHabitRates(data.habit_rates);
}

function renderWeekChart(week) {
  const ctx = document.getElementById('chart-week').getContext('2d');
  if (weekChart) weekChart.destroy();
  weekChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: week.map(w => w.day),
      datasets: [{
        data: week.map(w => w.pct),
        backgroundColor: 'rgba(124,106,247,.6)',
        borderColor: '#7c6af7',
        borderWidth: 1,
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false }, tooltip: { callbacks: { label: c => c.parsed.y + '%' } } },
      scales: {
        y: { min: 0, max: 100, ticks: { color: '#8888a0', callback: v => v + '%' }, grid: { color: 'rgba(255,255,255,.04)' } },
        x: { ticks: { color: '#8888a0' }, grid: { display: false } }
      }
    }
  });
}

function renderMoodChart(moods) {
  const ctx = document.getElementById('chart-mood').getContext('2d');
  if (moodChart) moodChart.destroy();
  if (!moods.length) return;
  const labels = ['😞','😕','😐','🙂','😄'];
  moodChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: moods.map(m => new Date(m.date).toLocaleDateString('en-US',{weekday:'short'})),
      datasets: [{
        data: moods.map(m => m.mood),
        borderColor: '#f0a630',
        backgroundColor: 'rgba(240,166,48,.1)',
        borderWidth: 2,
        tension: 0.4,
        pointBackgroundColor: '#f0a630',
        pointRadius: 5,
        fill: true
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false }, tooltip: { callbacks: { label: c => labels[c.parsed.y-1] || c.parsed.y } } },
      scales: {
        y: { min: 1, max: 5, ticks: { color: '#8888a0', stepSize: 1, callback: v => labels[v-1]||'' }, grid: { color: 'rgba(255,255,255,.04)' } },
        x: { ticks: { color: '#8888a0' }, grid: { display: false } }
      }
    }
  });
}

function renderHabitRates(rates) {
  const el = document.getElementById('habit-rates');
  if (!rates.length) { el.innerHTML = '<p style="color:#8888a0;font-size:13px">No habits tracked yet.</p>'; return; }
  el.innerHTML = rates.map(r => `
    <div class="rate-row">
      <span class="rate-name">${r.name}</span>
      <div class="rate-bg"><div class="rate-fill" style="width:${r.rate}%;background:${r.color}"></div></div>
      <span class="rate-pct">${r.rate}%</span>
    </div>`).join('');
}