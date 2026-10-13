// D3.js GOAP Action Graph Visualization
// Force-directed graph showing actions as nodes, precond→effect as edges

let simulation = null;
let svg = null;
let g = null;
let nodeElements = null;
let edgeElements = null;
let tooltip = null;

// Color scheme matching index.html CSS variables
const COLORS = {
  action: '#58a6ff',
  effect: '#3fb950',
  precond: '#f0883e',
  cost: '#bc8cff',
  optimal: '#f85149',
  candidate: '#58a6ff',
  text: '#e6edf3',
  muted: '#8b949e',
  border: '#30363d',
  panel: '#1c2128'
};

/**
 * Initialize the graph visualization
 * @param {string} svgId - SVG element ID
 */
function initGraph(svgId) {
  svg = d3.select('#' + svgId);
  g = svg.append('g').attr('class', 'graph-container');

  // Arrow marker for edges
  svg.append('defs').append('marker')
    .attr('id', 'arrowhead')
    .attr('viewBox', '0 -5 10 10')
    .attr('refX', 20)
    .attr('refY', 0)
    .attr('markerWidth', 6)
    .attr('markerHeight', 6)
    .attr('orient', 'auto')
    .append('path')
    .attr('d', 'M0,-5L10,0L0,5')
    .attr('fill', COLORS.muted);

  tooltip = document.getElementById('tooltip');
}

/**
 * Build graph data from action library
 * @param {Object} actions - Action library
 * @returns {Object} - {nodes: [], edges: []}
 */
function buildGraphData(actions) {
  const nodes = [];
  const edges = [];
  const nodeIds = new Set();

  // Create action nodes
  Object.entries(actions).forEach(([name, action]) => {
    nodes.push({
      id: name,
      type: 'action',
      cost: action.cost,
      preconditions: Object.entries(action.preconditions).map(([k, v]) => `${k}=${v}`).join(', '),
      effects: Object.entries(action.effects).map(([k, v]) => `${k}=${v}`).join(', ')
    });
    nodeIds.add(name);
  });

  // Create effect→action edges (precondition satisfaction)
  Object.entries(actions).forEach(([fromName, fromAction]) => {
    Object.entries(fromAction.effects).forEach(([effectKey, effectVal]) => {
      Object.entries(actions).forEach(([toName, toAction]) => {
        if (toAction.preconditions.hasOwnProperty(effectKey)) {
          edges.push({
            source: fromName,
            target: toName,
            label: effectKey,
            type: 'effect-link'
          });
        }
      });
    });
  });

  return { nodes, edges };
}

/**
 * Render the graph with actions and edges
 * @param {Object} actions - Action library
 * @param {Array} planPath - Optimal path (for highlighting)
 */
