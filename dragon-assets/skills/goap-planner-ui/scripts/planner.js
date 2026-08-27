// GOAP Planner UI Orchestration
// Connects GOAP engine with D3 graph visualization and UI controls

let currentState = null;
let currentPlan = [];
let currentStep = 0;
let isPlaying = false;
let autoPlayInterval = null;

// UI element references
const elements = {
  goalSelect: null,
  goalCustom: null,
  btnPlan: null,
  btnStep: null,
  btnAuto: null,
  btnPause: null,
  btnReset: null,
  planResult: null,
  planEmpty: null,
  btnExport: null,
  btnImport: null,
  importText: null,
  stateList: null,
  statsList: null,
  statusStep: null,
  statusCost: null,
  statusMode: null
};

/**
 * Initialize the planner UI
 */
function initPlanner() {
  // Cache DOM elements
  elements.goalSelect = document.getElementById('goal-select');
  elements.goalCustom = document.getElementById('goal-custom');
  elements.btnPlan = document.getElementById('btn-plan');
  elements.btnStep = document.getElementById('btn-step');
  elements.btnAuto = document.getElementById('btn-auto');
  elements.btnPause = document.getElementById('btn-pause');
  elements.btnReset = document.getElementById('btn-reset');
  elements.planResult = document.getElementById('plan-result');
  elements.planEmpty = document.getElementById('plan-empty');
  elements.btnExport = document.getElementById('btn-export');
  elements.btnImport = document.getElementById('btn-import');
  elements.importText = document.getElementById('import-text');
  elements.stateList = document.getElementById('state-list');
  elements.statsList = document.getElementById('stats-list');
  elements.statusStep = document.getElementById('status-step');
  elements.statusCost = document.getElementById('status-cost');
  elements.statusMode = document.getElementById('status-mode');

  // Initialize graph
  if (window.graphViz) {
    window.graphViz.initGraph('graph-svg');
  }

  // Reset state
  resetState();

  // Bind events
  bindEvents();

  // Initial render
  renderState();
  renderGraph();

  // Handle window resize
  window.addEventListener('resize', () => {
    if (window.graphViz) window.graphViz.resizeGraph();
  });
}

/**
 * Bind UI event handlers
 */
function bindEvents() {
  // Plan button
  elements.btnPlan.addEventListener('click', handlePlan);

  // Goal select change
  elements.goalSelect.addEventListener('change', (e) => {
    if (e.target.value) {
      elements.goalCustom.value = '';
    }
  });

  // Custom goal input
  elements.goalCustom.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handlePlan();
  });

  // Execution controls
  elements.btnStep.addEventListener('click', handleStep);
  elements.btnAuto.addEventListener('click', handleAuto);
  elements.btnPause.addEventListener('click', handlePause);
  elements.btnReset.addEventListener('click', handleReset);

  // Import/Export
  elements.btnExport.addEventListener('click', handleExport);
  elements.btnImport.addEventListener('click', handleImportToggle);
  elements.importText.addEventListener('input', handleImport);
}

/**
 * Handle plan generation
 */
function handlePlan() {
  let goal = null;

  // Get goal from select or custom input
  if (elements.goalSelect.value) {
    goal = GOALS[elements.goalSelect.value];
  } else if (elements.goalCustom.value.trim()) {
    try {
      goal = JSON.parse(elements.goalCustom.value.trim());
    } catch (e) {
      alert('Invalid JSON goal format');
      return;
    }
  } else {
    alert('Please select or enter a goal');
    return;
  }

  // Run A* GOAP planner
  const plan = goapPlan(goal, currentState, ACTION_LIBRARY);

  if (plan) {
    currentPlan = plan;
    currentStep = 0;
    renderPlan();
    renderGraph();
    updateStatus(`已规划: ${plan.length} 步`, '规划完成');
  } else {
    currentPlan = [];
    currentStep = 0;
    renderPlan();
    renderGraph();
    updateStatus('无法找到可行路径', '无解');
  }
}

/**
 * Handle single step execution
 */
function handleStep() {
  if (currentPlan.length === 0) {
    alert('请先生成规划');
    return;
  }

  if (currentStep >= currentPlan.length) {
    updateStatus('规划已全部执行', '完成');
    stopAutoPlay();
    return;
  }

  const action = currentPlan[currentStep];
  const actionName = action.name || action;

  // Apply effects
  currentState = applyEffect(currentState, action);

  currentStep++;
  renderState();
  renderPlan();
  updateStatus(`执行: ${actionName}`, `步骤 ${currentStep}/${currentPlan.length}`);

  if (currentStep >= currentPlan.length) {
    updateStatus('规划执行完成!', '完成');
    stopAutoPlay();
  }
}

/**
 * Handle auto-play
 */
function handleAuto() {
  if (currentPlan.length === 0) {
    alert('请先生成规划');
    return;
  }

  isPlaying = true;
  elements.btnAuto.style.display = 'none';
  elements.btnPause.style.display = 'flex';

  autoPlayInterval = setInterval(() => {
    if (currentStep >= currentPlan.length) {
      stopAutoPlay();
      return;
    }
    handleStep();
  }, 1000);
}

/**
 * Handle pause
 */
function handlePause() {
  stopAutoPlay();
}

/**
 * Stop auto-play
 */
