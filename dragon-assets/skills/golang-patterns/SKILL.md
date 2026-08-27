---
license: UNKNOWN
name: golang-patterns
description: Idiomatic Go patterns, best practices, and conventions for building robust, efficient, and maintainable Go applications.
github_repo: affaan-m/everything-claude-code
github_hash: 4e66b2882da9afb9747468b08a253ca2f09c85f3
last_updated: 2026-04-25
source_type: derived
origin: ECC (everything-claude-code)
triggers: ["golang patterns", "Go Development Patterns — Go开发模式"]
---

# Go Development Patterns — Go开发模式

> 来源: [affaan-m/everything-claude-code/skills/golang-patterns](https://github.com/affaan-m/everything-claude-code)

## 功能概述

惯用Go模式与最佳实践，构建健壮、高效、可维护的Go应用程序。

## 何时使用

- 编写新Go代码
- 审查Go代码
- 重构现有Go代码
- 设计Go包/模块

## 核心原则

### 1. 简洁与清晰

Go崇尚简洁而非技巧。代码应该明显且易于阅读。

```go
// ✅ Good: 清晰直接
func GetUser(id string) (*User, error) {
    user, err := db.FindUser(id)
    if err != nil {
        return nil, fmt.Errorf("get user %s: %w", id, err)
    }
    return user, nil
}

// ❌ Bad: 过度技巧
func GetUser(id string) (*User, error) {
    return func() (*User, error) {
        if u, e := db.FindUser(id); e == nil {
            return u, nil
        } else {
            return nil, e
        }
    }()
}
```

### 2. 让零值有用

设计类型使其零值无需初始化即可直接使用。

```go
// ✅ Good: 零值有用
type Counter struct {
    mu    sync.Mutex
    count int // 零值是0，可直接使用
}

func (c *Counter) Inc() {
    c.mu.Lock()
    c.count++
    c.mu.Unlock()
}

// ✅ Good: bytes.Buffer零值即可用
var buf bytes.Buffer
buf.WriteString("hello")

// ❌ Bad: 需要初始化
type BadCounter struct {
    counts map[string]int // nil map会panic
}
```

### 3. 接受接口，返回结构体

函数应接受接口参数，返回具体类型。

```go
// ✅ Good: 接受接口，返回具体类型
func ProcessData(r io.Reader) (*Result, error) {
    data, err := io.ReadAll(r)
    if err != nil {
        return nil, err
    }
    return &Result{Data: data}, nil
}
```

## 错误处理模式

### 错误包装与上下文

```go
// ✅ Good: 用上下文包装错误
func LoadConfig(path string) (*Config, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, fmt.Errorf("load config %s: %w", path, err)
    }

    var cfg Config
    if err := json.Unmarshal(data, &cfg); err != nil {
        return nil, fmt.Errorf("parse config %s: %w", path, err)
    }

    return &cfg, nil
}
```

### 自定义错误类型

```go
// 定义领域特定错误
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation failed on %s: %s", e.Field, e.Message)
}

// 哨兵错误
var (
    ErrNotFound     = errors.New("resource not found")
    ErrUnauthorized = errors.New("unauthorized")
    ErrInvalidInput = errors.New("invalid input")
)
```

### 使用errors.Is和errors.As检查

```go
func HandleError(err error) {
    // 检查特定错误
    if errors.Is(err, sql.ErrNoRows) {
        log.Println("No records found")
        return
    }

    // 检查错误类型
    var validationErr *ValidationError
    if errors.As(err, &validationErr) {
        log.Printf("Validation error on field %s: %s",
            validationErr.Field, validationErr.Message)
        return
    }
}
```

## 并发模式

### Worker Pool

```go
func WorkerPool(jobs <-chan Job, results chan<- Result, numWorkers int) {
    var wg sync.WaitGroup

    for i := 0; i < numWorkers; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for job := range jobs {
                results <- process(job)
            }
        }()
    }

    wg.Wait()
    close(results)
}
```

### Context取消与超时

```go
func FetchWithTimeout(ctx context.Context, url string) ([]byte, error) {
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()

    req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
    if err != nil {
        return nil, fmt.Errorf("create request: %w", err)
    }

    resp, err := http.DefaultClient.Do(req)
    if err != nil {
        return nil, fmt.Errorf("fetch %s: %w", url, err)
    }
    defer resp.Body.Close()

    return io.ReadAll(resp.Body)
}
```

### errgroup协同goroutine

```go
import "golang.org/x/sync/errgroup"

func FetchAll(ctx context.Context, urls []string) ([][]byte, error) {
    g, ctx := errgroup.WithContext(ctx)
    results := make([][]byte, len(urls))

    for i, url := range urls {
        i, url := i, url // 捕获循环变量
        g.Go(func() error {
            data, err := FetchWithTimeout(ctx, url)
            if err != nil {
                return err
            }
            results[i] = data
            return nil
        })
    }

    if err := g.Wait(); err != nil {
        return nil, err
    }
    return results, nil
}
```

## 接口设计

### 小而专注

```go
// ✅ Good: 单方法接口
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

type Closer interface {
    Close() error
}
```

### 在消费方定义接口

```go
// 在消费包中定义，而非提供者
package service

// UserStore定义此服务需要什么
type UserStore interface {
    GetUser(id string) (*User, error)
    SaveUser(user *User) error
}

type Service struct {
    store UserStore
}
```

## 包组织

### 标准项目布局

```
myproject/
├── cmd/
│   └── myapp/
│       └── main.go           # 入口点
├── internal/
│   ├── handler/              # HTTP处理器
│   ├── service/              # 业务逻辑
│   ├── repository/           # 数据访问
│   └── config/               # 配置
├── pkg/
│   └── client/               # 公共API客户端
├── api/
│   └── v1/                   # API定义
├── testdata/                 # 测试fixtures
├── go.mod
├── go.sum
└── Makefile
```

### 函数式选项模式

```go
type Server struct {
    addr    string
    timeout time.Duration
    logger  *log.Logger
}

type Option func(*Server)

func WithTimeout(d time.Duration) Option {
    return func(s *Server) {
        s.timeout = d
    }
}

func NewServer(addr string, opts ...Option) *Server {
    s := &Server{
        addr:    addr,
        timeout: 30 * time.Second, // 默认值
        logger:  log.Default(),    // 默认值
    }
    for _, opt := range opts {
        opt(s)
    }
    return s
}
```

## 内存与性能

### 预分配切片

```go
// ✅ Good: 预分配减少分配
func processItems(items []Item) []Result {
    results := make([]Result, 0, len(items))
    for _, item := range items {
        results = append(results, process(item))
    }
    return results
}
```

### 避免循环中字符串拼接

```go
// ✅ Good: 单次分配strings.Builder
func join(parts []string) string {
    var sb strings.Builder
    for i, p := range parts {
        if i > 0 {
            sb.WriteString(",")
        }
        sb.WriteString(p)
    }
    return sb.String()
}
```

## Go工具链集成

### 必需命令

```bash
# 构建和运行
go build ./...
go run ./cmd/myapp

# 测试
go test ./...
go test -race ./...
go test -cover ./...

# 静态分析
go vet ./...
golangci-lint run

# 模块管理
go mod tidy
go mod verify
```

## 惯用语速查

| 惯用语 | 说明 |
|--------|------|
| 接受接口，返回结构体 | 函数接受接口参数，返回具体类型 |
| 错误是值 | 将错误作为一等公民处理 |
| 不要通过共享内存通信 | goroutine间用channel协调 |
| 让零值有用 | 类型无需显式初始化即可使用 |
| 简洁优于技巧 | 优先可读性而非技巧性 |
| gofmt是每个人的朋友 | 总是用gofmt/goimports格式化 |

## 天龙引擎集成

### 适用岗位

| 岗位 | 集成方式 | 增强能力 |
|------|---------|---------|
| **03构建师** | Go代码实现 | 惯用模式 + 错误处理 + 并发 |
| **06审查师** | Go代码审查 | 内存泄漏检测 + 接口设计 |
| **10-03算法工程师** | 高性能Go | 性能优化 + 内存分配 |

### 天龙引擎增强

```
┌─────────────────────────────────────────────────────────────┐
│ 天龙引擎 Go开发体系                                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Go开发流程:                                               │
│   ├── 03构建师 → 惯用模式 + 函数式选项                     │
│   ├── 04验证师 → 并发测试 + 竞态检测                      │
│   └── 06审查师 → 内存泄漏 + 接口设计                      │
│                                                             │
│   协同技能:                                                 │
│   ├── /api-design         → REST API Go实现               │
│   ├── /database-migrations → Go数据库迁移                  │
│   └── /deployment-patterns → Go应用容器化                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 核心命令

```bash
# Go开发
[@构建师] 使用golang-patterns实现这个API处理器
[@构建师] 添加errgroup并发处理

# 代码审查
[@审查师] 检查goroutine泄漏
[@审查师] 审查接口设计

# 性能
[@算法工程师] 优化这个Go服务的内存分配
```

---

**版本**: V1.0 | **兼容性**: 天龙引擎 V8.68+ | **来源**: ECC
