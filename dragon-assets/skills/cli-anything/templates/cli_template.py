"""
CLI-Anything CLI Template
CLI结构模板 - Click命令行接口

特性：
- 子命令 + REPL双模式
- JSON + Human双输出
- 状态持久化
- Undo/Redo支持
"""

import click
import json
import os
import sys
from typing import Optional, Dict, Any

# 导入ReplSkin
# from utils.repl_skin import ReplSkin


# ============================================================
# 全局选项
# ============================================================

@click.group(invoke_without_command=True)
@click.option('--json', 'json_output', is_flag=True, help='Output in JSON format')
@click.option('--project', '-p', type=click.Path(), help='Project file path')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.version_option(version='1.0.0', prog_name='cli-anything-<SOFTWARE>')
@click.pass_context
def cli(ctx, json_output, project, verbose):
    """CLI-Anything for <SOFTWARE>

    Universal CLI interface for controlling <SOFTWARE> programmatically.

    Examples:
        # Create a new project
        cli-anything-<software> project new --width 1920 --height 1080

        # JSON output for agents
        cli-anything-<software> --json layer add -n "Background" --color "#ffffff"

        # Interactive REPL mode
        cli-anything-<software>
    """
    ctx.ensure_object(dict)
    ctx.obj['json_output'] = json_output
    ctx.obj['project'] = project
    ctx.obj['verbose'] = verbose
    ctx.obj['state'] = {}  # 状态存储

    # 无子命令时进入REPL
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl, project_path=project)


# ============================================================
# 项目管理命令
# ============================================================

@cli.group('project')
@click.pass_context
def project(ctx):
    """Project management commands"""
    pass


@project.command('new')
@click.option('--width', '-W', type=int, default=1920, help='Project width')
@click.option('--height', '-H', type=int, default=1080, help='Project height')
@click.option('--name', '-n', default='Untitled', help='Project name')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.pass_context
def project_new(ctx, width, height, name, output):
    """Create a new project"""
    state = {
        'name': name,
        'width': width,
        'height': height,
        'layers': [],
        'history': []
    }

    if output:
        # 保存项目文件
        with open(output, 'w') as f:
            json.dump(state, f, indent=2)

    if ctx.obj['json_output']:
        click.echo(json.dumps({
            'status': 'success',
            'project': state
        }))
    else:
        click.echo(f"✓ Created project: {name} ({width}x{height})")
        if output:
            click.echo(f"  Saved to: {output}")


@project.command('open')
@click.argument('path', type=click.Path(exists=True))
@click.pass_context
def project_open(ctx, path):
    """Open an existing project"""
    with open(path, 'r') as f:
        state = json.load(f)

    ctx.obj['state'] = state
    ctx.obj['project'] = path

    if ctx.obj['json_output']:
        click.echo(json.dumps({
            'status': 'success',
            'project': state
        }))
    else:
        click.echo(f"✓ Opened project: {state.get('name', 'Untitled')}")


@project.command('save')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.pass_context
def project_save(ctx, output):
    """Save current project"""
    path = output or ctx.obj.get('project')
    if not path:
        raise click.ClickException("No project path specified")

    with open(path, 'w') as f:
        json.dump(ctx.obj['state'], f, indent=2)

    if ctx.obj['json_output']:
        click.echo(json.dumps({'status': 'success', 'path': path}))
    else:
        click.echo(f"✓ Saved to: {path}")


@project.command('info')
@click.pass_context
def project_info(ctx):
    """Show project information"""
    state = ctx.obj.get('state', {})

    if ctx.obj['json_output']:
        click.echo(json.dumps(state))
    else:
        click.echo(f"Project: {state.get('name', 'Untitled')}")
        click.echo(f"Size: {state.get('width', 0)}x{state.get('height', 0)}")
        click.echo(f"Layers: {len(state.get('layers', []))}")


# ============================================================
# 核心操作命令（示例）
# ============================================================

@cli.group('layer')
@click.pass_context
def layer(ctx):
    """Layer operations"""
    pass


@layer.command('add')
@click.option('--name', '-n', required=True, help='Layer name')
@click.option('--type', '-t', type=click.Choice(['solid', 'gradient', 'image']),
              default='solid', help='Layer type')
@click.option('--color', '-c', default='#ffffff', help='Color (for solid type)')
@click.pass_context
def layer_add(ctx, name, type, color):
    """Add a new layer"""
    state = ctx.obj['state']
    layer_data = {
        'name': name,
        'type': type,
        'color': color,
        'visible': True
    }

    # 保存到历史（用于undo）
    if 'history' not in state:
        state['history'] = []
    state['history'].append({'action': 'layer_add', 'layer': layer_data})

    # 添加图层
    if 'layers' not in state:
        state['layers'] = []
    state['layers'].append(layer_data)

    if ctx.obj['json_output']:
        click.echo(json.dumps({
            'status': 'success',
            'layer': layer_data,
            'index': len(state['layers']) - 1
        }))
    else:
        click.echo(f"✓ Added layer: {name}")