function renderGraph(actions, planPath = []) {
  if (!svg || !g) return;

  const { nodes, edges } = buildGraphData(actions);
  const planSet = new Set(planPath.map(a => a.name));

  // Clear previous render
  g.selectAll('*').remove();

  const width = svg.node().clientWidth || 800;
  const height = svg.node().clientHeight || 600;

  // Create force simulation
  simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(edges).id(d => d.id).distance(160).strength(0.5))
    .force('charge', d3.forceManyBody().strength(-400))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(80));

  // Render edges
  const edgeG = g.append('g').attr('class', 'edges');
  edgeElements = edgeG.selectAll('line')
    .data(edges)
    .enter()
    .append('line')
    .attr('class', d => {
      const isOptimal = planPath.length > 0;
      const pathIndex = planPath.findIndex(a => a.name === d.source.id);
      const nextIndex = planPath.findIndex(a => a.name === d.target.id);
      if (isOptimal && (pathIndex >= 0 || nextIndex >= 0)) {
        return 'edge-line edge-optimal';
      }
      return 'edge-line edge-candidate';
    })
    .attr('stroke', d => {
      const pathIndex = planPath.findIndex(a => a.name === d.source.id);
      const nextIndex = planPath.findIndex(a => a.name === d.target.id);
      if (planPath.length > 0 && (pathIndex >= 0 || nextIndex >= 0)) {
        return COLORS.optimal;
      }
      return COLORS.muted;
    })
    .attr('stroke-width', d => {
      const pathIndex = planPath.findIndex(a => a.name === d.source.id);
      const nextIndex = planPath.findIndex(a => a.name === d.target.id);
      if (planPath.length > 0 && (pathIndex >= 0 || nextIndex >= 0)) {
        return 3;
      }
      return 1.5;
    })
    .attr('stroke-opacity', d => {
      const pathIndex = planPath.findIndex(a => a.name === d.source.id);
      const nextIndex = planPath.findIndex(a => a.name === d.target.id);
      if (planPath.length > 0 && (pathIndex >= 0 || nextIndex >= 0)) {
        return 1;
      }
      return 0.5;
    });

  // Edge labels
  edgeG.selectAll('text')
    .data(edges)
    .enter()
    .append('text')
    .attr('class', 'edge-label')
    .attr('font-size', '10px')
    .attr('fill', COLORS.muted)
    .attr('text-anchor', 'middle')
    .text(d => d.label);

  // Render action nodes
  const nodeG = g.append('g').attr('class', 'nodes');
  nodeElements = nodeG.selectAll('g')
    .data(nodes)
    .enter()
    .append('g')
    .attr('class', 'node-action')
    .call(d3.drag()
      .on('start', dragStarted)
      .on('drag', dragged)
      .on('end', dragEnded))
    .on('mouseenter', (event, d) => showTooltip(event, d))
    .on('mouseleave', hideTooltip)
    .on('mousemove', moveTooltip);

  // Node background
  nodeElements.append('rect')
    .attr('rx', 8)
    .attr('ry', 8)
    .attr('width', 140)
    .attr('height', 70)
    .attr('x', -70)
    .attr('y', -35)
    .attr('fill', COLORS.panel)
    .attr('stroke', d => planSet.has(d.id) ? COLORS.optimal : COLORS.action)
    .attr('stroke-width', d => planSet.has(d.id) ? 3 : 2);

  // Node label (action name)
  nodeElements.append('text')
    .attr('class', 'node-label')
    .attr('y', -8)
    .text(d => d.id)
    .attr('fill', COLORS.text)
    .attr('font-size', '12px')
    .attr('font-weight', '600')
    .attr('text-anchor', 'middle');

  // Node cost
  nodeElements.append('text')
    .attr('class', 'node-cost')
    .attr('y', 10)
    .text(d => `Cost: ${d.cost}`)
    .attr('fill', 'rgba(255,255,255,0.7)')
    .attr('font-size', '10px')
    .attr('text-anchor', 'middle');

  // Node effects preview
  nodeElements.append('text')
    .attr('class', 'node-effect')
    .attr('y', 26)
    .text(d => d.effects.substring(0, 20) + (d.effects.length > 20 ? '...' : ''))
    .attr('fill', 'rgba(255,255,255,0.6)')
    .attr('font-size', '9px')
    .attr('text-anchor', 'middle');

  // Update positions on tick
  simulation.on('tick', () => {
    edgeElements
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y);

    edgeG.selectAll('text')
      .attr('x', d => (d.source.x + d.target.x) / 2)
      .attr('y', d => (d.source.y + d.target.y) / 2 - 8);

    nodeElements.attr('transform', d => `translate(${d.x},${d.y})`);
  });

  // Zoom behavior
  const zoom = d3.zoom()
    .scaleExtent([0.2, 3])
    .on('zoom', (event) => {
      g.attr('transform', event.transform);
    });

  svg.call(zoom);
}

/**
 * Highlight the optimal plan path in the graph
 * @param {Array} plan - Plan array
 */
function highlightPlan(plan) {
  if (!plan || plan.length === 0) return;
  renderGraph(ACTION_LIBRARY, plan);
}

/**
 * Show tooltip for a node
 */
function showTooltip(event, d) {
  const tt = document.getElementById('tooltip');
  if (!tt) return;

  document.getElementById('tooltip-title').textContent = d.id;
  document.getElementById('tooltip-precond').textContent = d.preconditions || '—';
  document.getElementById('tooltip-effect').textContent = d.effects || '—';
  document.getElementById('tooltip-cost').textContent = d.cost;

  tt.style.display = 'block';
  moveTooltip(event);
}

/**
 * Move tooltip with mouse
 */
function moveTooltip(event) {
  const tt = document.getElementById('tooltip');
  if (!tt) return;
  const canvas = document.querySelector('.graph-canvas');
  const rect = canvas.getBoundingClientRect();
  const x = event.clientX - rect.left + 15;
  const y = event.clientY - rect.top + 15;
  tt.style.left = Math.min(x, rect.width - 240) + 'px';
  tt.style.top = Math.min(y, rect.height - 150) + 'px';
}

/**
 * Hide tooltip
 */
function hideTooltip() {
  if (tooltip) tooltip.style.display = 'none';
}

/**
 * Drag handlers
 */
function dragStarted(event, d) {
  if (!event.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x;
  d.fy = d.y;
}

function dragged(event, d) {
  d.fx = event.x;
  d.fy = event.y;
}

function dragEnded(event, d) {
  if (!event.active) simulation.alphaTarget(0);
  d.fx = null;
  d.fy = null;
}

/**
 * Resize graph to fit container
 */
function resizeGraph() {
  const canvas = document.querySelector('.graph-canvas');
  if (canvas && svg) {
    svg.attr('width', canvas.clientWidth).attr('height', canvas.clientHeight);
    if (simulation) {
      simulation.force('center', d3.forceCenter(canvas.clientWidth / 2, canvas.clientHeight / 2));
      simulation.alpha(0.3).restart();
    }
  }
}

// Export for use in other scripts
if (typeof window !== 'undefined') {
  window.graphViz = {
    initGraph,
    buildGraphData,
    renderGraph,
    highlightPlan,
    resizeGraph
  };
}
