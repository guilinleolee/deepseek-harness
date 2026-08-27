# JavaScript Code Node 示例 - 数据转换

## 概述

n8n Code 节点使用 JavaScript 处理数据转换、计算和逻辑操作。

## 基础示例

### 1. 数组映射

```javascript
// 将所有字段名转为大写
const items = $input.all();
const newItems = items.map(item => {
  const newItem = {};
  for (const key of Object.keys(item.json)) {
    newItem[key.toUpperCase()] = item.json[key];
  }
  return { json: newItem };
});
return newItems;
```

### 2. 过滤数据

```javascript
// 只保留 status 为 'active' 的项
const items = $input.all();
const filteredItems = items.filter(item => {
  return item.json.status === 'active';
});
return filteredItems.length > 0 ? filteredItems : [{ json: { message: 'No active items found' } }];
```

### 3. 数据聚合

```javascript
// 计算总销售额
const items = $input.all();
const totalSales = items.reduce((sum, item) => {
  return sum + (item.json.amount || 0);
}, 0);

return [{
  json: {
    totalSales: totalSales,
    transactionCount: items.length,
    averageAmount: totalSales / items.length,
    timestamp: new Date().toISOString()
  }
}];
```

### 4. 数据分组

```javascript
// 按类别分组
const items = $input.all();
const grouped = items.reduce((acc, item) => {
  const category = item.json.category || 'uncategorized';
  if (!acc[category]) {
    acc[category] = [];
  }
  acc[category].push(item.json);
  return acc;
}, {});

// 转换为数组格式
const result = Object.entries(grouped).map(([category, items]) => ({
  json: { category, items, count: items.length }
}));

return result;
```

## 高级示例

### 5. 日期处理

```javascript
// 计算两个日期之间的天数
const items = $input.all();
const result = items.map(item => {
  const startDate = new Date(item.json.startDate);
  const endDate = new Date(item.json.endDate);
  const daysDiff = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24));

  return {
    json: {
      ...item.json,
      daysDifference: daysDiff,
      weeksDifference: Math.round(daysDiff / 7 * 10) / 10,
      isOverdue: new Date() > endDate
    }
  };
});

return result;
```

### 6. 字符串操作

```javascript
// 清理和格式化文本
const items = $input.all();
const result = items.map(item => {
  const text = item.json.rawText || '';
  return {
    json: {
      original: text,
      trimmed: text.trim(),
      upperCase: text.toUpperCase(),
      lowerCase: text.toLowerCase(),
      wordCount: text.split(/\s+/).filter(w => w.length > 0).length,
      charCount: text.length,
      slug: text.toLowerCase().replace(/\s+/g, '-').replace(/[^\w-]/g, '')
    }
  };
});

return result;
```

### 7. 嵌套数据展开

```javascript
// 展开嵌套的 JSON 结构
const items = $input.all();
const result = [];

for (const item of items) {
  const userData = item.json;
  if (userData.addresses && Array.isArray(userData.addresses)) {
    for (const address of userData.addresses) {
      result.push({
        json: {
          userId: userData.id,
          name: userData.name,
          street: address.street,
          city: address.city,
          country: address.country,
          isPrimary: address.isPrimary || false
        }
      });
    }
  }
}

return result.length > 0 ? result : [{ json: { message: 'No addresses found' } }];
```

### 8. 条件逻辑

```javascript
// 根据条件设置不同的值
const items = $input.all();
const result = items.map(item => {
  const score = item.json.score || 0;
  let grade, status, message;

  if (score >= 90) {
    grade = 'A';
    status = 'excellent';
    message = 'Outstanding performance!';
  } else if (score >= 80) {
    grade = 'B';
    status = 'good';
    message = 'Good job!';
  } else if (score >= 70) {
    grade = 'C';
    status = 'average';
    message = 'You passed.';
  } else if (score >= 60) {
    grade = 'D';
    status = 'below average';
    message = 'Needs improvement.';
  } else {
    grade = 'F';
    status = 'fail';
    message = 'Please retake the exam.';
  }

  return {
    json: {
      ...item.json,
      grade,
      status,
      message,
      passed: score >= 60,
      curve: Math.min(100, score + 5) // Add 5 points curve, max 100
    }
  };
});

return result;
```

### 9. 数据验证

```javascript
// 验证邮箱地址格式
const items = $input.all();
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const result = items.map(item => {
  const email = item.json.email || '';
  const isValid = emailRegex.test(email);
  const [localPart, domain] = email.split('@');

  return {
    json: {
      ...item.json,
      email,
      isValid,
      localPart: localPart || '',
      domain: domain || '',
      error: isValid ? null : 'Invalid email format'
    }
  };
});

// 可以选择只返回有效或无效的邮箱
// const validEmails = result.filter(item => item.json.isValid);
// return validEmails;

return result;
```

### 10. HTTP 请求处理

```javascript
// 处理 API 响应并提取数据
const response = $input.first().json;

// 假设 API 返回 { data: { users: [...] } }
const rawUsers = response.data?.users || [];

const processedUsers = rawUsers.map(user => ({
  json: {
    id: user.id,
    fullName: `${user.firstName} ${user.lastName}`.trim(),
    email: user.email?.toLowerCase() || '',
    age: user.age || 0,
    isAdult: (user.age || 0) >= 18,
    registeredAt: user.createdAt ? new Date(user.createdAt).toISOString() : null,
    tags: user.tags?.join(', ') || ''
  }
}));

return processedUsers;
```

## 实用工具函数

### 生成唯一 ID

```javascript
function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

const items = $input.all();
return items.map(item => ({
  json: {
    ...item.json,
    id: item.json.id || generateId()
  }
}));
```

### 深度克隆对象

```javascript
function deepClone(obj) {
  return JSON.parse(JSON.stringify(obj));
}

const items = $input.all();
return items.map(item => ({
  json: {
    original: item.json,
    copy: deepClone(item.json)
  }
}));
```

### 延迟执行

```javascript
// 在循环中添加延迟（谨慎使用）
async function processWithDelay(items, delayMs) {
  const result = [];

  for (const item of items) {
    // 处理 item
    result.push({ json: { ...item.json, processed: true } });

    // 延迟
    await new Promise(resolve => setTimeout(resolve, delayMs));
  }

  return result;
}

const items = $input.all();
return await processWithDelay(items, 1000); // 1秒延迟
```

## 错误处理

### Try-Catch 模式

```javascript
const items = $input.all();
const result = [];

for (const item of items) {
  try {
    // 尝试处理数据
    const processed = {
      json: {
        ...item.json,
        calculated: item.json.value * 2,
        timestamp: new Date().toISOString()
      }
    };
    result.push(processed);
  } catch (error) {
    // 记录错误但继续处理
    result.push({
      json: {
        ...item.json,
        error: error.message,
        failed: true
      }
    });
  }
}

return result;
```

## 性能优化

### 批量处理大数据集

```javascript
// 对于大数据集，分批处理
function chunk(array, size) {
  const chunks = [];
  for (let i = 0; i < array.length; i += size) {
    chunks.push(array.slice(i, i + size));
  }
  return chunks;
}

const items = $input.all();
const batchSize = 100;
const chunks = chunk(items, batchSize);

// 处理第一批
const firstBatch = chunks[0].map(item => ({
  json: {
    ...item.json,
    batchNumber: 1
  }
}));

return firstBatch;
```

## 相关文档

- [Python Code Node 示例](../python/python-examples.md)
- [Code Node 最佳实践](../code-best-practices.md)
- [表达式语法](../../specs/expression-syntax.md)
