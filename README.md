# thinkany-2api 🚀

<div align="center">

<img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License">
<img src="https://img.shields.io/badge/Version-1.0.1-brightgreen.svg" alt="Version">
<img src="https://img.shields.io/badge/Docker-Ready-blue.svg?logo=docker" alt="Docker">
<img src="https://img.shields.io/badge/Python-3.10+-yellow.svg?logo=python" alt="Python">
<img src="https://img.shields.io/badge/GitHub-Repo-black.svg?logo=github" alt="GitHub">

**将强大的 ThinkAny.ai 搜索引擎和对话能力，转化为兼容 OpenAI 格式的可部署 API 服务**

<sub>赋能你的应用，让思考无界，让智能随行</sub>

</div>

---

## 🌟 项目宣言

> 在这个信息爆炸的时代，我们相信知识的力量不应被垄断。每一个有创意的灵魂，都应该拥有低成本、高效率的智能引擎来将想法变为现实。`thinkany-2api` 诞生的初衷，就是为了打破壁垒，将顶尖的 AI 搜索与对话能力，以最简单、最开放的方式，交到每一位开发者手中。
>
> 这不仅仅是一个项目，更是一场关于"知识平权"的实践。我们希望，通过开源的力量，点燃更多人的创造火花。当你运行这个项目的瞬间，你不仅是使用者，更是这场变革的参与者。

## ✨ 核心特性

<div align="center">

| 特性 | 描述 | 状态 |
|------|------|------|
| 🤖 OpenAI 格式兼容 | 无缝对接现有生态，无需修改应用代码 | ✅ 已实现 |
| 🔍 双模式切换 | 支持搜索+回答和纯聊天两种模式 | ✅ 已实现 |
| 🔄 多 Cookie 轮询 | 支持多个账号自动轮询，提高稳定性 | ✅ 已实现 |
| 🧠 有状态对话 | 独家实现会话上下文保持 | ✅ 已实现 |
| 📄 结构化输出 | 以 Markdown 格式返回搜索结果和引用来源 | ✅ 已实现 |
| 🐳 Docker 一键部署 | 完整容器化支持，快速启动服务 | ✅ 已实现 |
| 🛡️ API 密钥保护 | 支持设置访问密钥，防止滥用 | ✅ 已实现 |

</div>

## 🏗️ 系统架构

```mermaid
graph TB
    subgraph "客户端"
        A[Web 应用] --> B[API 调用]
        C[移动应用] --> B
        D[命令行工具] --> B
    end

    subgraph "thinkany-2api 服务"
        E[Nginx 网关] --> F[FastAPI 应用]
        F --> G{认证中间件}
        G --> H[路由分发]
        
        subgraph "会话管理"
            I[会话管理器]
            I --> J[内存缓存]
        end
        
        subgraph "服务提供者"
            K[ThinkAny 提供者]
            K --> L[多 Cookie 轮询]
            K --> M[双模式切换]
        end
        
        H --> I
        H --> K
    end

    subgraph "数据流"
        K --> N[ThinkAny.ai API]
        N --> O[数据解析]
        O --> P[SSE 流式响应]
        P --> B
    end

    style E fill:#ffd700
    style F fill:#87ceeb
    style K fill:#98fb98
    style I fill:#ffb6c1
```

## 📁 项目结构

```
thinkany-2api/
├── 🐳 Docker 部署文件
│   ├── Dockerfile              # 应用容器构建配置
│   └── docker-compose.yml      # 服务编排配置
├── 🔧 配置文件
│   ├── .env.example           # 环境变量模板
│   ├── nginx.conf             # Nginx 反向代理配置
│   └── requirements.txt       # Python 依赖列表
├── 🚀 应用入口
│   └── main.py                # FastAPI 应用主文件
└── 📦 核心模块
    └── app/
        ├── core/
        │   └── config.py              # 配置管理中心
        ├── providers/
        │   ├── base_provider.py       # 提供者基类
        │   └── thinkany_provider.py   # ThinkAny 交互核心
        ├── services/
        │   └── session_manager.py     # 会话状态管理
        └── utils/
            └── sse_utils.py           # 流式响应工具
```

## 🎯 适用场景

<div align="center">

| 用户类型 | 使用场景 | 收益 |
|---------|----------|------|
| 👨‍💻 开发者 & 创客 | 集成免费 AI 搜索到自有应用 | 节省 API 费用，快速验证想法 |
| 🎓 学生 & 研究者 | 学术研究、资料查询、论文写作 | 获得专业的研究助手 |
| 🤖 AI 爱好者 | 学习反向工程、API 封装技术 | 深入了解 LLM 工作原理 |
| 💼 初创团队 | 产品原型开发和功能验证 | 低成本试错，快速迭代 |

</div>

## 🚀 快速开始

### 1. 获取项目代码

```bash
# 克隆仓库
git clone https://github.com/lzA6/thinkany-2api.git
cd thinkany-2api
```

### 2. 获取 ThinkAny Cookie