@layer.command('list')
@click.pass_context
def layer_list(ctx):
    """List all layers"""
    state = ctx.obj['state']
    layers = state.get('layers', [])

    if ctx.obj['json_output']:
        click.echo(json.dumps({'layers': layers}))
    else:
        if not layers:
            click.echo("No layers")
            return
        for i, layer in enumerate(layers):
            status = "👁" if layer.get('visible', True) else " "
            click.echo(f"{i}: [{status}] {layer['name']} ({layer['type']})")


@layer.command('remove')
@click.argument('index', type=int)
@click.pass_context
def layer_remove(ctx, index):
    """Remove a layer by index"""
    state = ctx.obj['state']
    layers = state.get('layers', [])

    if index < 0 or index >= len(layers):
        raise click.ClickException(f"Invalid layer index: {index}")

    removed = layers.pop(index)

    # 保存到历史
    if 'history' not in state:
        state['history'] = []
    state['history'].append({'action': 'layer_remove', 'layer': removed, 'index': index})

    if ctx.obj['json_output']:
        click.echo(json.dumps({'status': 'success', 'removed': removed}))
    else:
        click.echo(f"✓ Removed layer: {removed['name']}")


# ============================================================
# 导出命令
# ============================================================

@cli.command('export')
@click.argument('output', type=click.Path())
@click.option('--format', '-f', type=click.Choice(['png', 'jpg', 'pdf', 'svg']),
              default='png', help='Output format')
@click.option('--quality', '-q', type=int, default=90, help='Output quality (1-100)')
@click.pass_context
def export_cmd(ctx, output, format, quality):
    """Export project to file

    This command calls the real software backend for rendering.
    """
    # TODO: 调用真实软件后端
    # from utils.software_backend import export_project
    # result = export_project(ctx.obj['project'], output, format, quality)

    if ctx.obj['json_output']:
        click.echo(json.dumps({
            'status': 'success',
            'output': output,
            'format': format
        }))
    else:
        click.echo(f"✓ Exported to: {output} ({format})")


# ============================================================
# 会话管理命令
# ============================================================

@cli.command('undo')
@click.pass_context
def undo(ctx):
    """Undo last operation"""
    state = ctx.obj['state']
    history = state.get('history', [])

    if not history:
        if ctx.obj['json_output']:
            click.echo(json.dumps({'status': 'error', 'message': 'Nothing to undo'}))
        else:
            click.echo("Nothing to undo")
        return

    last = history.pop()
    # TODO: 实现实际的undo逻辑

    if ctx.obj['json_output']:
        click.echo(json.dumps({'status': 'success', 'undone': last}))
    else:
        click.echo(f"✓ Undone: {last['action']}")


@cli.command('redo')
@click.pass_context
def redo(ctx):
    """Redo last undone operation"""
    # TODO: 实现redo逻辑
    if ctx.obj['json_output']:
        click.echo(json.dumps({'status': 'error', 'message': 'Nothing to redo'}))
    else:
        click.echo("Nothing to redo")


# ============================================================
# REPL模式
# ============================================================

@cli.command('repl')
@click.option('--project-path', type=click.Path(), help='Project to open')
@click.pass_context
def repl(ctx, project_path):
    """Start interactive REPL mode"""
    # 使用ReplSkin（需要复制repl_skin.py到utils/）
    # skin = ReplSkin("<SOFTWARE>", version="1.0.0")
    # skin.print_banner()
    # pt_session = skin.create_prompt_session()

    click.echo("╔════════════════════════════════════════════╗")
    click.echo("║   CLI-Anything for <SOFTWARE> v1.0.0       ║")
    click.echo("╚════════════════════════════════════════════╝")
    click.echo()
    click.echo("Type 'help' for commands, 'exit' to quit.")
    click.echo()

    # 如果指定了项目，打开它
    if project_path and os.path.exists(project_path):
        with open(project_path, 'r') as f:
            ctx.obj['state'] = json.load(f)
        click.echo(f"Opened: {project_path}")

    # REPL循环
    while True:
        try:
            # 简单的prompt（实际使用ReplSkin更好）
            line = input("cli-anything> ").strip()

            if not line:
                continue

            if line in ['exit', 'quit', 'q']:
                click.echo("Goodbye!")
                break

            if line == 'help':
                # 显示帮助
                with click.Context(cli) as help_ctx:
                    help_ctx.info_name = 'cli-anything-<software>'
                    click.echo(cli.get_help(help_ctx))
                continue

            # 解析并执行命令
            try:
                args = line.split()
                cli.main(args, standalone_mode=False, obj=ctx.obj)
            except click.ClickException as e:
                click.echo(f"Error: {e.message}")
            except SystemExit:
                pass

        except KeyboardInterrupt:
            click.echo("\nUse 'exit' to quit.")
        except EOFError:
            click.echo("\nGoodbye!")
            break


# ============================================================
# 入口点
# ============================================================

if __name__ == '__main__':
    cli(obj={})