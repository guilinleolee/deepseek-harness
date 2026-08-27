# Remotion AWS Lambda 云渲染配置指南

## 🎯 核心价值

| 维度 | 本地渲染 | Lambda 云渲染 |
|------|---------|--------------|
| **并行能力** | 单机 | 1000 Lambda 并行 |
| **渲染速度** | 实时 | **视频时长/并发数** |
| **成本** | 固定硬件 | 按渲染时间付费 |
| **视频长度** | 无限制 | Full HD 最长 80 分钟 |
| **适用场景** | 开发预览 | 批量生产、商业渲染 |

---

## 📋 前置要求

### 1. AWS 账户

```yaml
必需:
  - AWS 账户（已验证）
  - AWS CLI 安装
  - IAM 权限（Lambda、S3、IAM）

推荐配置:
  - 区域: us-east-1 或 eu-west-1
  - 预算: 设置 AWS Budget 预警
```

### 2. 本地环境

```bash
# 检查 Node.js 版本（需要 18+）
node --version

# 检查 AWS CLI
aws --version

# 安装 Remotion Lambda
npm install @remotion/lambda
```

---

## 🚀 配置步骤

### Step 1: 配置 AWS 凭证

```bash
# 方式1：AWS CLI 配置
aws configure
# 输入:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region (如 us-east-1)
# - Default output format (json)

# 方式2：环境变量
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1

# 验证配置
aws sts get-caller-identity
```

### Step 2: 创建 IAM 用户和策略

```bash
# 创建 IAM 策略文件
cat > remotion-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:*",
        "lambda:*",
        "iam:CreateRole",
        "iam:DeleteRole",
        "iam:GetRole",
        "iam:PassRole",
        "iam:CreateInstanceProfile",
        "iam:DeleteInstanceProfile",
        "iam:AddRoleToInstanceProfile",
        "iam:RemoveRoleFromInstanceProfile",
        "iam:AttachRolePolicy",
        "iam:DetachRolePolicy",
        "iam:PutRolePolicy",
        "iam:DeleteRolePolicy",
        "iam:GetRolePolicy",
        "logs:*"
      ],
      "Resource": "*"
    }
  ]
}
EOF

# 创建 IAM 用户（可选）
aws iam create-user --user-name remotion-renderer

# 附加策略
aws iam attach-user-policy \
  --user-name remotion-renderer \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
```

### Step 3: 部署 Lambda 函数

```bash
# 查看可用区域
npx remotion lambda regions

# 部署 Lambda 函数（首次需要 5-10 分钟）
npx remotion lambda deploy

# 输出示例:
# Created function "remotion-render-3-3-82" in region "us-east-1"
# Created bucket "remotion-render-abc123"
```

### Step 4: 验证部署

```bash
# 检查 Lambda 函数
npx remotion lambda functions

# 检查 S3 存储桶
npx remotion lambda buckets

# 测试渲染
npx remotion lambda render test out/test.mp4
```

---

## 📊 渲染命令

### 基础渲染

```bash
# 渲染视频
npx remotion lambda render <composition-id> out/video.mp4

# 指定区域
npx remotion lambda render <composition-id> out/video.mp4 --region us-east-1

# 指定参数
npx remotion lambda render <composition-id> out/video.mp4 \
  --props '{"title":"产品介绍","logo":"logo.png"}'

# 指定帧范围（渲染部分）
npx remotion lambda render <composition-id> out/video.mp4 \
  --frame 0-100
```

### 并行渲染

```bash
# 设置并发数（默认 100）
npx remotion lambda render <composition-id> out/video.mp4 \
  --max-bucket-size 1000

# 批量渲染
for i in {1..10}; do
  npx remotion lambda render <composition-id> out/video-$i.mp4 \
    --props "{\"id\":$i}" &
done
wait
```

### 渲染监控

```bash
# 查看渲染进度
npx remotion lambda render <composition-id> out/video.mp4 \
  --log progress

# 查看渲染日志
aws logs tail /aws/lambda/remotion-render-*

# 查看 CloudWatch 指标
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=remotion-render-* \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 300 \
  --statistics Average
```

---

## 💰 成本估算

### 渲染成本（Full HD 30fps）

| 视频时长 | Lambda 成本 | S3 存储成本 | 总成本 |
|---------|------------|------------|--------|
| 1分钟 | ~$0.05 | ~$0.01 | **~$0.06** |
| 5分钟 | ~$0.25 | ~$0.02 | **~$0.27** |
| 10分钟 | ~$0.50 | ~$0.03 | **~$0.53** |
| 30分钟 | ~$1.50 | ~$0.05 | **~$1.55** |
| 60分钟 | ~$3.00 | ~$0.08 | **~$3.08** |

### 并行渲染收益

```yaml
100 Lambda 并行:
  1分钟视频: ~1秒完成
  5分钟视频: ~5秒完成

1000 Lambda 并行:
  1分钟视频: ~0.1秒完成
  5分钟视频: ~0.5秒完成

成本影响: 并行不增加成本（总帧数相同）
```

