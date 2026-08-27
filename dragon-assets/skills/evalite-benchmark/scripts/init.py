#!/usr/bin/env python3
"""
evalite-benchmark 项目初始化脚本
用于创建新的 benchmark 项目结构
"""

import argparse
import json
import os
import shutil
from pathlib import Path


def get_project_template() -> dict:
    """获取项目模板配置"""
    return {
        "name": "",
        "version": "1.0.0",
        "models": [],
        "dataset": {
            "source": "./datasets/custom.json",
            "format": "json",
            "shuffle": True
        },
        "evaluation": {
            "trials": 5,
            "timeout": 30,
            "parallel": True,
            "max_parallel_models": 3
        },
        "statistical": {
            "test": "t-test",
            "alpha": 0.05,
            "confidence_interval": 0.95
        },
        "reporting": {
            "formats": ["html", "markdown", "json"],
            "output_dir": "./results",
            "include_charts": True
        },
        "regression": {
            "enabled": False,
            "baseline_file": "./results/baseline.json",
            "alert_threshold": 0.05
        }
    }


def get_dataset_template() -> dict:
    """获取数据集模板"""
    return {
        "name": "custom-benchmark",
        "version": "1.0.0",
        "description": "Custom LLM Benchmark Dataset",
        "tasks": [
            {
                "id": "example-001",
                "question": "What is the capital of France?",
                "choices": ["London", "Paris", "Berlin", "Madrid"],
                "answer": "Paris",
                "category": "geography",
                "difficulty": "easy"
            }
        ],
        "metadata": {
            "source": "custom",
            "created": "",
            "license": "MIT"
        }
    }


def create_project_structure(project_name: str, output_dir: Path) -> None:
    """创建项目目录结构"""
    project_dir = output_dir / project_name

    dirs = [
        project_dir / "configs",
        project_dir / "datasets",
        project_dir / "results",
        project_dir / "scripts",
        project_dir / "templates"
    ]

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        # 创建 .gitkeep
        gitkeep = d / ".gitkeep"
        gitkeep.touch()

    print(f"✓ Created project structure: {project_dir}")


def create_config_file(project_name: str, output_dir: Path) -> None:
    """创建默认配置文件"""
    project_dir = output_dir / project_name
    config_path = project_dir / "configs" / "benchmark_config.yaml"

    config = get_project_template()
    config["name"] = project_name

    import yaml
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    print(f"✓ Created config: {config_path}")


def create_dataset_template(project_name: str, output_dir: Path) -> None:
    """创建数据集模板"""
    project_dir = output_dir / project_name
    dataset_path = project_dir / "datasets" / "custom.json"

    dataset = get_dataset_template()
    dataset["metadata"]["created"] = ""

    with open(dataset_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)

    print(f"✓ Created dataset template: {dataset_path}")


def create_readme(project_name: str, output_dir: Path) -> None:
    """创建 README 文件"""
    project_dir = output_dir / project_name
    readme_path = project_dir / "README.md"

    readme_content = f"""# {project_name}

LLM Benchmark Evaluation Project

## 结构

```
{project_name}/
├── configs/
│   └── benchmark_config.yaml    # Benchmark 配置
├── datasets/
│   └── custom.json              # 测试数据集
├── results/                      # 评估结果输出
├── scripts/                      # 辅助脚本
└── templates/                    # 模板文件
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r ~/.claude/skills/evalite-benchmark/requirements.txt
```

### 2. 运行评估

```bash
cd {project_name}
python scripts/benchmark_runner.py run --config configs/benchmark_config.yaml
```

### 3. 查看结果

```bash
python scripts/benchmark_runner.py leaderboard
```

## 配置说明

编辑 `configs/benchmark_config.yaml` 来自定义评估参数。
"""

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"✓ Created README: {readme_path}")


def init_project(name: str, output_dir: Path = None) -> None:
    """初始化新的 benchmark 项目"""
    if output_dir is None:
        output_dir = Path.cwd()

    print(f"\n📁 初始化项目: {name}")
    print("=" * 50)

    # 创建目录结构
    create_project_structure(name, output_dir)

    # 创建配置文件
    create_config_file(name, output_dir)

    # 创建数据集模板
    create_dataset_template(name, output_dir)

    # 创建 README
    create_readme(name, output_dir)

    print("\n" + "=" * 50)
    print(f"✅ 项目初始化完成!")
    print(f"\n下一步:")
    print(f"  1. 编辑 configs/benchmark_config.yaml 配置模型")
    print(f"  2. 编辑 datasets/custom.json 添加测试数据")
    print(f"  3. 运行 python scripts/benchmark_runner.py run")
    print()


def main():
    parser = argparse.ArgumentParser(description="初始化 evalite-benchmark 项目")
    parser.add_argument("--name", "-n", required=True, help="项目名称")
    parser.add_argument("--output", "-o", type=Path, default=Path.cwd(), help="输出目录")

    args = parser.parse_args()
    init_project(args.name, args.output)


if __name__ == "__main__":
    main()