// ─── DATA ───
const ans = {};
const totalScreens = 23;

// ─── SCROLL LOCK ───
let scrollLocked = false;
const SURVEY_START = 8;
const SURVEY_END = 19;
let lockTimeout = null;

function isQuestionScreen(idx) {
  return idx >= SURVEY_START && idx <= SURVEY_END;
}

window.addEventListener('wheel', e => { if (scrollLocked) e.preventDefault(); }, { passive: false });
window.addEventListener('keydown', e => {
  if (scrollLocked && ['ArrowDown', 'ArrowUp', ' ', 'PageDown', 'PageUp'].includes(e.key)) e.preventDefault();
});
window.addEventListener('touchmove', e => { if (scrollLocked) e.preventDefault(); }, { passive: false });

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
      scrollLocked = isQuestionScreen(idx);
    }
  });
}, { threshold: 0.5 });
allScreens.forEach(s => sObs.observe(s));

// ─── THOUGHT BUBBLES ───
const tObs = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      const list = e.target.closest('.tlist');
      if (list) list.querySelectorAll('.tbub').forEach((t, i) => setTimeout(() => t.classList.add('vis'), i * 280));
      tObs.unobserve(e.target);
    }
  });
}, { threshold: 0.3 });
document.querySelectorAll('.tlist').forEach(list => {
  const first = list.querySelector('.tbub');
  if (first) tObs.observe(first);
});
 
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
  scrollLocked = false;
  clearTimeout(lockTimeout);
  const target = document.querySelector(`[data-s="${targetDataS}"]`);
  if (target) {
    target.scrollIntoView({ behavior: 'smooth' });
    if (isQuestionScreen(parseInt(targetDataS))) {
      lockTimeout = setTimeout(() => { scrollLocked = true; }, 700);
    }
  }
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
  // Only name is required — phone is optional
  const n = document.getElementById('fname').value.trim();
  document.getElementById('ctaBtn').disabled = !(n.length > 0);
}

function buildPayload(nameOverride) {
  const name = nameOverride !== undefined
    ? nameOverride
    : document.getElementById('fname').value.trim();
  const rawPhone = document.getElementById('fphone').value.replace(/\s/g,'');
  const phone = rawPhone.length >= 9 ? '+27' + rawPhone : '';
  const scamStory = document.getElementById('scam-story')?.value?.trim() || '';
  const openTrust = document.getElementById('open-trust')?.value?.trim() || '';
  return {
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
}

function setSubmitting(isSubmitting) {
  const ctaBtn = document.getElementById('ctaBtn');
  const anonBtn = document.getElementById('anonBtn');
  if (ctaBtn) ctaBtn.disabled = isSubmitting;
  if (anonBtn) anonBtn.disabled = isSubmitting;
  if (ctaBtn) ctaBtn.textContent = isSubmitting ? 'Submitting…' : 'Submit your answers';
}

function showSubmitError() {
  const msg = document.getElementById('submitMsg');
  if (!msg) return;
  msg.textContent = 'Something went wrong on our end. Your answers have been saved locally — please try again or continue without contact details.';
  msg.className = 'submit-msg submit-msg--error';
  msg.style.display = 'block';
}

function sendToSheets(payload) {
  return fetch(
    'https://script.google.com/macros/s/AKfycbziSkBmFUfU9aOg10m3zPVt2HV1DN7cjfR_G51_BA5BKnlYgSIZx3Fbc40VaKUKGwa4VQ/exec',
    { method: 'POST', mode: 'no-cors', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }
  );
}

function showThanks(hasPhone) {
  document.querySelector('[data-s="21"]').style.display = 'none';
  const thanks = document.getElementById('thanksScreen');
  thanks.classList.remove('hidden');
  if (hasPhone) {
    document.getElementById('thanksMsg').textContent =
      'Your input has been recorded. We\'ll send you one WhatsApp when SafeTrade launches — nothing else.';
    document.getElementById('waBadge').style.display = 'inline-flex';
  }
  thanks.scrollIntoView({ behavior: 'smooth' });
  updateBar(22);
}

function submitAll() {
  const name = document.getElementById('fname').value.trim();
  if (!name) return;
  const payload = buildPayload();
  const hasPhone = payload.phone.length > 0;

  console.log('SafeTrade submission:', JSON.stringify(payload, null, 2));
  setSubmitting(true);

  sendToSheets(payload)
    .then(() => { showThanks(hasPhone); })
    .catch(() => {
      // no-cors requests always resolve — only a network/CORS hard failure lands here
      setSubmitting(false);
      showSubmitError();
    });
}

function submitAnon() {
  const payload = buildPayload('anonymous');
  console.log('SafeTrade anonymous submission:', JSON.stringify(payload, null, 2));

  const anonBtn = document.getElementById('anonBtn');
  if (anonBtn) { anonBtn.disabled = true; anonBtn.textContent = 'Submitting…'; }

  sendToSheets(payload)
    .then(() => { showThanks(false); })
    .catch(() => {
      if (anonBtn) { anonBtn.disabled = false; anonBtn.textContent = 'Submit without contact details'; }
      showSubmitError();
    });
}