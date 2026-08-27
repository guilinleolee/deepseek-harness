---
license: UNKNOWN
triggers: ["64-04 金融A2A协调师"]
---
# 64-04 金融A2A协调师

## L0: 一句话描述 (≤15字)
金融多Agent编排协调

## L1: 使用场景 (50-100字)
适用于金融多Agent系统中，负责编排协调量化研究员、策略工程师、算法交易员之间的协作流程，实现研究→策略→执行的自动化闭环。

## L2: 详细文档

### 角色定义

```yaml
编号: 64-04
名称: 金融A2A协调师
英文: Financial A2A Coordinator
类别: 投资中心-量化投资
思维模型: 系统协调思维 (Coordination Engineering)
核心能力:
  - 多Agent编排 (量化研究员/策略工程师/交易员)
  - A2A协议管理 (Agent-to-Agent通信)
  - 流水线编排 (研究→策略→执行)
  - 人机协同 (HITL审批流)
  - 实时监控 (多Agent状态)

技术栈:
  - Agno Framework (A2A协议)
  - Python 3.12+
  - ValueCell Trading Agent
  - LanceDB (状态存储)
  - Streaming Pipeline

上游角色:
  - 60-01 投资总监 (投资决策)
  - 64-01 量化研究员 (研究方向)
  - 64-03 量化策略工程师 (策略实现)

下游角色:
  - 64-02 算法交易员 (策略执行)
  - 64-03 量化策略工程师 (策略开发)

触发关键词:
  - "编排执行"
  - "A2A协调"
  - "多Agent协作"
  - "流水线管理"
  - "人机协同"
```

### A2A协调架构

