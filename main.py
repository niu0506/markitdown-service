from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import traceback
from pathlib import Path

app = FastAPI(title="MarkItDown Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".pptx", ".ppt",
    ".xlsx", ".xls", ".csv", ".html", ".htm",
    ".txt", ".md", ".xml", ".json", ".zip"
}

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB


@app.get("/", response_class=HTMLResponse)
async def index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/convert")
async def convert(file: UploadFile = File(...)):
    # Validate file extension
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式: {suffix}。支持的格式: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # Read file content
    content = await file.read()

    # Check file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件太大，最大支持 20MB，当前文件: {len(content) / 1024 / 1024:.1f}MB"
        )

    # Write to temp file and convert
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        from markitdown import MarkItDown
        md = MarkItDown()
        result = md.convert(tmp_path)
        markdown_text = result.text_content

        if not markdown_text or not markdown_text.strip():
            raise HTTPException(status_code=422, detail="文件内容为空或无法提取文本")

        return JSONResponse({
            "success": True,
            "filename": file.filename,
            "markdown": markdown_text,
            "char_count": len(markdown_text),
            "line_count": len(markdown_text.splitlines())
        })

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"转换失败: {str(e)}")
    finally:
        os.unlink(tmp_path)


@app.get("/health")
async def health():
    return {"status": "ok"}
