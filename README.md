# MarkItDown Service

文档转 Markdown 后端服务，基于 FastAPI 和 MarkItDown 构建。

## 功能

- 支持多种文档格式转换为 Markdown
- RESTful API 接口
- 自动保活（防止云平台休眠）

## 支持的文件格式

`.pdf` `.docx` `.doc` `.pptx` `.ppt` `.xlsx` `.xls` `.csv` `.html` `.htm` `.txt` `.md` `.xml` `.json` `.zip`

## 快速开始

### 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

访问 http://localhost:8000 即可使用。

### 部署到 Render

1. Fork 或 clone 本仓库
2. 在 Render 创建新的 Web Service
3. 连接 GitHub 仓库
4. Render 会自动检测 `render.yaml` 配置

**环境变量：**
- `SELF_URL`: 服务地址（用于心跳保活），如 `https://your-app.onrender.com`

## API 接口

### GET /

返回前端 HTML 页面

### GET /health

健康检查端点

### POST /convert

上传文件并转换为 Markdown

**请求：**
- Content-Type: `multipart/form-data`
- Body: `file` 字段（文件）

**响应：**
```json
{
  "success": true,
  "filename": "document.pdf",
  "markdown": "转换后的Markdown内容...",
  "char_count": 1234,
  "line_count": 56
}
```

**错误响应：**
```json
{
  "detail": "错误信息"
}
```

## 限制

- 最大文件大小：20MB
- 免费版 Render 服务15分钟无请求会休眠（已内置心跳保活）

## 技术栈

- Python 3.11
- FastAPI
- MarkItDown
- Uvicorn

## License

MIT