```python
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
import asyncio
import uuid


class AgentRole(str, Enum):
    """金融Agent角色"""
    RESEARCHER = "researcher"      # 量化研究员 (64-01)
    STRATEGIST = "strategist"      # 策略工程师 (64-03)
    TRADER = "trader"            # 算法交易员 (64-02)


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WAITING_HITL = "waiting_hitl"  # 等待人工审批
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentMessage:
    """Agent间通信消息（V11.11 P0-3升级：标准化协议+相关性追踪）"""
    msg_id: str
    msg_type: MessageType  # V11.11 P0-3新增：消息类型标准化
    from_agent: AgentRole
    to_agent: AgentRole
    content: Dict[str, Any]
    timestamp: datetime
    correlation_id: str  # V11.11 P0-3新增：关联追踪request-response
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent_id: Optional[str] = None  # V11.11 P0-3新增：消息链父消息ID


@dataclass
class PipelineTask:
    """流水线任务"""
    task_id: str
    pipeline_type: str  # research_to_strategy, strategy_to_execution
    stages: List[str]
    current_stage: int
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    hitl_approvals: List[Dict] = field(default_factory=list)
    # P0-3 新增：相关性追踪字段（V11.11）
    correlation_ids: List[str] = field(default_factory=list)  # 关联消息ID列表
    message_correlation_map: Dict[str, str] = field(default_factory=dict)  # stage → correlation_id映射
    pending_correlation_ids: List[str] = field(default_factory=list)  # 等待响应的correlation_id队列
    parent_correlation_id: Optional[str] = None  # 父任务correlation_id，支持任务树

class FinancialA2ACoordinator:
    """金融A2A协调器"""

    def __init__(self):
        self.agents: Dict[AgentRole, Any] = {}
        self.pipeline_tasks: Dict[str, PipelineTask] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.hitl_queue: asyncio.Queue = asyncio.Queue()

    async def register_agent(self, role: AgentRole, agent: Any):
        """注册Agent到协调器"""
        self.agents[role] = agent

    async def send_message(
        self,
        from_agent: AgentRole,
        to_agent: AgentRole,
        content: Dict[str, Any],
        msg_type: MessageType = MessageType.TASK_REQUEST,
        correlation_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """发送Agent间消息（V11.11 P0-3升级：标准化协议+相关性追踪）"""
        # 生成correlation_id用于追踪request-response对
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())

        msg = AgentMessage(
            msg_id=f"msg_{uuid.uuid4().hex[:12]}",
            msg_type=msg_type,
            from_agent=from_agent,
            to_agent=to_agent,
            content=content,
            timestamp=datetime.now(),
            correlation_id=correlation_id,
            metadata=metadata or {},
            parent_id=parent_id
        )
        await self.message_queue.put(msg)
        return msg.msg_id

    async def send_response(
        self,
        request_msg_id: str,
        from_agent: AgentRole,
        to_agent: AgentRole,
        content: Dict[str, Any],
        status: str = "success",
        metadata: Optional[Dict] = None
    ) -> str:
        """创建响应消息，关联到原始请求（V11.11 P0-3升级：相关性追踪）"""
        msg = AgentMessage(
            msg_id=f"msg_{uuid.uuid4().hex[:12]}",
            msg_type=MessageType.TASK_RESPONSE,
            from_agent=from_agent,
            to_agent=to_agent,
            content=content,
            timestamp=datetime.now(),
            correlation_id=request_msg_id,  # 关联到原始请求
            metadata={**(metadata or {}), "status": status, "request_id": request_msg_id},
            parent_id=request_msg_id  # 消息链追踪
        )
        await self.message_queue.put(msg)
        return msg.msg_id

    async def get_correlated_messages(self, correlation_id: str) -> List[AgentMessage]:
        """获取所有关联到同一correlation_id的消息（V11.11 P0-3升级：相关性追踪）"""
        correlated = []
        temp_queue = asyncio.Queue()
        # 遍历消息队列查找关联消息
        while not self.message_queue.empty():
            msg = await self.message_queue.get()
            if msg.correlation_id == correlation_id:
                correlated.append(msg)
            await temp_queue.put(msg)
        # 恢复原队列
        while not temp_queue.empty():
            await self.message_queue.put(await temp_queue.get())
        return correlated

    async def get_pipeline_message_tree(self, task_id: str) -> Dict[str, Any]:
        """获取流水线任务的消息树（V11.11 P0-3新增：相关性追踪增强）

        Returns:
            Dict containing task info and all correlated messages organized by stage
        """
        task = self.pipeline_tasks.get(task_id)
        if not task:
            return {"error": "Task not found", "task_id": task_id}

        # 收集该任务所有相关消息
        all_messages = []
        for corr_id in task.correlation_ids:
            msgs = await self.get_correlated_messages(corr_id)
            all_messages.extend(msgs)

        # 按stage组织消息树
        message_tree = {
            "task_id": task_id,
            "pipeline_type": task.pipeline_type,
            "status": task.status.value,
            "current_stage": task.current_stage,
            "stages": task.stages,
            "correlation_ids": task.correlation_ids,
            "message_count": len(all_messages),
            "messages_by_stage": {},
            "pending_approvals": [],
            "completed_stages": [],
        }

        # 按stage分类消息
        for stage_name, stage_corr_id in task.message_correlation_map.items():
            stage_messages = [m for m in all_messages if m.correlation_id == stage_corr_id]
            message_tree["messages_by_stage"][stage_name] = {
                "correlation_id": stage_corr_id,
                "message_count": len(stage_messages),
                "messages": [
                    {
                        "msg_id": m.msg_id,
                        "type": m.msg_type.value,
                        "from": m.from_agent.value,
                        "to": m.to_agent.value,
                        "timestamp": m.timestamp.isoformat(),
                    }
                    for m in stage_messages
                ]
            }

        # 收集待审批
        for approval in task.hitl_approvals:
            if not approval.get("approved"):
                message_tree["pending_approvals"].append(approval)

        # 记录已完成阶段
        for i in range(task.current_stage):
            if i < len(task.stages):
                message_tree["completed_stages"].append(task.stages[i])

        return message_tree

    async def create_pipeline(
        self,
        pipeline_type: str,
        initial_context: Dict[str, Any]
    ) -> str:
        """创建流水线任务"""
        pipeline_stages = self._get_pipeline_stages(pipeline_type)
        task = PipelineTask(
            task_id=f"pipeline_{datetime.now().timestamp()}",
            pipeline_type=pipeline_type,
            stages=pipeline_stages,
            current_stage=0,
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            context=initial_context
        )
        self.pipeline_tasks[task.task_id] = task
        return task.task_id

    def _get_pipeline_stages(self, pipeline_type: str) -> List[str]:
        """获取流水线阶段"""
        pipelines = {
            "research_to_strategy": [
                "research_init",      # 研究初始化
                "data_collection",    # 数据采集
                "analysis",           # 分析
                "strategy_generation", # 策略生成
                "backtest_validation", # 回测验证
                "hitl_approval",     # 人工审批
                "strategy_ready"      # 策略就绪
            ],
            "strategy_to_execution": [
                "strategy_review",    # 策略审查
                "risk_validation",   # 风控验证
                "execution_prep",    # 执行准备
                "hitl_approval",      # 人工审批
                "execution_start",   # 开始执行
                "monitoring",         # 监控
                "execution_complete"  # 执行完成
            ]
        }
        return pipelines.get(pipeline_type, [])

    async def execute_pipeline(self, task_id: str) -> Dict[str, Any]:
        """执行流水线"""
        task = self.pipeline_tasks.get(task_id)
        if not task:
            raise ValueError(f"Pipeline {task_id} not found")

        task.status = TaskStatus.IN_PROGRESS

        while task.current_stage < len(task.stages):
            stage = task.stages[task.current_stage]

            # 检查是否需要HITL
            if self._requires_hitl(stage):
                task.status = TaskStatus.WAITING_HITL
                await self._request_hitl_approval(task, stage)
                continue

            # 执行阶段
            result = await self._execute_stage(task, stage)
            task.context.update(result)
            task.current_stage += 1
            task.updated_at = datetime.now()

        task.status = TaskStatus.COMPLETED
        return task.context

    def _requires_hitl(self, stage: str) -> bool:
        """判断是否需要人工审批"""
        hitl_stages = {"hitl_approval", "execution_start"}
        return stage in hitl_stages

    async def _request_hitl_approval(self, task: PipelineTask, stage: str):
        """请求人工审批"""
        approval_request = {
            "task_id": task.task_id,
            "stage": stage,
            "context": task.context,
            "timestamp": datetime.now()
        }
        await self.hitl_queue.put(approval_request)

    async def hitl_approve(self, task_id: str, approved: bool, notes: str = ""):
        """人工审批回调（V11.11 P0-3增强：关联correlation_id）

        Args:
            task_id: 任务ID
            approved: 是否批准
            notes: 审批备注
        """
        task = self.pipeline_tasks.get(task_id)
        if not task:
            return

        # V11.11 P0-3新增：从pending_correlation_ids提取当前审批关联ID
        correlation_id = task.pending_correlation_ids[-1] if task.pending_correlation_ids else None

        task.hitl_approvals.append({
            "stage": task.stages[task.current_stage],
            "approved": approved,
            "notes": notes,
            "timestamp": datetime.now(),
            # V11.11 P0-3新增：审批记录关联追踪
            "correlation_id": correlation_id,
            "parent_correlation_id": task.parent_correlation_id,
        })

        if approved:
            task.current_stage += 1
            task.status = TaskStatus.IN_PROGRESS
            task.updated_at = datetime.now()
        else:
            task.status = TaskStatus.CANCELLED

    async def _execute_stage(self, task: PipelineTask, stage: str) -> Dict:
        """执行单个阶段"""
        handlers = {
            "research_init": self._handle_research_init,
            "data_collection": self._handle_data_collection,
            "analysis": self._handle_analysis,
            "strategy_generation": self._handle_strategy_generation,
            "backtest_validation": self._handle_backtest,
            "strategy_review": self._handle_strategy_review,
            "risk_validation": self._handle_risk_validation,
            "execution_prep": self._handle_execution_prep,
            "monitoring": self._handle_monitoring,
        }

        handler = handlers.get(stage)
        if handler:
            return await handler(task.context)

        return {"stage": stage, "status": "completed"}

    async def get_pipeline_status(self, task_id: str) -> Dict:
        """获取流水线状态"""
        task = self.pipeline_tasks.get(task_id)
        if not task:
            return {"error": "Pipeline not found"}

        return {
            "task_id": task.task_id,
            "pipeline_type": task.pipeline_type,
            "status": task.status.value,
            "current_stage": task.current_stage,
            "stage_name": task.stages[task.current_stage] if task.current_stage < len(task.stages) else "completed",
            "progress": f"{task.current_stage}/{len(task.stages)}",
            "hitl_approvals": len(task.hitl_approvals),
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat()
        }
```

