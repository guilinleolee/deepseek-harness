---
license: UNKNOWN
github_repo: Ofnoname/baidu-index-spider
github_hash: a626f1ee87798894ebefaf9fdefa11a36a638321
last_updated: 2026-04-25
source_type: derived
triggers: ["baidu index", "百度指数查询工具"]
---
# 百度指数查询工具

> **安装位置**: `~/.claude/skills/baidu-index/`
> **来源**: [Ofnoname/baidu-index-spider](https://github.com/Ofnoname/baidu-index-spider)

---

## 一、功能说明

- 支持多关键词、多地区查询
- 时间范围：2011年至今
- Web GUI可视化界面
- 支持多个百度账号轮换

---

## 二、配置步骤

### 步骤1：获取百度Cookie

1. 打开浏览器，访问 [百度指数](https://index.baidu.com)
2. 登录你的百度账号
3. 按 `F12` 打开开发者工具
4. 切换到 `Application` 或 `存储` 标签
5. 在 `Cookies` → `https://index.baidu.com` 中找到：
   - `BDUSS` - 复制值
   - `cipherText` - 如果没有，查看教程获取

### 步骤2：配置credential.json

编辑文件：`~/.claude/skills/baidu-index/credential.json`

```json
[
  {
    "cookie_BDUSS": "你的BDUSS值",
    "cipherText": "你的cipherText值"
  }
]
```

可配置多个账号：
```json
[
  {
    "cookie_BDUSS": "账号1的BDUSS",
    "cipherText": "账号1的cipherText"
  },
  {
    "cookie_BDUSS": "账号2的BDUSS",
    "cipherText": "账号2的cipherText"
  }
]
```

---

## 三、使用方法

### 启动Web服务

```bash
cd ~/.claude/skills/baidu-index
py app.py
```

服务启动后，浏览器访问：`http://localhost:5000`

### CLI使用

```python
from spider import Spider

# 创建爬虫实例
spider = Spider()

# 查询单个关键词
result = spider.get_index("超级个体", "2024-01-01", "2024-12-31")

# 查询多个关键词（最多5个）
result = spider.get_index(["超级个体", "一人公司", "个人IP"], "2024-01-01", "2024-12-31")

# 指定地区
result = spider.get_index("超级个体", "2024-01-01", "2024-12-31", region="北京")
```

---

## 四、注意事项

1. **时效性**：爬虫程序随API变动可能失效，请注意时效
2. **请求限制**：单次最多5个关键词，一个关键词最多3个词条
3. **时间范围**：最早只能查询2011年1月的数据
4. **账号安全**：建议使用小号，避免主账号风险

---

## 五、详细教程

- [博客教程](https://www.cnblogs.com/ofnoname/p/18228567)
- [GitHub仓库](https://github.com/Ofnoname/baidu-index-spider)

---

## 六、已安装位置

```
C:\Users\li\.claude\skills\baidu-index\
├── app.py              # 主程序入口
├── spider.py           # 爬虫核心
├── credential.json     # Cookie配置（需要填写）
├── requirements.txt    # 依赖列表
└── webui/              # Web界面
```