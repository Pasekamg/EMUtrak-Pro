// --- config & helpers ---------------------------------------------------------
const STORE = { api:'emutrak_api_base', token:'emutrak_token', role:'emutrak_role' };
const $  = (s)=>document.querySelector(s);
const esc = (s)=>String(s ?? '').replace(/[&<>"']/g, m=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[m]));
const human = (iso)=> iso ? new Date(iso).toLocaleString() : '';
const status = (msg, ms=2000)=>{ const el=$('#status'); if(!el) return; el.textContent=msg||''; if(msg) setTimeout(()=>el.textContent='',ms); };

// Dates: accept MM/DD/YYYY or YYYY-MM-DD and always output YYYY-MM-DD
function normalizeDate(input){
  if(!input) return '';
  const s = String(input).trim();
  if (/^\d{4}-\d{2}-\d{2}$/.test(s)) return s; // already ISO
  const m = s.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/); // MM/DD/YYYY
  if (m){ const mm=m[1].padStart(2,'0'), dd=m[2].padStart(2,'0'), yyyy=m[3]; return `${yyyy}-${mm}-${dd}`; }
  const d = new Date(s); if(!isNaN(d)) return new Date(d.getTime()-d.getTimezoneOffset()*60000).toISOString().slice(0,10);
  return s;
}
function computeDays(adm){
  if(!adm) return '';
  const [y,m,d] = normalizeDate(adm).split('-').map(Number);
  if(!y||!m||!d) return '';
  const startUTC = Date.UTC(y, m-1, d);
  const now = new Date();
  const todayUTC = Date.UTC(now.getFullYear(), now.getMonth(), now.getDate());
  return Math.max(0, Math.floor((todayUTC - startUTC)/86400000));
}
async function jsonOrText(res){
  const ct = res.headers.get('content-type')||'';
  return ct.includes('application/json') ? await res.json() : await res.text();
}
function firstError(obj){
  if(typeof obj==='string') return obj;
  if(obj && typeof obj==='object'){
    const k = Object.keys(obj)[0];
    if(k && Array.isArray(obj[k])) return `${k}: ${obj[k][0]}`;
    if(k) return `${k}: ${obj[k]}`;
  }
  return 'Unknown error';
}

// --- persisted session --------------------------------------------------------
let API   = localStorage.getItem(STORE.api)   || '';
let token = localStorage.getItem(STORE.token) || '';
let role  = localStorage.getItem(STORE.role)  || 'viewer';

$('#apiBase').value = API;
$('#saveApi').onclick = ()=>{ API = $('#apiBase').value.trim(); localStorage.setItem(STORE.api, API); alert('Saved API base'); };

// --- auth dialog --------------------------------------------------------------
const authDialog = $('#authDialog');
$('#authBtn').onclick = ()=> authDialog.showModal();
$('#closeAuth').onclick = ()=> authDialog.close();

$('#doAuth').onclick = async ()=>{
  if(!API) return alert('Set API base first.');
  const u = $('#u').value.trim();
  const p = $('#p').value.trim();
  const fallbackRole = $('#role').value || 'viewer';
  try{
    const res = await fetch(`${API}/api/auth/token/`, {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({username:u, password:p})
    });
    if(!res.ok){ const err = await jsonOrText(res); throw new Error(firstError(err)); }
    const obj = await res.json();
    token = obj.access || ''; if(!token) throw new Error('No access token returned');
    localStorage.setItem(STORE.token, token);

    // role from JWT payload if present; otherwise fallback selector
    try{ role = JSON.parse(atob(token.split('.')[1]||''))?.role || fallbackRole; }catch{ role = fallbackRole; }
    localStorage.setItem(STORE.role, role);

    $('#who').textContent = `Signed in as ${u} · ${role}`;
    authDialog.close();
    await refresh();
  }catch(e){
    console.error('Auth error:', e);
    alert(`Login failed: ${e.message||e}`);
  }
};

// --- form wiring --------------------------------------------------------------
const FIELDS = ['name','diagnosis','discipline','doctor','admitted','admissionDate','day','sticker','remarks'];
let editing = null;

// keep day in sync
$('#admissionDate').addEventListener('change', ()=>{
  const nd = normalizeDate($('#admissionDate').value);
  $('#admissionDate').value = nd;
  $('#day').value = computeDays(nd);
});

$('#patientForm').addEventListener('submit', async (e)=>{
  e.preventDefault();
  if(!API)  return alert('Set API base first.');
  if(!token) return alert('Sign in first.');

  // collect + normalize
  const v = Object.fromEntries(FIELDS.map(f=>[f, ($('#'+f)?.value ?? '').trim()]));
  v.admissionDate = normalizeDate(v.admissionDate || new Date());
  v.day = computeDays(v.admissionDate);

  const payload = {
    name: v.name,
    diagnosis: v.diagnosis,
    discipline: v.discipline,
    doctor: v.doctor,
    admitted: v.admitted,
    admission_date: v.admissionDate, // <-- snake_case for API
    day: v.day,
    sticker: v.sticker,
    remarks: v.remarks
  };

  try{
    const res = await fetch(`${API}/api/patients/`, {
      method:'POST',
      headers:{ 'Content-Type':'application/json', 'Authorization':'Bearer '+token, 'X-Role': role },
      body: JSON.stringify(payload)
    });
    if(!res.ok){
      const err = await jsonOrText(res);
      throw new Error(firstError(err));
    }
    status('Captured');
    e.target.reset();
    $('#day').value = '';
    editing = null;
    $('#updateBtn').disabled = true;
    await refresh();
  }catch(e2){
    console.error('Save failed:', e2);
    alert(`Save failed: ${e2.message||e2}`);
  }
});

$('#clearBtn').onclick = ()=>{
  $('#patientForm').reset(); $('#day').value=''; editing=null; $('#updateBtn').disabled=true;
};

$('#updateBtn').onclick = async ()=>{
  if(editing == null) return;
  if(!API || !token) return alert('Sign in first.');

  const v = Object.fromEntries(FIELDS.map(f=>[f, ($('#'+f)?.value ?? '').trim()]));
  v.admissionDate = normalizeDate(v.admissionDate || new Date());
  v.day = computeDays(v.admissionDate);

  const payload = {
    name: v.name,
    diagnosis: v.diagnosis,
    discipline: v.discipline,
    doctor: v.doctor,
    admitted: v.admitted,
    admission_date: v.admissionDate,
    day: v.day,
    sticker: v.sticker,
    remarks: v.remarks
  };

  try{
    const res = await fetch(`${API}/api/patients/${editing}/`, {
      method:'PUT',
      headers:{ 'Content-Type':'application/json', 'Authorization':'Bearer '+token, 'X-Role': role },
      body: JSON.stringify(payload)
    });
    if(!res.ok){ const err = await jsonOrText(res); throw new Error(firstError(err)); }
    status('Updated');
    $('#patientForm').reset(); $('#day').value=''; editing=null; $('#updateBtn').disabled=true;
    await refresh();
  }catch(e){
    console.error('Update failed:', e);
    alert(`Update failed: ${e.message||e}`);
  }
};

$('#refreshBtn').onclick = refresh;

// --- table render & data flow -------------------------------------------------
const tbody = $('#table tbody');
const search = $('#search');
search.addEventListener('input', render);

async function refresh(){
  if(!API || !token) return;
  try{
    const res = await fetch(`${API}/api/patients/`, { headers:{'Authorization':'Bearer '+token, 'X-Role': role} });
    if(!res.ok){ const err = await jsonOrText(res); throw new Error(firstError(err)); }
    window._rows = await res.json();
    render();
  }catch(e){
    console.warn('Fetch patients failed:', e);
    alert(`Load failed: ${e.message||e}`);
  }
}

function render(){
  const q = (search.value||'').toLowerCase().trim();
  tbody.innerHTML = '';
  const rows = (window._rows||[]).filter(r => !q || JSON.stringify(r).toLowerCase().includes(q));

  rows.forEach((r, idx)=>{
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${idx+1}</td>
      <td>${esc(r.name)}</td>
      <td>${esc(r.diagnosis)}</td>
      <td>${esc(r.discipline)}</td>
      <td>${esc(r.doctor)}</td>
      <td>${esc(r.admitted)}</td>
      <td>${esc(r.admission_date || '')}</td>
      <td>${esc(r.day ?? '')}</td>
      <td>${esc(r.sticker ?? '')}</td>
      <td>${esc((r.remarks||'').replace(/\n/g,' '))}</td>
      <td>${esc(human(r.updated_at))}</td>
      <td>
        <div class="inline">
          <button class="btn" data-act="edit">Edit</button>
          <button class="btn" data-act="del">Delete</button>
        </div>
      </td>`;
    tr.querySelector('[data-act="edit"]').onclick = ()=>{
      editing = r.id;
      ['name','diagnosis','discipline','doctor','admitted','sticker','remarks']
        .forEach(f => $('#'+f).value = r[f] || '');
      const nd = normalizeDate(r.admission_date || '');
      $('#admissionDate').value = nd;
      $('#day').value = r.day ?? computeDays(nd);
      $('#updateBtn').disabled = false;
      window.scrollTo({top:0, behavior:'smooth'});
    };
    tr.querySelector('[data-act="del"]').onclick = async ()=>{
      if(!confirm('Delete this record?')) return;
      const res = await fetch(`${API}/api/patients/${r.id}/`, { method:'DELETE', headers:{'Authorization':'Bearer '+token, 'X-Role': role} });
      if(res.ok) await refresh(); else alert('Delete failed');
    };
    tbody.appendChild(tr);
  });
}

// --- export CSV ---------------------------------------------------------------
$('#exportCsv').onclick = ()=>{
  const rows = window._rows || [];
  const header = ['Name','Diagnosis','Discipline','Doctor','Admitted','Admission Date','Day','Sticker','Remarks','Last Edited'];
  const data = rows.map(r=>[
    r.name, r.diagnosis, r.discipline, r.doctor, r.admitted,
    r.admission_date, r.day, r.sticker, (r.remarks||'').replace(/\n/g,' '), human(r.updated_at)
  ]);
  const csv = [header, ...data].map(row=>row.map(v=>`"${String(v??'').replace(/"/g,'""')}"`).join(',')).join('\n');
  const blob = new Blob([csv], {type:'text/csv'}); const a = document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='patients.csv'; a.click();
};

// --- boot ---------------------------------------------------------------------
if(token) $('#who').textContent = `Signed in · role: ${role}`;
refresh();