function stopAutoPlay() {
  isPlaying = false;
  if (autoPlayInterval) {
    clearInterval(autoPlayInterval);
    autoPlayInterval = null;
  }
  if (elements.btnAuto) elements.btnAuto.style.display = 'flex';
  if (elements.btnPause) elements.btnPause.style.display = 'none';
}

/**
 * Handle reset
 */
function handleReset() {
  stopAutoPlay();
  resetState();
  currentPlan = [];
  currentStep = 0;
  renderState();
  renderPlan();
  renderGraph();
  updateStatus('已重置', '就绪');
}

/**
 * Reset state to initial
 */
function resetState() {
  currentState = { ...INITIAL_STATE };
}

/**
 * Handle export
 */
function handleExport() {
  const data = {
    actionLibrary: ACTION_LIBRARY,
    initialState: INITIAL_STATE,
    goals: GOALS,
    currentPlan: currentPlan,
    currentState: currentState,
    currentStep: currentStep
  };

  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'goap-plan.json';
  a.click();
  URL.revokeObjectURL(url);
}

/**
 * Handle import toggle
 */
function handleImportToggle() {
  const textarea = elements.importText;
  textarea.style.display = textarea.style.display === 'none' ? 'block' : 'none';
}

/**
 * Handle import
 */
function handleImport() {
  try {
    const data = JSON.parse(elements.importText.value);
    if (data.actionLibrary) {
      Object.assign(ACTION_LIBRARY, data.actionLibrary);
    }
    if (data.currentPlan) {
      currentPlan = data.currentPlan;
      currentStep = data.currentStep || 0;
    }
    if (data.currentState) {
      currentState = data.currentState;
    }
    renderState();
    renderPlan();
    renderGraph();
    updateStatus('导入成功', '就绪');
  } catch (e) {
    // Ignore JSON parse errors during typing
  }
}

/**
 * Render current state in right panel
 */
function renderState() {
  const container = elements.stateList;
  container.innerHTML = '';

  Object.entries(currentState).forEach(([key, val]) => {
    const item = document.createElement('div');
    item.className = 'state-item';

    const keyEl = document.createElement('span');
    keyEl.className = 'state-key';
    keyEl.textContent = key;

    const valEl = document.createElement('span');
    valEl.className = `state-val ${typeof val === 'boolean' ? (val ? 'true' : 'false') : 'number'}`;
    valEl.textContent = typeof val === 'boolean' ? (val ? '✓' : '✗') : val;

    item.appendChild(keyEl);
    item.appendChild(valEl);
    container.appendChild(item);
  });

  // Render stats
  renderStats();
}

/**
 * Render execution stats
 */
function renderStats() {
  const container = elements.statsList;
  container.innerHTML = '';

  const stats = [
    { label: '总代价', value: currentPlan.slice(0, currentStep).reduce((s, a) => s + (a.cost || 1), 0) },
    { label: '已执行', value: `${currentStep}/${currentPlan.length}` },
    { label: '剩余步数', value: currentPlan.length - currentStep }
  ];

  stats.forEach(s => {
    const item = document.createElement('div');
    item.className = 'state-item';
    item.innerHTML = `<span class="state-key">${s.label}</span><span class="state-val number">${s.value}</span>`;
    container.appendChild(item);
  });

  // Update status bar
  if (elements.statusCost) {
    const totalCost = currentPlan.slice(0, currentStep).reduce((sum, a) => sum + (a.cost || 1), 0);
    elements.statusCost.textContent = `总代价: ${totalCost}`;
  }
  if (elements.statusStep) {
    elements.statusStep.textContent = `步骤: ${currentStep}/${currentPlan.length}`;
  }
}

/**
 * Render plan in left panel
 */
function renderPlan() {
  const container = elements.planResult;
  container.innerHTML = '';

  if (currentPlan.length === 0) {
    const empty = document.createElement('div');
    empty.className = 'plan-empty';
    empty.id = 'plan-empty';
    empty.textContent = '规划结果将显示在这里';
    container.appendChild(empty);
    return;
  }

  currentPlan.forEach((action, idx) => {
    const actionName = action.name || action;
    const cost = action.cost || 1;
    const effects = Object.entries((action.effects || {})).map(([k, v]) => `${k}=${v}`).join(', ');

    const step = document.createElement('div');
    step.className = 'plan-step' + (idx < currentStep ? ' current' : '');

    const num = document.createElement('span');
    num.className = 'step-num';
    num.textContent = idx + 1;

    const name = document.createElement('span');
    name.className = 'step-name';
    name.textContent = actionName;

    const costEl = document.createElement('span');
    costEl.className = 'step-cost';
    costEl.textContent = cost;

    const effect = document.createElement('span');
    effect.className = 'step-effect';
    effect.textContent = effects.substring(0, 15) + (effects.length > 15 ? '...' : '');

    step.appendChild(num);
    step.appendChild(name);
    step.appendChild(costEl);
    step.appendChild(effect);
    container.appendChild(step);
  });
}

/**
 * Render graph
 */
function renderGraph() {
  if (window.graphViz) {
    const planPath = currentPlan.slice(0, currentStep);
    window.graphViz.renderGraph(ACTION_LIBRARY, planPath);
  }
}

/**
 * Update status bar
 */
function updateStatus(text, mode) {
  if (elements.statusMode) {
    elements.statusMode.textContent = `模式: ${mode || '就绪'}`;
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initPlanner);
} else {
  // DOM already loaded, wait for scripts to load
  setTimeout(initPlanner, 100);
}