### P0升级：HITL审批UI (Streamlit可视化审批面板)

> V11.11 P0-3升级：解决"无可视化审批界面"问题，提供实时审批面板

#### Streamlit审批面板组件

```python
import streamlit as st
import asyncio
import uuid
from datetime import datetime
from financial_a2a_coordinator import (
    FinancialA2ACoordinator,
    AgentRole,
    TaskStatus,
    MessageType,
)


class HITLApprovalPanel:
    """HITL人工审批UI面板（V11.11 P0-3升级）"""

    def __init__(self, coordinator: FinancialA2ACoordinator):
        self.coordinator = coordinator
        self._refresh_interval = 2  # 秒

    def render(self):
        """渲染审批面板"""
        st.set_page_config(
            page_title="金融A2A审批中心",
            page_icon="🔐",
            layout="wide"
        )

        st.title("🔐 金融A2A协调中心 - HITL审批面板")
        st.caption(f"自动刷新间隔: {self._refresh_interval}秒 | 实时监控审批队列")

        # 侧边栏：系统状态
        self._render_sidebar()

        # 主区域：待审批任务
        self._render_pending_approvals()

        # 底部：审批历史
        self._render_approval_history()

        # 自动刷新
        st.rerun()

    def _render_sidebar(self):
        """侧边栏：系统概览"""
        with st.sidebar:
            st.header("📊 系统状态")

            # Agent状态
            st.subheader("Agent状态")
            for role, agent in self.coordinator.agents.items():
                status_color = "🟢" if agent else "🔴"
                st.write(f"{status_color} {role.value}")

            # 流水线概览
            st.subheader("流水线概览")
            total = len(self.coordinator.pipeline_tasks)
            pending = sum(
                1 for t in self.coordinator.pipeline_tasks.values()
                if t.status == TaskStatus.PENDING
            )
            in_progress = sum(
                1 for t in self.coordinator.pipeline_tasks.values()
                if t.status == TaskStatus.IN_PROGRESS
            )
            waiting_hitl = sum(
                1 for t in self.coordinator.pipeline_tasks.values()
                if t.status == TaskStatus.WAITING_HITL
            )
            completed = sum(
                1 for t in self.coordinator.pipeline_tasks.values()
                if t.status == TaskStatus.COMPLETED
            )

            col1, col2 = st.columns(2)
            col1.metric("总计", total)
            col1.metric("待处理", pending)
            col2.metric("进行中", in_progress)
            col2.metric("⏳待审批", waiting_hitl)

            st.metric("✅已完成", completed)

            # 刷新控制
            st.subheader("⚙️ 控制")
            self._refresh_interval = st.slider(
                "刷新间隔(秒)",
                min_value=1,
                max_value=10,
                value=self._refresh_interval
            )

    def _render_pending_approvals(self):
        """主区域：待审批任务列表"""
        st.header("⏳ 待审批任务")

        # 获取所有待审批的流水线
        pending_tasks = [
            task for task in self.coordinator.pipeline_tasks.values()
            if task.status == TaskStatus.WAITING_HITL
        ]

        if not pending_tasks:
            st.info("📭 当前没有待审批的任务")
            return

        for task in pending_tasks:
            self._render_approval_card(task)

    def _render_approval_card(self, task):
        """渲染单个审批卡片"""
        current_stage = task.stages[task.current_stage]

        with st.container():
            col1, col2 = st.columns([4, 1])

            with col1:
                st.subheader(f"📋 {task.task_id}")

                # 基本信息
                st.write(f"**类型:** {task.pipeline_type}")
                st.write(f"**阶段:** {current_stage}")
                st.write(f"**进度:** {task.current_stage}/{len(task.stages)}")
                st.write(f"**创建时间:** {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

                # 审批历史
                if task.hitl_approvals:
                    st.write("**历史审批:**")
                    for approval in task.hitl_approvals:
                        icon = "✅" if approval["approved"] else "❌"
                        st.write(f"  {icon} [{approval['stage']}] {approval['notes'][:50]}...")

                # 上下文详情
                if task.context:
                    with st.expander("📄 查看上下文详情"):
                        st.json(task.context)

            with col2:
                st.write("**操作:**")

                # 审批操作
                if st.button(f"✅ 批准", key=f"approve_{task.task_id}", type="primary"):
                    notes = st.text_area(
                        "审批备注(可选)",
                        key=f"notes_approve_{task.task_id}",
                        placeholder="输入审批意见..."
                    )
                    if st.button("确认批准", key=f"confirm_approve_{task.task_id}"):
                        asyncio.run(
                            self.coordinator.hitl_approve(task.task_id, True, notes or "")
                        )
                        st.success(f"✅ 已批准 {task.task_id}")
                        st.rerun()

                if st.button(f"❌ 拒绝", key=f"reject_{task.task_id}", type="secondary"):
                    notes = st.text_area(
                        "拒绝原因(必填)",
                        key=f"notes_reject_{task.task_id}",
                        placeholder="说明拒绝原因..."
                    )
                    if st.button("确认拒绝", key=f"confirm_reject_{task.task_id}"):
                        if notes:
                            asyncio.run(
                                self.coordinator.hitl_approve(task.task_id, False, notes)
                            )
                            st.error(f"❌ 已拒绝 {task.task_id}")
                            st.rerun()
                        else:
                            st.warning("请填写拒绝原因")

                if st.button(f"🔍 查看详情", key=f"detail_{task.task_id}"):
                    st.session_state[f"detail_view_{task.task_id}"] = True

            st.divider()

    def _render_approval_history(self):
        """底部：审批历史"""
        st.header("📜 审批历史")

        # 收集所有审批记录
        all_approvals = []
        for task in self.coordinator.pipeline_tasks.values():
            for approval in task.hitl_approvals:
                all_approvals.append({
                    **approval,
                    "task_id": task.task_id,
                    "pipeline_type": task.pipeline_type
                })

        if not all_approvals:
            st.info("暂无审批历史记录")
            return

        # 按时间倒序
        all_approvals.sort(key=lambda x: x["timestamp"], reverse=True)

        # 表格展示
        import pandas as pd
        df = pd.DataFrame([
            {
                "时间": a["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                "任务ID": a["task_id"],
                "阶段": a["stage"],
                "结果": "✅批准" if a["approved"] else "❌拒绝",
                "备注": a["notes"][:100] if a["notes"] else ""
            }
            for a in all_approvals[:50]  # 最近50条
        ])

        st.dataframe(df, use_container_width=True, hide_index=True)


# 启动审批面板
if __name__ == "__main__":
    coordinator = FinancialA2ACoordinator()

    # 注册Agent（示例）
    # await coordinator.register_agent(AgentRole.RESEARCHER, researcher_agent)
    # await coordinator.register_agent(AgentRole.STRATEGIST, strategist_agent)
    # await coordinator.register_agent(AgentRole.TRADER, trader_agent)

    panel = HITLApprovalPanel(coordinator)
    panel.render()
```

