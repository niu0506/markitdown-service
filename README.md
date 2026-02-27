# MarkItDown 在线转换服务

将 PDF、Word、PPT、Excel、图片等格式一键转为 Markdown。

## 支持格式

PDF · DOCX · PPTX · XLSX · CSV · HTML · TXT · JSON · XML · JPG/PNG · MP3/WAV · ZIP

## 本地运行

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

访问 http://localhost:8000

## 部署到 Render（免费）

### 方法一：一键部署（推荐）

1. Fork 本仓库到你的 GitHub 账号
2. 登录 [Render](https://render.com) 并注册账号
3. 点击 **New → Web Service**
4. 选择 **Connect a repository**，授权并选择你 Fork 的仓库
5. Render 会自动读取 `render.yaml` 配置文件
6. 点击 **Create Web Service**，等待部署完成（约 3~5 分钟）

### 方法二：手动配置

如果自动读取配置失败，手动填写：

| 字段 | 值 |
|------|-----|
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

### 注意事项

- Render 免费套餐在 **15 分钟无访问后会自动休眠**，下次访问需要 30~60 秒冷启动
- 如需避免休眠，可使用 [UptimeRobot](https://uptimerobot.com) 每 10 分钟 ping 一次
- 文件大小限制：20MB

## 项目结构

```
markitdown-service/
├── main.py          # FastAPI 后端
├── index.html       # 前端页面
├── requirements.txt # Python 依赖
├── render.yaml      # Render 部署配置
└── README.md
```
