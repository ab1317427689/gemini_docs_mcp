# Gemini Docs MCP

基于 Gemini 的文档 RAG MCP 服务器，包含管理后台。

## 快速开始

1. **安装依赖**:
   ```bash
   uv sync
   ```

2. **配置环境**:
   编辑 `.env` 文件：
   ```env
   OPENROUTER_API_KEY=your_key
   ADMIN_PASSWORD=admin
   ```

3. **启动服务**:
   ```bash
   uv run python main.py --http
   nohup uv run python main.py --http  2>&1 | split -b 100M -d - log_prefix_ &
   ```

## 访问路径

- **管理后台**: `http://localhost:8000/admin` (网页上传、管理、删除文档)
- **MCP 接口**: `http://localhost:8000/mcp` (用于集成到 Claude/Cursor 等)
