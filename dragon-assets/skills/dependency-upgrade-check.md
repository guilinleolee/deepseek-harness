# 名称
dependency-upgrade-check

# 触发
检测到package.json/requirements.txt/go.mod等变更时

# 执行逻辑
1、识别新增、升级、删除的依赖
2、对每个变更依赖:
- 用github MCP查该库的changelog和breaking changes
- 用context7查新版本的API变化
- 扫描项目代码,找出使用该依赖的位置
- 评估影响面(多少文件、是否核心路径)
3、检查依赖树冲突(peerDependencies、版本兼容性)
4、查询CVE数据库,检查已知漏洞
5、生成升级checklist

# 输出
## 升级风险评估
- 高风险依赖(breaking changes多、使用面广)
- 中风险依赖(小改动、局部影响)
- 低风险依赖(bugfix、无API变化)

## 需要人工验证的点
[列出可能出问题的代码位置]

## 建议升级顺序
[从低风险到高风险,逐步验证]

## 回滚预案
[如果升级出问题,怎么快速回退]
