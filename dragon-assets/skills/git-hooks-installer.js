#!/usr/bin/env node

/**
 * Git Hooks 安装工具
 * 自动安装和配置Git提交信息验证hooks
 */

const fs = require('fs');
const path = require('path');

class GitHooksInstaller {
  constructor(projectPath = process.cwd()) {
    this.projectPath = projectPath;
    this.gitDir = path.join(projectPath, '.git');
    this.hooksDir = path.join(this.gitDir, 'hooks');
  }

  checkGitRepository() {
    if (!fs.existsSync(this.gitDir)) {
      throw new Error('当前目录不是一个Git仓库');
    }

    if (!fs.existsSync(this.hooksDir)) {
      fs.mkdirSync(this.hooksDir, { recursive: true });
    }

    return true;
  }

  installPreCommitHook() {
    const preCommitPath = path.join(this.hooksDir, 'pre-commit');
    const preCommitContent = `#!/bin/sh
# Git提交信息验证 - Pre-commit Hook
# 由git-commit-standard自动生成

echo "正在检查提交信息格式..."

# 获取当前提交信息
commit_msg=$(cat "$1")

# 验证提交信息格式
node "${path.resolve(__dirname, 'git-commit-validator.js')}" "$commit_msg"

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 提交信息格式验证失败"
    echo "请查看上方的错误信息并修正提交格式"
    echo ""
    echo "建议格式: <type>[optional scope]: <description>"
    echo "示例: feat(auth): 添加用户登录功能"
    echo ""
    exit 1
fi

echo "✅ 提交信息格式验证通过"
exit 0
`;

    fs.writeFileSync(preCommitPath, preCommitContent, { mode: 0o755 });
    console.log('✅ Pre-commit hook 安装成功');
  }

  installCommitMsgHook() {
    const commitMsgPath = path.join(this.hooksDir, 'commit-msg');
    const commitMsgContent = `#!/bin/sh
# Git提交信息验证 - Commit-msg Hook
# 由git-commit-standard自动生成

echo "正在验证提交信息..."

# 验证提交信息格式
node "${path.resolve(__dirname, 'git-commit-validator.js')}" --strict "$(cat "$1")"

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 提交信息格式验证失败"
    echo "请查看上方的错误信息并修正提交格式"
    echo ""
    echo "使用以下命令重新提交:"
    echo "  git commit -m \"<type>(<scope>): <description>\""
    echo ""
    echo "示例:"
    echo "  git commit -m \"feat(auth): 添加用户登录功能\""
    echo "  git commit -m \"fix: 修复登录验证bug\""
    echo ""
    exit 1
fi

echo "✅ 提交信息验证通过"
exit 0
`;

    fs.writeFileSync(commitMsgPath, commitMsgContent, { mode: 0o755 });
    console.log('✅ Commit-msg hook 安装成功');
  }

  installPrePushHook() {
    const prePushPath = path.join(this.hooksDir, 'pre-push');
    const prePushContent = `#!/bin/sh
# Git推送前检查 - Pre-push Hook
# 由git-commit-standard自动生成

echo "正在检查即将推送的提交..."

# 获取即将推送的提交数量
remote=$1
url=$2

# 读取推送的提交信息
while read local_ref local_sha remote_ref remote_sha; do
    if [ "$local_sha" != "0000000000000000000000000000000000000000" ]; then
        # 获取提交范围
        if [ "$remote_sha" = "0000000000000000000000000000000000000000" ]; then
            # 新分支推送
            range="HEAD~10..HEAD"
        else
            # 更新现有分支
            range="$remote_sha..$local_sha"
        fi

        # 检查每个提交信息
        invalid_commits=$(git log --format='%B' "$range" | while read commit_msg; do
            if [ -n "$commit_msg" ]; then
                node "${path.resolve(__dirname, 'git-commit-validator.js')}" "$commit_msg" >/dev/null 2>&1
                if [ $? -ne 0 ]; then
                    echo "1"
                fi
            fi
        done | grep -c "1" || true)

        if [ "$invalid_commits" -gt 0 ]; then
            echo ""
            echo "❌ 发现 $invalid_commits 个不符合规范的提交信息"
            echo "请修正提交信息后再推送"
            echo ""
            echo "查看问题提交:"
            echo "  git log --format='%H %s' $range | head -n 5"
            echo ""
            echo "修正方法:"
            echo "  1. 使用 git rebase -i 修改历史提交"
            echo "  2. 使用 git commit --amend 修改最后一次提交"
            echo ""
            exit 1
        fi
    fi
done

echo "✅ 所有提交信息格式正确"
exit 0
`;

    fs.writeFileSync(prePushPath, prePushContent, { mode: 0o755 });
    console.log('✅ Pre-push hook 安装成功');
  }