#### 审批面板核心特性

| 特性 | 说明 |
|------|------|
| **实时轮询** | 自动刷新审批队列，间隔可调(1-10秒) |
| **流水线概览** | 侧边栏显示各状态任务统计 |
| **审批卡片** | 展示任务ID、类型、阶段、上下文详情 |
| **批准/拒绝** | 按钮触发，支持审批备注 |
| **审批历史** | 表格展示最近50条审批记录 |
| **上下文查看** | 可展开JSON查看完整上下文 |

#### 与协调器集成

```python
# 集成示例
async def main():
    coordinator = FinancialA2ACoordinator()

    # 注册Agent
    researcher = QuantResearcherAgent()
    strategist = StrategyEngineerAgent()
    trader = AlgoTraderAgent()

    await coordinator.register_agent(AgentRole.RESEARCHER, researcher)
    await coordinator.register_agent(AgentRole.STRATEGIST, strategist)
    await coordinator.register_agent(AgentRole.TRADER, trader)

    # 创建流水线
    task_id = await coordinator.create_pipeline(
        "research_to_strategy",
        {"research_topic": "BTC永续合约趋势跟踪"}
    )

    # 执行流水线（审批在Streamlit面板中处理）
    result = await coordinator.execute_pipeline(task_id)
    print(f"流水线完成: {result}")


# 启动审批面板（单独进程）
def start_approval_panel():
    import subprocess
    subprocess.run([
        "streamlit", "run",
        "hitl_approval_panel.py",
        "--server.port", "8501",
        "--server.headless", "true"
    ])


# 或使用fastapi集成
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="金融A2A协调API")

@app.post("/api/hitl/pending")
async def get_pending_approvals():
    """获取待审批列表"""
    return [
        {
            "task_id": t.task_id,
            "stage": t.stages[t.current_stage],
            "context": t.context
        }
        for t in coordinator.pipeline_tasks.values()
        if t.status == TaskStatus.WAITING_HITL
    ]

@app.post("/api/hitl/approve")
async def approve_task(task_id: str, notes: str = ""):
    """批准任务"""
    await coordinator.hitl_approve(task_id, True, notes)
    return {"status": "approved"}

@app.post("/api/hitl/reject")
async def reject_task(task_id: str, reason: str):
    """拒绝任务"""
    await coordinator.hitl_approve(task_id, False, reason)
    return {"status": "rejected"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### Gradio替代方案（轻量级）

```python
import gradio as gr