1. 访问 [ThinkAny.ai](https://thinkany.ai) 并登录
2. 打开浏览器开发者工具 (F12)
3. 切换到 Network 标签页
4. 进行一次搜索或对话
5. 找到 `completions` 请求，复制完整的 Cookie 值

<div align="center">

![获取 Cookie 示意图](https://via.placeholder.com/600x300?text=Cookie+获取+演示图)

<sub>*示意图：在开发者工具中复制 Cookie 值*</sub>

</div>

### 3. 配置环境变量

```bash
# 复制配置文件模板
cp .env.example .env
```

编辑 `.env` 文件：

```env
# API 安全配置
API_MASTER_KEY=sk-your-secret-key-123456

# 服务端口配置
NGINX_PORT=8088

# ThinkAny 账号配置（支持多个）
THINKANY_COOKIE_1="你的第一个Cookie字符串"
THINKANY_COOKIE_2="你的第二个Cookie字符串（可选）"
THINKANY_COOKIE_3="你的第三个Cookie字符串（可选）"
```

### 4. 启动服务

```bash
# 使用 Docker Compose 启动服务
docker-compose up -d --build

# 查看服务状态
docker-compose logs -f
```

### 5. 测试 API

**搜索模式测试：**

```bash
curl -X POST http://localhost:8088/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-your-secret-key-123456" \
  -d '{
    "model": "thinkany-search-gpt4o-mini",
    "messages": [{
      "role": "user",
      "content": "最近有什么好玩的AI应用？"
    }],
    "stream": true
  }'
```

**聊天模式测试：**

```bash
curl -X POST http://localhost:8088/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-your-secret-key-123456" \
  -d '{
    "model": "thinkany-chat-haiku",
    "messages": [{
      "role": "user", 
      "content": "你好，我们来玩成语接龙吧，我先来：为所欲为"
    }],
    "stream": true
  }'
```

## 🧩 技术架构详解

### 核心组件说明

<div align="center">

| 组件 | 角色 | 技术选型理由 |
|------|------|-------------|
| 🚪 **Nginx** | API 网关 & 负载均衡 | `ip_hash` 策略保持会话粘性，确保同一用户请求路由到相同后端 |
| ⚡ **FastAPI** | Web 应用框架 | 高性能异步处理，自动生成 API 文档，开发体验优秀 |
| 🕵️ **Cloudscraper** | 反爬虫绕过工具 | 专门应对 Cloudflare 防护，确保服务稳定性 |
| 🐳 **Docker** | 容器化平台 | 环境一致性，简化部署流程，支持快速扩展 |
| 🧠 **SessionManager** | 会话状态管理 | 基于 TTLCache 的内存缓存，实现 AI 的"短期记忆" |
| 📡 **SSE** | 流式数据传输 | 模拟 OpenAI 流式输出，提供实时交互体验 |

</div>

### 数据流示意图

```mermaid
sequenceDiagram
    participant C as Client
    participant N as Nginx
    participant F as FastAPI
    participant S as SessionManager
    participant T as ThinkAny Provider
    participant A as ThinkAny.ai

    C->>N: POST /v1/chat/completions
    N->>F: 转发请求 (ip_hash)
    F->>F: 验证 API Key
    F->>S: 获取会话历史
    S->>F: 返回历史消息
    F->>T: 构建请求载荷
    T->>T: Cookie 轮询选择
    T->>A: 发送聊天请求 (stream=True)
    A-->>T: 流式响应
    T->>F: SSE 数据块处理
    F->>C: 流式返回结果
    T->>S: 更新会话历史
```

## 🔧 高级配置

### 模型映射配置

支持以下模型名称映射：

```python
# 搜索模式（搜索 + 回答）
"thinkany-search-gpt4o-mini"    # 默认搜索模型
"thinkany-search-deepseek"      # DeepSeek 搜索模型

# 聊天模式（纯对话）  
"thinkany-chat-haiku"           # Claude Haiku 模型
"thinkany-chat-sonnet"          # Claude Sonnet 模型
```

### 自定义部署配置

修改 `docker-compose.yml` 调整资源限制：

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
    environment:
      - WORKERS=2
      - MAX_SESSION_AGE=3600
```

## 🗺️ 项目路线图

### ✅ 已实现功能
- [x] OpenAI API 格式兼容
- [x] 搜索/聊天双模式
- [x] 多账号 Cookie 轮询
- [x] 会话状态保持
- [x] Docker 容器化部署
- [x] API 密钥认证

### 🔄 进行中改进
- [ ] Cookie 自动刷新机制
- [ ] Redis 会话存储支持
- [ ] 更完善的错误处理
- [ ] 性能监控和指标收集

### 🎯 未来规划
- [ ] 可视化管理面板
- [ ] 多数据源提供者支持
- [ ] 高级缓存策略
- [ ] 集群部署支持
- [ ] 自动扩缩容机制

## 🐛 常见问题

### Q: Cookie 失效怎么办？
**A:** 目前需要手动更新 `.env` 文件中的 Cookie 值。我们正在开发自动刷新机制。

### Q: 如何查看服务日志？
**A:** 使用以下命令查看实时日志：
```bash
docker-compose logs -f app
```

### Q: 支持并发请求吗？
**A:** 当前版本使用单工作进程，适合中小规模使用。如需高并发，可调整 `docker-compose.yml` 中的 worker 数量。

### Q: 会话数据存储在哪里？
**A:** 默认使用内存缓存，服务重启后数据会丢失。生产环境建议配置 Redis。

## 🤝 参与贡献

我们欢迎各种形式的贡献！

- 🐛 **报告问题**: [提交 Issue](https://github.com/lzA6/thinkany-2api/issues)
- 💡 **功能建议**: 通过 Issue 分享你的想法
- 🔧 **代码贡献**: 提交 Pull Request
- 📖 **文档改进**: 帮助完善文档和示例
- 🐋 **Docker 优化**: 改善容器化部署体验

## 📄 开源协议

本项目采用 **Apache 2.0** 开源协议。

## 🙏 致谢

- 感谢 [ThinkAny.ai](https://thinkany.ai) 提供优秀的 AI 搜索服务
- 感谢所有为开源社区做出贡献的开发者
- 特别感谢使用和反馈本项目的每一位用户

---

<div align="center">

**如果这个项目对你有帮助，请给个 ⭐️ Star 支持我们！**

*让思考无界，让创造更简单* 🚀

</div>