  createConfigFile() {
    const configPath = path.join(this.projectPath, '.git-commit-standard.json');

    if (fs.existsSync(configPath)) {
      console.log('⚠️  配置文件已存在，跳过创建');
      return;
    }

    const defaultConfig = {
      format: "conventional",
      types: ["feat", "fix", "docs", "style", "refactor", "test", "chore", "perf", "ci", "build"],
      scopes: ["auth", "api", "ui", "utils", "config"],
      maxLength: 100,
      requireScope: false,
      requireDescription: true,
      maxLineLength: 72
    };

    fs.writeFileSync(configPath, JSON.stringify(defaultConfig, null, 2), 'utf8');
    console.log('✅ 配置文件创建成功: .git-commit-standard.json');
  }

  installAll() {
    try {
      this.checkGitRepository();

      console.log('🚀 开始安装Git提交规范hooks...\n');

      this.installCommitMsgHook();
      this.installPreCommitHook();
      this.installPrePushHook();
      this.createConfigFile();

      console.log('\n🎉 所有hooks安装完成！');
      console.log('\n📝 使用说明:');
      console.log('  - 所有提交信息将自动验证格式');
      console.log('  - 配置文件: .git-commit-standard.json');
      console.log('  - 手动验证: node git-commit-validator.js "<提交信息>"');
      console.log('  - 交互生成: node git-commit-validator.js --interactive');

    } catch (error) {
      console.error(`❌ 安装失败: ${error.message}`);
      process.exit(1);
    }
  }

  uninstall() {
    try {
      this.checkGitRepository();

      const hooks = ['pre-commit', 'commit-msg', 'pre-push'];
      let removedCount = 0;

      hooks.forEach(hook => {
        const hookPath = path.join(this.hooksDir, hook);
        if (fs.existsSync(hookPath)) {
          const content = fs.readFileSync(hookPath, 'utf8');
          if (content.includes('git-commit-standard')) {
            fs.unlinkSync(hookPath);
            removedCount++;
            console.log(`✅ 已移除 ${hook} hook`);
          }
        }
      });

      if (removedCount === 0) {
        console.log('ℹ️  没有找到相关的hooks文件');
      } else {
        console.log(`\n🗑️  已移除 ${removedCount} 个hooks文件`);
      }

    } catch (error) {
      console.error(`❌ 卸载失败: ${error.message}`);
      process.exit(1);
    }
  }

  status() {
    try {
      this.checkGitRepository();

      console.log('📋 Git Hooks 状态检查:\n');

      const hooks = ['pre-commit', 'commit-msg', 'pre-push'];
      let installedCount = 0;

      hooks.forEach(hook => {
        const hookPath = path.join(this.hooksDir, hook);
        if (fs.existsSync(hookPath)) {
          const content = fs.readFileSync(hookPath, 'utf8');
          if (content.includes('git-commit-standard')) {
            console.log(`✅ ${hook}: 已安装`);
            installedCount++;
          } else {
            console.log(`⚠️  ${hook}: 存在其他hook`);
          }
        } else {
          console.log(`❌ ${hook}: 未安装`);
        }
      });

      // 检查配置文件
      const configPath = path.join(this.projectPath, '.git-commit-standard.json');
      if (fs.existsSync(configPath)) {
        console.log('✅ 配置文件: 已存在');
      } else {
        console.log('❌ 配置文件: 不存在');
      }

      console.log(`\n📊 总体状态: ${installedCount}/${hooks.length} 个hooks已安装`);

    } catch (error) {
      console.error(`❌ 状态检查失败: ${error.message}`);
      process.exit(1);
    }
  }
}

// CLI接口
function main() {
  const args = process.argv.slice(2);
  const installer = new GitHooksInstaller();

  if (args.includes('--help') || args.includes('-h')) {
    console.log(`
Git Hooks 安装工具

用法:
  git-hooks-installer [命令] [选项]

命令:
  install                 安装所有Git hooks (默认)
  uninstall               卸载Git hooks
  status                  检查hooks状态

选项:
  --help, -h              显示帮助信息
  --version               显示版本信息
  --path <路径>           指定项目路径 (默认: 当前目录)

示例:
  git-hooks-installer install
  git-hooks-installer status
  git-hooks-installer uninstall
  git-hooks-installer --path /path/to/project
`);
    process.exit(0);
  }

  if (args.includes('--version')) {
    console.log('Git Hooks Installer v1.0.0');
    process.exit(0);
  }

  const pathIndex = args.indexOf('--path');
  if (pathIndex !== -1 && args[pathIndex + 1]) {
    installer.projectPath = args[pathIndex + 1];
    installer.gitDir = path.join(installer.projectPath, '.git');
    installer.hooksDir = path.join(installer.gitDir, 'hooks');
  }

  const command = args[0] || 'install';

  switch (command) {
    case 'install':
      installer.installAll();
      break;
    case 'uninstall':
      installer.uninstall();
      break;
    case 'status':
      installer.status();
      break;
    default:
      console.error(`未知命令: ${command}`);
      console.log('使用 --help 查看帮助信息');
      process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = GitHooksInstaller;