// ─── DATA ───
const ans = {};
const totalScreens = 21;
 
// ─── PROGRESS BAR ───
function updateBar(screenIdx) {
  const pct = Math.round((screenIdx / (totalScreens - 1)) * 100);
  document.getElementById('topFill').style.width = pct + '%';
}
 
// ─── SCROLL TRACKING ───
const allScreens = document.querySelectorAll('.screen');
const sObs = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      const idx = parseInt(e.target.dataset.s || '0');
      updateBar(idx);
    }
  });
}, { threshold: 0.5 });
allScreens.forEach(s => sObs.observe(s));
 
// ─── THOUGHT BUBBLES ───
const tBubs = document.querySelectorAll('.tbub');
const tObs = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      const list = e.target.closest('.tlist');
      if (list) list.querySelectorAll('.tbub').forEach((t, i) => setTimeout(() => t.classList.add('vis'), i * 280));
      tObs.unobserve(e.target);
    }
  });
}, { threshold: 0.3 });
if (tBubs[0]) tObs.observe(tBubs[0]);
 
// ─── SINGLE SELECT ───
function pick(el, key) {
  const parent = el.closest('.opts');
  parent.querySelectorAll('.opt').forEach(o => o.classList.remove('picked'));
  el.classList.add('picked');
  ans[key] = el.textContent.replace('✓','').trim();
  // Enable next button
  const nb = document.getElementById('nb-' + key);
  if (nb) nb.classList.add('ready');
}
 
// ─── MULTI SELECT ───
function pickMulti(el, key) {
  el.classList.toggle('picked');
  const parent = el.closest('.opts');
  const selected = parent.querySelectorAll('.picked');
  ans[key] = Array.from(selected).map(o => o.textContent.replace('✓','').trim());
  const nb = document.getElementById('nb-' + key);
  if (nb) {
    if (selected.length > 0) nb.classList.add('ready');
    else nb.classList.remove('ready');
  }
}
 
// ─── NEXT BUTTON ───
function goNext(targetDataS) {
  const target = document.querySelector(`[data-s="${targetDataS}"]`);
  if (target) target.scrollIntoView({ behavior: 'smooth' });
}
 
// ─── FORM ───
function fmtPh(input) {
  let v = input.value.replace(/\D/g, '');
  if (v.length > 9) v = v.slice(0, 9);
  if (v.length > 5) v = v.slice(0,2)+' '+v.slice(2,5)+' '+v.slice(5);
  else if (v.length > 2) v = v.slice(0,2)+' '+v.slice(2);
  input.value = v;
}
 
function checkReady() {
  const n = document.getElementById('fname').value.trim();
  const p = document.getElementById('fphone').value.replace(/\s/g,'');
  document.getElementById('ctaBtn').disabled = !(n.length > 0 && p.length >= 9);
}
 
function submitAll() {
  const name = document.getElementById('fname').value.trim();
  const phone = '+27' + document.getElementById('fphone').value.replace(/\s/g,'');
  const scamStory = document.getElementById('scam-story')?.value?.trim() || '';
  const openTrust = document.getElementById('open-trust')?.value?.trim() || '';
 
  const payload = {
    name,
    phone,
    age: ans.age || '',
    frequency: ans.freq || '',
    bought_online: ans.online || '',
    safety_feeling: ans.safety || '',
    scam_experience: ans.scammed || '',
    scam_story: scamStory,
    top_concerns: Array.isArray(ans.concerns) ? ans.concerns.join(', ') : '',
    stop_using: ans.stopuse || '',
    cancelled_deal: ans.cancelled || '',
    wanted_features: Array.isArray(ans.features) ? ans.features.join(', ') : '',
    price_willing: ans.price || '',
    when_pay: ans.whenpay || '',
    trust_insight: openTrust,
    timestamp: new Date().toISOString()
  };
 
  // ── GOOGLE SHEETS WEBHOOK ──
  // Uncomment and replace URL when ready:
  // fetch('YOUR_GOOGLE_SHEETS_WEBHOOK_URL', {
  //   method: 'POST',
  //   mode: 'no-cors',
  //   headers: { 'Content-Type': 'application/json' },
  //   body: JSON.stringify(payload)
  // });
 
  console.log('SafeTrade full submission:', JSON.stringify(payload, null, 2));
 
  // Show thank you
  document.querySelector('[data-s="19"]').style.display = 'none';
  const thanks = document.getElementById('thanksScreen');
  thanks.classList.remove('hidden');
  thanks.scrollIntoView({ behavior: 'smooth' });
  updateBar(20);
}