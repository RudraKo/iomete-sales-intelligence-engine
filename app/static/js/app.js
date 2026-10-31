// Frontend Logic for The Living Sales Intelligence Engine

document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  loadLedgerStats();
  loadSnippets();
  setupPresets();
});

function initTabs() {
  const tabs = document.querySelectorAll('.tab-btn');
  const panels = document.querySelectorAll('.tab-panel');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const target = tab.dataset.target;
      tabs.forEach(t => {
        t.classList.remove('border-cyan-400', 'text-cyan-400');
        t.classList.add('border-transparent', 'text-gray-400');
      });
      panels.forEach(p => p.classList.add('hidden'));

      tab.classList.add('border-cyan-400', 'text-cyan-400');
      tab.classList.remove('border-transparent', 'text-gray-400');
      document.getElementById(target).classList.remove('hidden');
    });
  });
}

// -------------------------
// 1. 15-MINUTE CALL PREP
// -------------------------
async function generateCallPrep() {
  const btn = document.getElementById('btn-call-prep');
  const output = document.getElementById('call-prep-output');
  const empty = document.getElementById('call-prep-empty');

  const prospectName = document.getElementById('prep-prospect').value.trim();
  const industry = document.getElementById('prep-industry').value.trim();
  const stack = document.getElementById('prep-stack').value.trim();
  const painPointsRaw = document.getElementById('prep-painpoints').value.trim();
  const personas = Array.from(document.querySelectorAll('input[name="prep-personas"]:checked')).map(cb => cb.value);

  if (!prospectName || !stack) {
    alert('Please enter prospect company name and current data stack.');
    return;
  }

  const painPoints = painPointsRaw.split('\n').filter(p => p.trim().length > 0);

  btn.disabled = true;
  btn.innerHTML = `<span class="animate-spin inline-block mr-2">🔄</span> Synthesizing Brief...`;

  try {
    const res = await fetch('/api/sales/call-prep', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prospect_name: prospectName,
        industry: industry,
        current_stack: stack,
        key_pain_points: painPoints,
        target_personas: personas
      })
    });

    if (!res.ok) throw new Error('Failed to generate call prep brief');
    const data = await res.json();
    renderCallPrep(data);
    empty.classList.add('hidden');
    output.classList.remove('hidden');
  } catch (err) {
    alert('Error: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = `🚀 Generate Instant Battle Brief`;
  }
}

function renderCallPrep(data) {
  document.getElementById('prep-out-title').innerText = `${data.prospect_name} - Strategic Call Brief`;
  document.getElementById('prep-out-fit').innerText = data.architecture_fit;

  // Value Drivers
  const vdContainer = document.getElementById('prep-out-drivers');
  vdContainer.innerHTML = data.verified_value_drivers.map(vd => `
    <div class="flex items-start space-x-2 text-sm text-gray-200 bg-gray-800/60 p-2.5 rounded-lg border border-gray-700">
      <span class="text-cyan-400 mt-0.5">✔</span>
      <span>${vd}</span>
    </div>
  `).join('');

  // Role Discovery Questions
  const dqContainer = document.getElementById('prep-out-questions');
  dqContainer.innerHTML = '';
  for (const [role, questions] of Object.entries(data.role_discovery_questions)) {
    dqContainer.innerHTML += `
      <div class="bg-gray-800/80 rounded-lg p-3 border border-gray-700">
        <h4 class="text-xs uppercase font-semibold text-cyan-400 mb-2 tracking-wider">${role}</h4>
        <ul class="space-y-1.5 text-sm text-gray-300">
          ${questions.map(q => `<li class="flex items-start space-x-2"><span class="text-gray-500">•</span><span>${q}</span></li>`).join('')}
        </ul>
      </div>
    `;
  }

  // Strict Landmines
  const lmContainer = document.getElementById('prep-out-landmines');
  lmContainer.innerHTML = data.strict_landmines.map(lm => `
    <div class="flex items-start space-x-2 text-sm text-red-200 bg-red-950/30 p-2.5 rounded-lg border border-red-900/50">
      <span class="text-red-400 font-bold mt-0.5">⚠️</span>
      <span>${lm}</span>
    </div>
  `).join('');

  // Citations
  const citContainer = document.getElementById('prep-out-citations');
  citContainer.innerHTML = data.citations.map(c => `
    <span class="inline-block text-xs bg-gray-800 text-gray-400 px-2 py-1 rounded border border-gray-700 mr-2 mb-2">
      📄 ${c.title} <strong class="text-cyan-300 font-mono">(${c.source})</strong>
    </span>
  `).join('');

  // Verification Badge
  const badge = document.getElementById('prep-out-badge');
  badge.className = data.confidence_score >= 0.35 
    ? "px-2.5 py-0.5 rounded-full text-xs font-semibold badge-verified" 
    : "px-2.5 py-0.5 rounded-full text-xs font-semibold badge-unverified";
  badge.innerText = `Confidence: ${(data.confidence_score * 100).toFixed(0)}% • ${data.grounding_status.slice(0, 24)}...`;
}

