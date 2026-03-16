# ===================================================
# main.py — MarkItDown 文档转 Markdown 后端服务
# 基于 FastAPI 框架，提供文件上传与格式转换接口
# ===================================================

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import tempfile
import os
import traceback
import asyncio
import httpx
from pathlib import Path

SELF_URL = os.getenv("SELF_URL", "")  # Render上设置自己的URL，如 https://xxx.onrender.com
KEEPALIVE_INTERVAL = 600  # 10分钟 = 600秒


async def keepalive_task():
    """后台心跳任务，每隔10分钟ping自己防止休眠"""
    if not SELF_URL:
        print("[KeepAlive] SELF_URL 未设置，心跳任务已跳过")
        return
    await asyncio.sleep(30)  # 启动后等待30秒
    async with httpx.AsyncClient() as client:
        while True:
            try:
                resp = await client.get(f"{SELF_URL}/health", timeout=30)
                print(f"[KeepAlive] 心跳发送成功: {resp.status_code}")
            except Exception as e:
                print(f"[KeepAlive] 心跳发送失败: {e}")
            await asyncio.sleep(KEEPALIVE_INTERVAL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理：启动后台心跳任务"""
    task = asyncio.create_task(keepalive_task())
    yield
    task.cancel()


# 创建 FastAPI 应用实例，设置服务名称和版本
app = FastAPI(title="MarkItDown Service", version="1.0.0", lifespan=lifespan)

# 配置跨域资源共享 (CORS) 中间件
# 允许所有来源、所有方法和所有请求头，便于前端跨域调用
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 允许所有域名（生产环境建议改为具体域名）
    allow_methods=["*"],   # 允许所有 HTTP 方法
    allow_headers=["*"],   # 允许所有请求头
)

# 支持的文件扩展名白名单
# 只有在此集合中的格式才会被接受处理
ALLOWED_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".pptx", ".ppt",
    ".xlsx", ".xls", ".csv", ".html", ".htm",
    ".txt", ".md", ".xml", ".json", ".zip"
}

# 文件大小上限：20MB（单位：字节）
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB


@app.get("/", response_class=HTMLResponse)
async def index():
    """
    首页路由：读取并返回前端 HTML 页面。
    FastAPI 会将返回值作为 HTML 内容直接渲染在浏览器中。
    """
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/health")
async def health():
    """健康检查端点，用于心跳保活"""
    return {"status": "ok", "service": "markitdown"}


@app.post("/convert")
async def convert(file: UploadFile = File(...)):
    """
    文件转换路由：接收上传的文件，将其转换为 Markdown 文本。

    处理流程：
    1. 校验文件扩展名是否在白名单内
    2. 读取文件内容并检查大小是否超限
    3. 将文件写入临时目录
    4. 调用 MarkItDown 执行转换
    5. 返回转换结果（含字符数和行数统计）
    """

    # ── 第一步：校验文件格式 ──────────────────────────
    suffix = Path(file.filename).suffix.lower()  # 提取并统一转为小写扩展名
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式: {suffix}。支持的格式: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # ── 第二步：读取文件内容 ──────────────────────────
    content = await file.read()

    # 检查文件大小是否超过 20MB 限制
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件太大，最大支持 20MB，当前文件: {len(content) / 1024 / 1024:.1f}MB"
        )

    # ── 第三步：写入临时文件 ──────────────────────────
    # 使用系统临时目录存放上传文件，保留原始扩展名以便 MarkItDown 识别格式
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name  # 记录临时文件路径，稍后清理

    try:
        # ── 第四步：调用 MarkItDown 进行转换 ─────────
        from markitdown import MarkItDown
        md = MarkItDown()               # 初始化转换器
        result = md.convert(tmp_path)   # 执行文件转换
        markdown_text = result.text_content  # 获取转换后的 Markdown 文本

        # 若转换结果为空，返回 422 错误（文件无可提取内容）
        if not markdown_text or not markdown_text.strip():
            raise HTTPException(status_code=422, detail="文件内容为空或无法提取文本")

        # ── 第五步：返回转换结果 ──────────────────────
        return JSONResponse({
            "success": True,
            "filename": file.filename,          # 原始文件名
            "markdown": markdown_text,           # 转换后的 Markdown 内容
            "char_count": len(markdown_text),    # 字符总数（用于前端展示统计）
            "line_count": len(markdown_text.splitlines())  # 行数统计
        })

    except HTTPException:
        # 直接重新抛出已知的 HTTP 异常，不做额外包装
        raise
    except Exception as e:
        # 捕获所有未预期异常，打印堆栈便于排查，并返回 500 错误
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"转换失败: {str(e)}")
    finally:
        # 无论成功或失败，始终删除临时文件，避免磁盘泄漏
        os.unlink(tmp_path)

