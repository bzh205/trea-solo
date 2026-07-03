"""FastAPI Web 应用 - 演示页面后端"""
import sys
import os
import json
import asyncio
from pathlib import Path

# 将项目根目录加入 sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core.engine import PriceCompareEngine

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title="电商价格采集对比工具")

# 静态资源
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """首页 - 初始化时通过JS加载示例数据"""
    return templates.TemplateResponse(request, "index.html")


@app.get("/api/sample")
async def get_sample_data():
    """获取示例数据"""
    sample_path = PROJECT_ROOT / "data" / "sample_results.json"
    if sample_path.exists():
        with open(sample_path, "r", encoding="utf-8") as f:
            return JSONResponse(json.load(f))
    return JSONResponse({"error": "示例数据不存在"}, status_code=404)


@app.post("/api/search")
async def search(request: Request):
    """实时采集搜索接口"""
    try:
        body = await request.json()
        keyword = body.get("keyword", "").strip()
        platforms = body.get("platforms", ["jd", "taobao", "pdd"])
        max_items = body.get("max_items", 20)

        if not keyword:
            return JSONResponse({"error": "请输入关键词"}, status_code=400)

        engine = PriceCompareEngine(headless=True)
        result = await engine.run(keyword, platforms, max_items)
        return JSONResponse(result)
    except RuntimeError as e:
        return JSONResponse({"error": str(e), "type": "browser_missing"}, status_code=503)
    except Exception as e:
        return JSONResponse({"error": f"采集失败: {str(e)}", "type": "unknown"}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
