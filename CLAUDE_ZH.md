# n8n-workflows 仓库

## 概述

n8n 自动化工作流仓库，拥有 4343+ 工作流、FastAPI 搜索 API 和 GitHub Pages 文档。

## 技术栈

- **后端**: Python FastAPI + SQLite FTS5（全文搜索）
- **前端**: 原生 HTML + CSS + JS（无框架）
- **基础设施**: Docker + Kubernetes + Helm
- **AI 栈**: n8n + Agent Zero + ComfyUI（在 `ai-stack/` 中）
- **发布**: GitHub Pages（`docs/`）

## 仓库结构

```
n8n-workflows/
├── .claude/agents/          # Claude 子代理（自动检测）
├── api_server.py            # 主 REST API（FastAPI）
├── run.py                   # 服务器入口
├── workflow_db.py           # SQLite 数据访问层
├── src/                     # Python 模块（AI、分析、社区、用户）
├── static/                  # 工作流搜索 SPA（原生 HTML）
├── workflows/               # 4343+ 按集成分类的 n8n JSON
├── context/                 # 分类和搜索索引数据
├── docs/                    # GitHub Pages + API 文档
├── k8s/                     # Kubernetes 清单
├── helm/                    # Helm chart
├── ai-stack/                # 本地 AI 栈（n8n + Agent Zero + ComfyUI）
├── scripts/                 # 部署、备份、健康检查、索引
├── templates/               # 可重用工作流模板
├── Dockerfile               # 生产镜像
├── docker-compose*.yml      # Docker 环境（基础、开发、生产）
└── test_*.sh / test_*.py    # API 和安全测试
```

## 项目 URL

| 环境 | URL |
|------|-----|
| 本地 API | `http://localhost:8000` |
| GitHub Pages | `https://zie619.github.io/n8n-workflows` |
| AI 栈（n8n） | `http://localhost:5678` |
| AI 栈（Agent Zero） | `http://localhost:50080` |

## n8n 工作流格式

`workflows/` 中的每个 JSON 包含：`name`、`nodes`（操作数组）、`connections`（节点间流程）、`settings`、`tags`、`createdAt/updatedAt`。

### 常见节点类型
- **触发器**: webhook、cron、manual
- **集成**: HTTP Request、数据库连接器、API
- **逻辑**: IF、Switch、Merge、Loop
- **数据**: Function、Set、Transform Data
- **通信**: Email、Slack、Discord

### 常见模式
- **数据管道**: 触发 → 获取 → 转换 → 存储/发送
- **集成同步**: 定时任务 → API 调用 → 比较 → 更新
- **自动化**: Webhook → 处理 → 条件判断 → 操作
- **监控**: 定时 → 检查状态 → 告警

## 安全性

- 速率限制：每 IP 每分钟 60 次请求（内存存储）
- 路径遍历防护：`validate_filename()` 三重 URL 解码
- CORS 限制特定来源
- JWT HS256 + bcrypt 密码哈希
- Docker：非 root 用户 `appuser`（UID 1001）
- 工作流凭证存储在 n8n 中，不在 JSON 文件中

# 子专业代理

本项目使用 **Claude 子代理**，位于 `.claude/agents/`。每个代理有明确的职责域。

## 代理结构

```
.claude/agents/
├── main-assistant.md   # 主编排器 — 所有任务的入口点
├── backend-api.md      # FastAPI API、Python、端点、中间件
├── database.md         # SQLite、FTS5、模式、迁移
├── frontend.md         # HTML/CSS/JS、GitHub Pages、静态 UI
├── ai-ml.md            # AI 对话、分析、ai-stack
├── security.md         # JWT 认证、速率限制、CVE、安全加固
├── devops.md           # Docker、Kubernetes、Helm、CI/CD、脚本
├── community.md        # 评分、评论、用户管理
├── workflows.md        # n8n JSON 集合、分类、索引
├── n8n-sync.md         # n8n ↔ 本地 JSON 文件双向同步（REST API）
└── git-commit.md       # 交互式提交，用户验证
```

**系统技术文档**: `docs/design/system-overview.md`

## 代理工作方式

- **main-assistant** 是编排器：分析请求，选择专家，自主执行直到完成任务。
- 代理**不会在每一步阻塞流程**请求确认 — 执行完毕后汇报。
- 仅在破坏性和不可逆操作前请求明确确认。

## AI 助手有用上下文

协助本仓库时：

1. **工作流分析**: 通过检查节点流程了解业务目的，不仅仅是单个节点。
2. **文档生成**: 描述工作流完成的功能，不仅仅是包含哪些节点。
3. **故障排除**: 常见问题：节点连接错误、缺少错误处理、循环低效、硬编码值。
4. **优化建议**: 识别冗余操作、建议批处理、推荐错误处理、拆分复杂工作流。
5. **代码生成**: 处理各种 n8n 格式版本、自定义节点、参数表达式、执行顺序。

# 仓库特定信息

- **技术栈**: Python FastAPI + SQLite FTS5 + 原生 HTML + Docker
- **工作流**: 4343+ n8n JSON 按集成分类在 `workflows/`
- **本地 API URL**: `http://localhost:8000`
- **GitHub Pages**: `https://zie619.github.io/n8n-workflows`

# 版本兼容性

- n8n 版本：兼容 n8n v1.x
- 最后更新：2026-02-21

[English](./CLAUDE.md)