def create_hitl_gradio(coordinator: FinancialA2ACoordinator):
    """Gradio轻量级审批UI"""

    with gr.Blocks(title="金融A2A审批中心") as demo:
        gr.Markdown("# 🔐 金融A2A审批中心")

        # 状态显示
        status_box = gr.JSON(label="系统状态", every=2)

        def get_status():
            return {
                "总任务": len(coordinator.pipeline_tasks),
                "待审批": sum(
                    1 for t in coordinator.pipeline_tasks.values()
                    if t.status == TaskStatus.WAITING_HITL
                ),
                "进行中": sum(
                    1 for t in coordinator.pipeline_tasks.values()
                    if t.status == TaskStatus.IN_PROGRESS
                )
            }

        # 审批面板
        with gr.Tab("待审批"):
            task_dropdown = gr.Dropdown(
                label="选择任务",
                choices=[
                    (f"{t.task_id} [{t.stages[t.current_stage]}]", t.task_id)
                    for t in coordinator.pipeline_tasks.values()
                    if t.status == TaskStatus.WAITING_HITL
                ]
            )
            context_display = gr.JSON(label="任务上下文")
            notes_input = gr.Textbox(label="审批备注")

            with gr.Row():
                approve_btn = gr.Button("✅ 批准", variant="primary")
                reject_btn = gr.Button("❌ 拒绝", variant="stop")

            def handle_approve(task_id, notes):
                if not task_id:
                    return "请选择任务"
                asyncio.run(coordinator.hitl_approve(task_id, True, notes or ""))
                return f"已批准: {task_id}"

            def handle_reject(task_id, notes):
                if not task_id:
                    return "请选择任务"
                if not notes:
                    return "拒绝时必须填写原因"
                asyncio.run(coordinator.hitl_approve(task_id, False, notes))
                return f"已拒绝: {task_id}"

            approve_btn.click(handle_approve, [task_dropdown, notes_input], status_box)
            reject_btn.click(handle_reject, [task_dropdown, notes_input], status_box)

        gr.Timer(2).tick(get_status, None, status_box)

    return demo
