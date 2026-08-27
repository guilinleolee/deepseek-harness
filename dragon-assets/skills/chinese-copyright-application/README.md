# 中国软件著作权申请材料生成 Skill

自动分析项目代码，生成符合中国版权保护中心要求的软件著作权申请材料。直接输出 LaTeX 源文件，用 XeLaTeX 编译为 PDF。

## 生成的文档

1. **著作权登记申请表** — 完整的申请信息，含企业工商信息
2. **源程序** — 前30页 + 后30页，共60页，自然分页
3. **用户手册** — 含界面截图占位，不少于10页
4. **设计说明书** — 含界面截图占位，不少于10页
5. **build_all.sh** — 一键编译脚本

## 特点

- 直接生成 LaTeX，精确控制页眉页脚、段首缩进、分页
- 页眉：软件全称V版本号 + 文档类型
- 页脚：第 X 页 共 XX 页
- 自动校验字数限制、日期逻辑、信息一致性
- 自动生成截图清单
- 支持微信小程序、Web应用、移动App、桌面应用等

## 前置条件

安装 XeLaTeX 环境和中文宏包。详见 SKILL.md 中的「LaTeX 环境依赖」章节。

## 文件结构

```
chinese-copyright-application/
├── SKILL.md                              # 主 Skill 文件
├── README.md
└── references/
    ├── requirements.md                   # 详细申请要求
    ├── application-form-template.tex     # 申请表 LaTeX 模板
    ├── source-code-template.tex          # 源程序 LaTeX 模板
    ├── user-manual-template.tex          # 用户手册 LaTeX 模板
    ├── design-doc-template.tex           # 设计说明书 LaTeX 模板
    └── build-script-template.sh          # 编译脚本模板
```
