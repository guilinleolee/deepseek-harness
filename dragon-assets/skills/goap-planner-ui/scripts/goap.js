// GOAP A* Search Engine
// Implements A* search over action graph with preconditions and effects

class PriorityQueue {
  constructor() {
    this.items = [];
  }

  push(item) {
    this.items.push(item);
    this.items.sort((a, b) => a.f - b.f);
  }

  pop() {
    return this.items.shift();
  }

  empty() {
    return this.items.length === 0;
  }
}

/**
 * Check if goal is satisfied by current state
 * @param {Object} s - World state
 * @param {Object} goal - Goal state
 * @returns {boolean}
 */
function goalSatisfied(s, goal) {
  return Object.entries(goal).every(([k, v]) => s[k] === v);
}

/**
 * Heuristic: count of unsatisfied goal conditions
 * @param {Object} s - World state
 * @param {Object} goal - Goal state
 * @returns {number}
 */
function heuristic(s, goal) {
  return Object.entries(goal).filter(([k, v]) => s[k] !== v).length;
}

/**
 * Check if action can be executed in current state
 * @param {Object} action - Action with preconditions
 * @param {Object} state - Current world state
 * @returns {boolean}
 */
function canExecute(action, state) {
  return Object.entries(action.preconditions).every(([k, v]) => state[k] === v);
}

/**
 * Apply action effects to state (returns new state object)
 * @param {Object} state - Current world state
 * @param {Object} action - Action with effects
 * @returns {Object} - New state
 */
function applyEffect(state, action) {
  const newState = { ...state };
  Object.entries(action.effects).forEach(([k, v]) => {
    newState[k] = v;
  });
  return newState;
}

/**
 * A* GOAP planner - finds optimal action sequence from state to goal
 * @param {Object} goal - Goal state
 * @param {Object} state - Current world state
 * @param {Object} actions - Action library (name -> action)
 * @returns {Array|null} - Plan array or null if no solution
 */
function goapPlan(goal, state, actions) {
  const actionList = Object.values(actions);
  const open = new PriorityQueue();
  open.push({ state: { ...state }, path: [], cost: 0 });

  const maxIterations = 1000;
  let iterations = 0;

  while (!open.empty() && iterations < maxIterations) {
    iterations++;
    const { state: curr, path, cost: g } = open.pop();

    if (goalSatisfied(curr, goal)) {
      return path;
    }

    for (const action of actionList) {
      if (canExecute(action, curr)) {
        const next = applyEffect(curr, action);
        const h = heuristic(next, goal);
        const f = g + action.cost + h;
        open.push({
          state: next,
          path: [...path, { name: action._name || Object.keys(actions).find(k => actions[k] === action), ...action }],
          cost: g + action.cost
        });
      }
    }
  }

  return null; // No solution found
}

/**
 * Get available actions for current state
 * @param {Object} state - Current world state
 * @param {Object} actions - Action library
 * @returns {Array} - List of executable actions
 */
function getAvailableActions(state, actions) {
  return Object.entries(actions)
    .filter(([_, action]) => canExecute(action, state))
    .map(([name, action]) => ({ name, ...action }));
}

/**
 * Deep clone state object
 * @param {Object} state - World state
 * @returns {Object} - Cloned state
 */
function cloneState(state) {
  return { ...state };
}

// Export for use in other scripts
if (typeof window !== 'undefined') {
  window.goapEngine = {
    PriorityQueue,
    goalSatisfied,
    heuristic,
    canExecute,
    applyEffect,
    goapPlan,
    getAvailableActions,
    cloneState
  };
}
