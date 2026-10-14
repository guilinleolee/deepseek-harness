# CLAUDE.md 全局个人规则
> 适用于本机所有 Claude Code 会话

## 🚨 硬性强制规则（不可违反）
1. 沟通默认使用中文回复；代码注释优先英文，文档、解释文字使用中文。
2. 修改代码前，先简要说明改动思路，再输出代码。
3. 大规模改动时，分步执行，不要一次性大段覆盖文件；每完成一轮改动，执行对应校验命令。
4. 删除文件、重命名、修改配置、数据库相关操作，**必须先向我确认，得到许可再执行**。
5. 绝不提交 .env、密钥、密码、本地路径到git。
6. 命令执行报错时，完整输出错误栈，不要直接忽略错误尝试修复。
7. 用户提及“天龙引擎”时，统一对应根路径：`C:\Users\li\.claude\projects\dragon-engine`，所有读写、查找、新建相关资源均以此为根目录。

## 📂 自定义资源目录固定路径（dragon‑engine 项目｜天龙引擎）
> 所有相关文件生成、读写、创建、编辑，必须严格使用下面路径，禁止使用默认或其它路径
- agents保存路径：C:\Users\li\.claude\projects\dragon-engine\agents
- commands保存路径：C:\Users\li\.claude\projects\dragon-engine\commands
- hooks保存路径：C:\Users\li\.claude\projects\dragon-engine\hooks
- ip-profiles保存路径：C:\Users\li\.claude\projects\dragon-engine\ip-profiles
- mcp保存路径：C:\Users\li\.claude\projects\dragon-engine\mcp
- memory保存路径：C:\Users\li\.claude\projects\dragon-engine\memory
- plugins保存路径：C:\Users\li\.claude\projects\dragon-engine\plugins
- prompts保存路径：C:\Users\li\.claude\projects\dragon-engine\prompts
- skills保存路径：C:\Users\li\.claude\projects\dragon-engine\skills

> 重要约束：当创建、新增、编辑、读取 agents / commands / hooks / ip‑profiles / mcp / memory / plugins / prompts / skills 相关资源时，**强制写入上面指定目录，不要存到其它位置**；需要新建文件夹就主动创建对应目录。

## 💻 编码风格约定
1. 优先使用现代语法；优先 early‑return，减少深层嵌套。
2. 变量、函数命名语义化；尽量使用 const，少用 let，避免 var。
3. 代码输出尽量完整可直接复制运行，不要只写片段。
4. 输出代码块带上正确语言标记。

## 🛠 工作流与工具偏好
1. 包管理器优先按项目现有，没有明确说明优先 pnpm。
2. 做功能改动之后：执行类型检查、lint；不要盲目自动修复全部lint。
3. 测试优先运行单文件测试，不要无脑跑完整测试套件。
4. Git提交信息遵循 Conventional Commits 规范。

## 📝 输出格式偏好
1. 回答结构清晰，善用标题、列表，减少大段无分割文字。
2. 给出方案时，同时列出风险点与注意事项。
3. 如果需求模糊，先提问澄清，不要自行脑补需求。

## ❌ 禁止行为
- 不要编造不存在的文件、API、命令。
- 不要过度解释基础常识，直奔主题。
- 不要未经确认直接重装、全局修改系统环境。