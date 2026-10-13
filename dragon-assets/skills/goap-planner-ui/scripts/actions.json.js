// GOAP Action Library — 目标导向动作规划动作库
// index.html 通过 <script src="scripts/actions.json.js"> 加载此文件

const ACTION_LIBRARY = {
  "收集数据": {
    preconditions: { "有API访问": true },
    effects: { "数据就绪": true, "token消耗": 10 },
    cost: 1
  },
  "分析数据": {
    preconditions: { "数据就绪": true },
    effects: { "洞察生成": true, "数据就绪": false },
    cost: 2
  },
  "撰写报告": {
    preconditions: { "洞察生成": true },
    effects: { "报告完成": true, "洞察生成": false },
    cost: 3
  },
  "审核报告": {
    preconditions: { "报告完成": true },
    effects: { "审核通过": true, "报告完成": false },
    cost: 1
  }
};

const INITIAL_STATE = {
  "有API访问": true,
  "数据就绪": false,
  "洞察生成": false,
  "报告完成": false,
  "审核通过": false,
  "token消耗": 0
};

const GOALS = {
  "完成季度报告": { "报告完成": true },
  "审核通过": { "审核通过": true }
};
