# Gemini Docs MCP

一个使用 Gemini 作为 RAG 的 MCP 服务器，用于文档查询。

## 安装

```bash
uv sync
```

## 配置

1. 复制环境变量配置：
```bash
cp .env.example .env
```

2. 编辑 `.env`，填入你的 OpenRouter API Key：
```
OPENROUTER_API_KEY=your_api_key_here
```

## 使用

### 1. 上传文档

```bash
uv run python scripts/upload_doc.py \
  --id "tauri2.0/llms.txt" \
  --name "tauri2.0_docs" \
  --file ~/llms-full.txt \
  --description "tauri2.0 document"
```

### 2. 运行 MCP 服务器

```bash
uv run python main.py
```

## Claude Code 配置

在 `~/.claude/claude_desktop_config.json` 中添加：

```json
{
  "mcpServers": {
    "gemini-docs": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/root/gemini_docs_mcp",
        "python",
        "main.py"
      ]
    },
  }
}
```

> 注：API Key 已在 `.env` 文件中配置，无需在此重复设置。

## MCP 工具

### get_all_resources

获取所有可用文档列表。

**参数**：无

**返回**：文档列表（id, name, description）

### get_docs_info

根据文档 ID 和提示词查询文档内容。

**参数**：
- `doc_id`: 文档 ID（如 `langchain/llms.txt`）
- `prompt`: 查询提示词

**返回**：Gemini 基于文档内容的回答

## 项目结构

```
gemini_docs_mcp/
├── main.py                   # MCP Server 入口
├── src/
│   └── gemini_docs_mcp/
│       ├── server.py         # MCP Server 核心
│       ├── agent.py          # CrewAI + OpenRouter
│       └── docs.py           # 文档管理
├── scripts/
│   └── upload_doc.py         # CLI 上传命令
└── docs/                     # 文档存储
    ├── index.json            # 文档索引
    └── *.txt                 # 文档文件
```

# test

```bash
cat << 'EOF' | uv run --directory /root/gemini_docs_mcp python main.py
{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}}
{"jsonrpc": "2.0", "method": "notifications/initialized"}
{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "get_all_resources", "arguments": {}}}
EOF
```

```bash
$ cat << 'EOF' | uv run --directory /root/gemini_docs_mcp python main.py 2>/dev/null
{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}}
{"jsonrpc": "2.0", "method": "notifications/initialized"}
{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "get_all_resources", "arguments": {}}}
{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "get_docs_info", "arguments": {"doc_id": "tauri2.0/llms.txt", "prompt": "Tauri 2.0 的安全特性有哪些？简单列出要点"}}}
EOF
```