```

---

### 流水线编排

#### 1. 研究→策略流水线

```
┌─────────────────────────────────────────────────────────────┐
│          Research → Strategy Pipeline                          │
├─────────────────────────────────────────────────────────────┤
│  64-01 量化研究员                                           │
│  ├── 生成研究方向                                            │
│  ├── 数据采集 (Binance/OKX/Hyperliquid)                   │
│  └── 输出: 研究报告 + 信号候选                               │
│                        ↓                                    │
│  64-03 量化策略工程师                                        │
│  ├── 策略建模 (趋势跟踪/均值回归/统计套利)                   │
│  ├── 回测验证 (Backtrader/Zipline)                        │
│  └── 输出: 策略代码 + 回测报告                               │
│                        ↓                                    │
│  64-04 金融A2A协调师                                        │
│  ├── 策略审查                                               │
│  ├── HITL审批 (可选)                                       │
│  └── 触发策略就绪事件                                       │
│                        ↓                                    │
│  64-02 算法交易员                                           │
│  ├── 策略加载                                              │
│  ├── 风控验证                                              │
│  └── 实盘执行                                              │
└─────────────────────────────────────────────────────────────┘
```

#### 2. A2A消息流

```python
# 消息类型定义
class MessageType(str, Enum):
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    STATUS_UPDATE = "status_update"
    APPROVAL_REQUEST = "approval_request"
    APPROVAL_RESPONSE = "approval_response"
    HEARTBEAT = "heartbeat"
    ERROR = "error"


