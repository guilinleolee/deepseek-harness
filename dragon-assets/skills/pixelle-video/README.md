# Pixelle-Video 快速开始

## 一、安装部署

### 1.1 Docker 部署（推荐）

```bash
cd ~/.claude/skills/pixelle-video

# 构建镜像
docker build -t pixelle-video .

# 运行容器
docker run --gpus all -p 8188:8188 \
  -v ~/.claude/skills/pixelle-video/workflows:/workspace/pixelle-workflows \
  pixelle-video
```

### 1.2 手动部署

```bash
# 安装 ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt

# 安装额外依赖
pip install opencv-python Pillow numpy torch torchvision transformers accelerate

# 下载模型到 models/ 目录
# - wan2.1_text2img.safetensors
# - wan2.1_i2v_480p.safetensors
# - wan_vae_bf16.safetensors
# - ChatTTS model
```

## 二、快速使用

### 2.1 检查服务状态

```bash
python3 ~/.claude/skills/pixelle-video/scripts/api_client.py \
  --url http://localhost:8188 --action status
```

### 2.2 查看可用模型

```bash
python3 ~/.claude/skills/pixelle-video/scripts/api_client.py \
  --url http://localhost:8188 --action models
```

### 2.3 生成视频

```python
from scripts.api_client import PixelleClient

client = PixelleClient(base_url="http://localhost:8188")

# 全自动短视频
prompt_id = client.generate_video(
    workflow="full-auto",
    topic="AI Agent发展趋势"
)
if prompt_id:
    result = client.wait_for_completion(prompt_id)
    print(result)
```

### 2.4 数字人口播

```python
# 使用数字人口播工作流
prompt_id = client.generate_video(
    workflow="digital-human",
    params={
        "input_image": "portrait.png",
        "voice_text": "欢迎观看今天的科技分享..."
    }
)
```

## 三、工作流管理

### 3.1 列出所有工作流

```bash
python3 ~/.claude/skills/pixelle-video/scripts/workflow_manager.py --list
```

### 3.2 验证工作流

```bash
python3 ~/.claude/skills/pixelle-video/scripts/workflow_manager.py \
  --validate full-auto
```

### 3.3 查看工作流详情

```bash
python3 ~/.claude/skills/pixelle-video/scripts/workflow_manager.py \
  --info digital-human
```

## 四、可用工作流

| 工作流 | 功能 | 输入 |
|--------|------|------|
| `full-auto` | 全自动短视频 | 主题文字 |
| `digital-human` | 数字人口播 | 图片+文字 |
| `motion-transfer` | 动作迁移 | 图片+视频 |

## 五、API 参考

### PixelleClient

```python
class PixelleClient:
    def get_system_stats() -> Dict
    def get_models() -> List[str]
    def queue_prompt(prompt: Dict) -> Optional[str]
    def get_history(prompt_id: str) -> Dict
    def wait_for_completion(prompt_id: str, ...) -> Dict
    def interrupt() -> bool
    def generate_video(workflow: str, topic: str, ...) -> Optional[str]
```

## 六、故障排除

### 服务无法启动

```bash
# 检查端口占用
netstat -an | grep 8188

# 查看 ComfyUI 日志
docker logs <container_id>
```

### 模型加载失败

```bash
# 检查模型目录
ls -la ComfyUI/models/checkpoints/
ls -la ComfyUI/models/vae/

# 确认模型文件完整
md5sum *.safetensors
```

### 视频生成超时

```python
# 增加超时时间
client = PixelleClient(timeout=600)  # 10分钟
```