// -------------------------
// 2. OBJECTION INVERSION
// -------------------------
async function invertObjection() {
  const btn = document.getElementById('btn-invert');
  const objectionText = document.getElementById('obj-input').value.trim();
  const competitor = document.getElementById('obj-competitor').value;
  const output = document.getElementById('obj-output');
  const empty = document.getElementById('obj-empty');

  if (!objectionText) {
    alert('Please enter or select an objection.');
    return;
  }

  btn.disabled = true;
  btn.innerHTML = `<span class="animate-spin inline-block mr-2">🔄</span> Analyzing Inversion...`;

  try {
    const res = await fetch('/api/sales/objection-inversion', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        objection_text: objectionText,
        competitor: competitor
      })
    });

    if (!res.ok) throw new Error('Failed to invert objection');
    const data = await res.json();
    renderObjection(data);
    empty.classList.add('hidden');
    output.classList.remove('hidden');
  } catch (err) {
    alert('Error: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = `🛡️ Invert Objection`;
  }
}

function renderObjection(data) {
  const badge = document.getElementById('obj-out-badge');
  if (data.is_verified) {
    badge.className = "px-2.5 py-0.5 rounded-full text-xs font-semibold badge-verified";
    badge.innerText = "Verified Grounded";
  } else {
    badge.className = "px-2.5 py-0.5 rounded-full text-xs font-semibold badge-unverified";
    badge.innerText = "Unknown / Requires Engineering Verification";
  }

  document.getElementById('obj-out-ack').innerText = data.acknowledgment;
  document.getElementById('obj-out-thesis').innerText = data.inversion_thesis;
  document.getElementById('obj-out-grounding').innerText = data.verified_technical_grounding;
  document.getElementById('obj-out-talktrack').innerText = data.battle_tested_talk_track;

  const citContainer = document.getElementById('obj-out-citations');
  citContainer.innerHTML = data.citations.length > 0 
    ? data.citations.map(c => `
      <span class="inline-block text-xs bg-gray-800 text-gray-400 px-2 py-1 rounded border border-gray-700 mr-2 mb-2">
        📄 ${c.title} <strong class="text-cyan-300 font-mono">(${c.source})</strong>
      </span>
    `).join('')
    : '<span class="text-xs text-red-400">No supporting documentation found in living ledger.</span>';
}

// -------------------------
// 3. PROPOSAL MEMO GENERATOR
// -------------------------
async function generateProposalMemo() {
  const btn = document.getElementById('btn-memo');
  const prospect = document.getElementById('memo-prospect').value.trim();
  const sponsor = document.getElementById('memo-sponsor').value.trim();
  const title = document.getElementById('memo-title').value.trim();
  const stack = document.getElementById('memo-stack').value.trim();
  const initiativesRaw = document.getElementById('memo-initiatives').value.trim();
  const notes = document.getElementById('memo-notes').value.trim();
  const output = document.getElementById('memo-output');
  const empty = document.getElementById('memo-empty');

  if (!prospect || !sponsor) {
    alert('Please fill in prospect and sponsor details.');
    return;
  }

  const initiatives = initiativesRaw.split('\n').filter(i => i.trim().length > 0);

  btn.disabled = true;
  btn.innerHTML = `<span class="animate-spin inline-block mr-2">🔄</span> Generating Executive Memo...`;

  try {
    const res = await fetch('/api/sales/proposal-memo', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prospect_name: prospect,
        sponsor_name: sponsor,
        sponsor_title: title,
        current_stack: stack,
        primary_initiatives: initiatives,
        discovery_notes: notes
      })
    });

    if (!res.ok) throw new Error('Failed to generate proposal memo');
    const data = await res.json();
    renderMemo(data);
    empty.classList.add('hidden');
    output.classList.remove('hidden');
  } catch (err) {
    alert('Error: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = `📄 Generate Executive Memo`;
  }
}