### 成本优化建议

```yaml
节省策略:
  - 使用 Reserved Concurrency（预留并发）
  - 设置 S3 生命周期策略（自动删除旧文件）
  - 使用 Spot 实例（如果可用）
  - 批量渲染时共享 Lambda 函数

成本预警:
  - 设置 AWS Budget 预警
  - 监控 Lambda 执行时间
  - 定期清理 S3 存储桶
```

---

## ⚙️ 高级配置

### 1. 自定义 Lambda 配置

```bash
# 设置内存（默认 2048MB）
npx remotion lambda deploy \
  --memory 4096

# 设置超时（默认 120秒）
npx remotion lambda deploy \
  --timeout 300

# 设置并发限制
npx remotion lambda deploy \
  --max-concurrency 1000
```

### 2. S3 存储配置

```yaml
# 生命周期策略（自动清理）
{
  "Rules": [
    {
      "ID": "DeleteOldRenders",
      "Status": "Enabled",
      "Expiration": {
        "Days": 7
      }
    }
  ]
}

# 应用策略
aws s3api put-bucket-lifecycle-configuration \
  --bucket remotion-render-* \
  --lifecycle-configuration file://lifecycle.json
```

### 3. 参数化视频渲染

```bash
# 批量渲染不同参数的视频
npx remotion lambda render ProductDemo out/product-a.mp4 \
  --props '{"product":"A","price":99}'

npx remotion lambda render ProductDemo out/product-b.mp4 \
  --props '{"product":"B","price":149}'

# 使用脚本批量渲染
cat products.json | jq -c '.[]' | while read product; do
  npx remotion lambda render ProductDemo "out/$(echo $product | jq -r '.name').mp4" \
    --props "$product"
done
```

---

## 🛠️ 故障排除

### 常见问题

#### 1. 权限错误

```bash
# 错误信息
# User is not authorized to perform: lambda:InvokeFunction

# 解决方案
aws iam attach-user-policy \
  --user-name remotion-renderer \
  --policy-arn arn:aws:iam::aws:policy/AWSLambdaFullAccess
```

#### 2. 内存不足

```bash
# 错误信息
# Runtime exited without providing a reason

# 解决方案：增加内存
npx remotion lambda deploy --memory 4096
```

#### 3. 超时错误

```bash
# 错误信息
# Task timed out after 120.00 seconds

# 解决方案：增加超时时间
npx remotion lambda deploy --timeout 300

# 或减少并行数
npx remotion lambda render <id> out/video.mp4 \
  --max-bucket-size 50
```

#### 4. 视频过长

```bash
# 错误信息
# Video is too long for Lambda rendering

# 解决方案
# Full HD 最长 80 分钟，4K 最长 20 分钟
# 超长视频需要分段渲染后合并
```

---

## 📊 监控与日志

### CloudWatch 监控

```bash
# 查看 Lambda 执行指标
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=remotion-render-* \
  --start-time $(date -u -d '1 day ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 3600 \
  --statistics Sum

# 查看错误率
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=remotion-render-* \
  --start-time $(date -u -d '1 day ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 3600 \
  --statistics Sum
```

### 日志分析

```bash
# 查看最近日志
aws logs tail /aws/lambda/remotion-render-* --since 1h

# 搜索错误日志
aws logs filter-log-events \
  --log-group-name /aws/lambda/remotion-render-* \
  --filter-pattern "ERROR"
```

---

## 🔐 安全最佳实践

### IAM 最小权限

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::remotion-render-*",
        "arn:aws:s3:::remotion-render-*/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "lambda:InvokeFunction"
      ],
      "Resource": "arn:aws:lambda:*:*:function:remotion-render-*"
    }
  ]
}
```

### 数据安全

```yaml
敏感数据处理:
  - 不在 Props 中传递敏感信息
  - 使用环境变量存储密钥
  - 启用 S3 加密
  - 定期轮换访问密钥

网络安全:
  - 使用 VPC 端点访问 S3
  - 限制 Lambda 网络访问
  - 启用 CloudTrail 审计
```

---

## 📚 相关资源

### 官方文档
- [Remotion Lambda 文档](https://remotion.dev/docs/lambda)
- [AWS Lambda 定价](https://aws.amazon.com/lambda/pricing/)
- [AWS S3 定价](https://aws.amazon.com/s3/pricing/)

### 技能文件
- [skills/remotion-best-practices/SKILL.md](./SKILL.md)
- [skills/remotion-best-practices/rules/animations.md](./rules/animations.md)

### 相关岗位
- [agents/35-05-video-director.md](../../agents/35-05-video-director.md) - 短视频编导
- [agents/35-02-social-media-v10.md](../../agents/35-02-social-media-v10.md) - 社媒运营
- [agents/13-01-designer-v10.md](../../agents/13-01-designer-v10.md) - 设计师

---

**版本**: v1.0
**最后更新**: 2026-03-13
**作者**: 天龙引擎团队