from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .api import routes
from .utils.logger import setup_logging
from .config import OUTPUT_DIR
import os

setup_logging()

app = FastAPI(title="RGB-Thermal Hybrid Visual Difference Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


app.include_router(routes.health_routes.router)
app.include_router(routes.image_routes.router, prefix="/api/image")
app.include_router(routes.video_routes.router, prefix="/api/video")

# serve output and upload folders so frontend can fetch images
app.mount("/outputs", StaticFiles(directory=str(OUTPUT_DIR)), name="outputs")
from .utils.file_manager import UPLOAD_DIR
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