function renderMemo(data) {
  document.getElementById('memo-out-header').innerText = `Executive Brief & Architecture Proposal: ${data.prospect_name}`;
  document.getElementById('memo-out-sponsor').innerText = `Prepared for: ${data.sponsor_name} (${data.sponsor_title})`;
  document.getElementById('memo-out-summary').innerText = data.executive_summary;
  document.getElementById('memo-out-problem').innerText = data.problem_statement;
  document.getElementById('memo-out-arch').innerText = data.proposed_solution_architecture;
  document.getElementById('memo-out-migration').innerText = data.migration_and_interoperability;

  // TCO Matrix
  const tco = data.tco_analysis_matrix;
  const tcoContainer = document.getElementById('memo-out-tco');
  tcoContainer.innerHTML = `
    <tr class="border-b border-gray-800"><td class="py-2 text-gray-400">Current Incumbent Stack</td><td class="py-2 text-white font-medium">${tco.current_stack}</td></tr>
    <tr class="border-b border-gray-800"><td class="py-2 text-gray-400">Est. Monthly Incumbent Spend</td><td class="py-2 text-red-400 font-medium">${tco.estimated_current_monthly_spend}</td></tr>
    <tr class="border-b border-gray-800"><td class="py-2 text-gray-400">Est. Monthly IOMETE Spend</td><td class="py-2 text-emerald-400 font-medium">${tco.estimated_iomete_monthly_spend}</td></tr>
    <tr class="border-b border-gray-800"><td class="py-2 text-gray-400">Projected TCO Savings</td><td class="py-2 text-cyan-400 font-bold">${tco.projected_cost_savings}</td></tr>
    <tr class="border-b border-gray-800"><td class="py-2 text-gray-400">Data Egress Cost</td><td class="py-2 text-white font-medium">${tco.data_egress_fee}</td></tr>
  `;

  // POC Plan
  const pocContainer = document.getElementById('memo-out-poc');
  pocContainer.innerHTML = data.next_steps_poc_plan.map(step => `
    <li class="flex items-start space-x-2 text-sm text-gray-300">
      <span class="text-cyan-400 font-semibold">•</span>
      <span>${step}</span>
    </li>
  `).join('');
}

// -------------------------
// 4. THE LIVING LEDGER
// -------------------------
async function loadLedgerStats() {
  try {
    const res = await fetch('/api/stats');
    if (!res.ok) return;
    const stats = await res.json();
    document.getElementById('stat-total-snippets').innerText = stats.total_snippets;
  } catch (e) {}
}