# 标准化消息格式
{
    "msg_id": "uuid",
    "type": "task_request|task_response|...",
    "from": "64-01|64-03|64-04|64-02",
    "to": "64-01|64-03|64-04|64-02",
    "payload": {
        "content": {},
        "metadata": {}
    },
    "timestamp": "ISO8601",
    "correlation_id": "uuid"  # 关联追踪
}
```

### 核心命令

```bash
# 流水线管理
[@64-04] 创建研究→策略流水线
[@64-04] 创建策略→执行流水线
[@64-04] 查看流水线状态

# A2A协调
[@64-04] 协调量化研究员生成策略
[@64-04] 协调策略工程师执行回测
[@64-04] 协调交易员执行策略

# HITL管理
[@64-04] 请求策略审批
[@64-04] 请求交易审批
[@64-04] 审批通过/拒绝

# 监控
[@64-04] 查看所有Agent状态
[@64-04] 查看消息队列
[@64-04] 查看待审批任务
```

### 与现有天龙组件协同

| 天龙组件 | 协同方式 | 效果 |
|---------|---------|------|
| **64-01 量化研究员** | 研究报告 → A2A消息 → 策略工程师 | 研究→落地闭环 |
| **64-03 量化策略工程师** | 策略代码 → A2A消息 → 交易员 | 策略→执行闭环 |
| **64-02 算法交易员** | 执行结果 → A2A消息 → 协调师 | 执行→反馈闭环 |
| **60-01 投资总监** | 投资决策 → HITL审批 → 协调师 | 监督→执行闭环 |
| **ValueCell Trading Agent** | A2A协议实现 | 消息路由 |

### 预期收益

| 指标 | 效果 |
|------|------|
| **编排效率** | +500% (自动化流水线) |
| **协调延迟** | -80% (A2A直连) |
| **人机协同** | 标准化审批流 |
| **错误率** | -60% (统一协调) |

### 技能文件

- [skills/valuecell-trading-agent/SKILL.md](skills/valuecell-trading-agent/SKILL.md)
- [skills/valuecell-deep-research/SKILL.md](skills/valuecell-deep-research/SKILL.md)
- [skills/valuecell-trading-agent/scripts/trading_client.py](skills/valuecell-trading-agent/scripts/trading_client.py)
- [skills/valuecell-deep-research/scripts/research_client.py](skills/valuecell-deep-research/scripts/research_client.py)
