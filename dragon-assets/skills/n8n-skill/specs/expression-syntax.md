# n8n 表达式语法规范

## 基本语法

### 表达式格式

n8n 表达式使用双花括号包裹：

```javascript
// 基本格式
{{ 表达式 }}

// 示例
{{ $json.name }}
{{ $node["HTTP Request"].json.data[0].id }}
```

### 数据访问

#### 访问当前节点数据

```javascript
// 访问 JSON 数据
{{ $json.fieldName }}

// 嵌套字段
{{ $json.data.user.name }}

// 数组元素
{{ $json.items[0].name }}
```

#### 访问其他节点数据

```javascript
// 访问指定节点的输出
{{ $node["节点名称"].json.fieldName }}

// 示例：访问 HTTP Request 节点的响应
{{ $node["HTTP Request"].json.data.id }}
```

#### 安全访问（推荐）

```javascript
// 使用可选链避免错误
{{ $json.data?.user?.name }}
{{ $node["HTTP Request"].json?.data?.[0]?.id }}

// 使用默认值
{{ $json.data?.user?.name || 'Unknown' }}
```

## 表达式类型

### 字符串表达式

```javascript
// 字符串拼接
{{ $json.firstName + ' ' + $json.lastName }}

// 模板字符串（n8n 不支持，使用拼接）
{{ 'Hello, ' + $json.name + '!' }}
```

### 数学表达式

```javascript
// 基本运算
{{ $json.price * 1.1 }}  // 价格加10%
{{ $json.quantity + 1 }}  // 数量加1

// 复杂运算
{{ ($json.price * $json.quantity) * (1 - $json.discount) }}

// 取整
{{ Math.floor($json.price) }}
{{ Math.ceil($json.price) }}
{{ Math.round($json.price) }}
```

### 布尔表达式

```javascript
// 比较
{{ $json.age > 18 }}
{{ $json.status === 'active' }}

// 逻辑运算
{{ $json.isActive && $json.hasPermission }}
{{ $json.type === 'A' || $json.type === 'B' }}
{{ ! $json.isDeleted }}

// 包含检查
{{ $json.tags.includes('important') }}
```

### 条件表达式

```javascript
// 三元运算符
{{ $json.age >= 18 ? 'adult' : 'minor' }}

// 嵌套三元
{{ $json.type === 'A' ? 'Type A' : $json.type === 'B' ? 'Type B' : 'Other' }}
```

### 数组表达式

```javascript
// 数组长度
{{ $json.items.length }}

// 数组第一个/最后一个
{{ $json.items[0] }}
{{ $json.items[$json.items.length - 1] }}

// 数组方法
{{ $json.items.join(', ') }}
{{ $json.items.map(item => item.name).join(', ') }}
```

## 内置函数

### 字符串函数

```javascript
// 大小写转换
{{ $json.text.toUpperCase() }}
{{ $json.text.toLowerCase() }}

// 字符串截取
{{ $json.text.substring(0, 10) }}
{{ $json.text.slice(0, 10) }}

// 去除空格
{{ $json.text.trim() }}

// 替换
{{ $json.text.replace('old', 'new') }}

// 分割
{{ $json.text.split(',') }}
```

### 数组函数

```javascript
// 数组方法
{{ $json.items.filter(item => item.active) }}
{{ $json.items.map(item => item.name) }}
{{ $json.items.find(item => item.id === 123) }}
{{ $json.items.reduce((sum, item) => sum + item.value, 0) }}

// 检查包含
{{ $json.items.some(item => item.active) }}
{{ $json.items.every(item => item.active) }}
```

### 对象函数

```javascript
// 获取键
{{ Object.keys($json.data) }}

// 获取值
{{ Object.values($json.data) }}

// 获取条目
{{ Object.entries($json.data) }}
```

### 时间函数

```javascript
// 当前时间
{{ $now }}
{{ new Date() }}

// 时间格式化
{{ new Date($json.timestamp).toLocaleString() }}
{{ new Date($json.timestamp).toISOString() }}

// 时间计算
{{ new Date($now + 86400000) }}  // 明天
```

## 高级用法

### 过滤节点 (Filter)

```javascript
// 在 Filter 节点中使用表达式
// 条件1: 字符串相等
{{ $json.status === "active" }}

// 条件2: 数字比较
{{ $json.age > 18 }}

// 条件3: 包含检查
{{ $json.tags.includes("important") }}

// 条件4: 布尔值
{{ $json.isActive }}
```

### Switch 节点

```javascript
// 使用表达式进行路由
{{ $json.type }}  // 基于类型路由
{{ $json.priority }}  // 基于优先级路由
```

### IF 节点

```javascript
// IF 节点条件表达式
{{ $json.amount > 1000 }}

// 多条件
{{ $json.type === 'A' && $json.active === true }}
```

### Set 节点

```javascript
// 设置字段值
字段名: {{ $json.originalField }}
字段名: {{ $json.firstName + ' ' + $json.lastName }}
字段名: {{ $json.price * 1.1 }}
```

## 常见错误

### 1. 嵌套表达式

```javascript
// ❌ 错误：嵌套表达式
{{ {{ $json.field }} }}

// ✅ 正确：直接引用
{{ $json.field }}
```

### 2. 引号冲突

```javascript
// ❌ 错误：单引号嵌套单引号
{{ $json.name + 'user's name' }}

// ✅ 正确：使用双引号或转义
{{ $json.name + "user's name" }}
{{ $json.name + 'user\'s name' }}
```

### 3. 未定义值

```javascript
// ❌ 错误：访问未定义字段会报错
{{ $json.data.user.name }}  // 如果 data 不存在会报错

// ✅ 正确：使用可选链
{{ $json.data?.user?.name }}
{{ $json.data?.user?.name || 'Unknown' }}
```

### 4. 节点引用错误

```javascript
// ❌ 错误：使用不存在的节点
{{ $node["Non-existent"].json.field }}

// ✅ 正确：使用 $json 引用当前节点
{{ $json.field }}
```

## 性能建议

1. **优先使用 $json**：访问当前节点数据更快
2. **避免复杂计算**：复杂逻辑使用 Code 节点
3. **缓存结果**：重复使用时考虑中间变量
4. **使用可选链**：避免运行时错误

## 调试技巧

### 在 Code 节点中调试

```javascript
// 在 Code 节点中查看表达式结果
const value = $json.field;
console.log('Value:', value);
return [{ json: { debug: value } }];
```

### 使用 Set 节点调试

```javascript
// 创建调试字段
debug_userName: {{ $json.user?.name }}
debug_itemCount: {{ $json.items?.length }}
```

## 相关文档

- [节点配置规范](node-configuration.md)
- [最佳实践](best-practices.md)
- [表达式官方文档](https://docs.n8n.io/code-examples/expressions/)