async function loadSnippets(category = '', query = '') {
  const container = document.getElementById('ledger-snippets-list');
  container.innerHTML = `<div class="p-4 text-gray-400">Loading snippets...</div>`;

  try {
    let url = `/api/snippets?limit=50`;
    if (category) url += `&category=${encodeURIComponent(category)}`;
    if (query) url += `&query=${encodeURIComponent(query)}`;

    const res = await fetch(url);
    const snippets = await res.json();

    if (snippets.length === 0) {
      container.innerHTML = `<div class="p-8 text-center text-gray-500">No snippets found matching query.</div>`;
      return;
    }

    container.innerHTML = snippets.map(s => `
      <div class="bg-gray-800/60 p-4 rounded-xl border border-gray-700/70 hover:border-cyan-500/40 transition">
        <div class="flex items-start justify-between mb-2">
          <span class="text-xs uppercase tracking-wider font-semibold px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800/40">
            ${s.category}
          </span>
          <span class="text-xs text-gray-500 font-mono">${s.source}</span>
        </div>
        <h3 class="text-base font-semibold text-white mb-2">${s.title}</h3>
        <p class="text-sm text-gray-300 line-clamp-3 mb-3">${s.content}</p>
        <div class="flex flex-wrap gap-1.5">
          ${s.tags.map(t => `<span class="text-xs bg-gray-900 text-gray-400 px-2 py-0.5 rounded">#${t}</span>`).join('')}
        </div>
      </div>
    `).join('');
  } catch (err) {
    container.innerHTML = `<div class="p-4 text-red-400">Failed to load snippets: ${err.message}</div>`;
  }
}

async function ingestSnippet() {
  const title = document.getElementById('new-snip-title').value.trim();
  const category = document.getElementById('new-snip-cat').value;
  const content = document.getElementById('new-snip-content').value.trim();
  const tagsRaw = document.getElementById('new-snip-tags').value.trim();
  const source = document.getElementById('new-snip-source').value.trim();

  if (!title || !content || !source) {
    alert('Please fill in Title, Content, and Source Reference.');
    return;
  }

  const tags = tagsRaw.split(',').map(t => t.trim()).filter(t => t.length > 0);

  try {
    const res = await fetch('/api/snippets', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title,
        category,
        content,
        tags,
        source
      })
    });

    if (!res.ok) throw new Error('Ingestion failed');
    alert('Snippet successfully indexed in Living Ledger!');
    // Reset form
    document.getElementById('new-snip-title').value = '';
    document.getElementById('new-snip-content').value = '';
    document.getElementById('new-snip-tags').value = '';
    document.getElementById('new-snip-source').value = '';
    loadLedgerStats();
    loadSnippets();
  } catch (err) {
    alert('Error: ' + err.message);
  }
}

// -------------------------
// 5. ZERO-HALLUCINATION AUDIT
// -------------------------
async function runAudit() {
  const query = document.getElementById('audit-input').value.trim();
  const output = document.getElementById('audit-output');
  if (!query) return;

  output.innerHTML = `<span class="text-gray-400">Auditing claim against living ledger...</span>`;

  try {
    const res = await fetch(`/api/verifier/audit?text=${encodeURIComponent(query)}`, {
      method: 'POST'
    });
    const data = await res.json();

    const isGrounded = data.is_fully_grounded;
    output.innerHTML = `
      <div class="p-4 rounded-xl border ${isGrounded ? 'bg-emerald-950/20 border-emerald-800/40' : 'bg-red-950/20 border-red-800/40'}">
        <div class="flex items-center justify-between mb-3">
          <span class="text-xs uppercase font-bold tracking-wider ${isGrounded ? 'text-emerald-400' : 'text-red-400'}">
            Status: ${data.status_message}
          </span>
          <span class="text-xs font-mono text-gray-400">Confidence: ${(data.confidence_score * 100).toFixed(0)}%</span>
        </div>
        <div class="space-y-2 text-sm">
          ${data.supported_claims.map(c => `<div class="text-emerald-300">✔ ${c}</div>`).join('')}
          ${data.unsupported_claims.map(c => `<div class="text-red-300">❌ ${c}</div>`).join('')}
        </div>
      </div>
    `;
  } catch (err) {
    output.innerHTML = `<div class="text-red-400">Audit failed: ${err.message}</div>`;
  }
}

// -------------------------
// PRESET HELPERS
// -------------------------
function setupPresets() {
  // Preset Call Preps
  window.loadPrepPreset = function(type) {
    if (type === 'snowflake') {
      document.getElementById('prep-prospect').value = 'Apex FinTech Solutions';
      document.getElementById('prep-industry').value = 'Financial Services & Payments';
      document.getElementById('prep-stack').value = 'Snowflake on AWS (500TB)';
      document.getElementById('prep-painpoints').value = 'High cloud compute credit multipliers ($85k/mo bill)\nRegulatory mandate requiring zero data egress outside VPC\nFear of lock-in with proprietary micro-partitions';
    } else if (type === 'emr') {
      document.getElementById('prep-prospect').value = 'OmniTrack SaaS';
      document.getElementById('prep-industry').value = 'B2B Analytics & Event Streaming';
      document.getElementById('prep-stack').value = 'Self-managed Apache Spark on AWS EMR';
      document.getElementById('prep-painpoints').value = '3 full-time engineers dedicated to babysitting Spark clusters\nSpot instance terminations crashing nightly ETL jobs\nSmall-file syndrome slowing down analytical queries';
    } else if (type === 'databricks') {
      document.getElementById('prep-prospect').value = 'Nova Retail Global';
      document.getElementById('prep-industry').value = 'E-commerce & Retail';
      document.getElementById('prep-stack').value = 'Databricks Lakehouse on GCP';
      document.getElementById('prep-painpoints').value = 'Excessive DBU consumption costs on standard SQL dashboards\nDesire to standardize on native Apache Iceberg tables\nDirect Tableau query concurrency bottlenecks';
    }
  };

  // Preset Objections
  window.loadObjectionPreset = function(type) {
    if (type === 'lockin') {
      document.getElementById('obj-input').value = 'We are already deeply committed to Snowflake; migrating away is too risky and locked in.';
      document.getElementById('obj-competitor').value = 'Snowflake';
    } else if (type === 'diy') {
      document.getElementById('obj-input').value = 'Why shouldn’t we just deploy open source Apache Spark and Iceberg ourselves on our Kubernetes cluster?';
      document.getElementById('obj-competitor').value = 'DIY Open Source';
    } else if (type === 'sovereignty') {
      document.getElementById('obj-input').value = 'How can you guarantee our customer financial data will never leave our private cloud VPC?';
      document.getElementById('obj-competitor').value = 'General';
    } else if (type === 'hallucination_trap') {
      document.getElementById('obj-input').value = 'Can IOMETE run on Windows 95 and directly store raw customer credit card transactions?';
      document.getElementById('obj-competitor').value = 'None';
    }
  };
}

