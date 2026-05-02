from fastapi import UploadFile
from typing import Optional
import uuid
from ..services.pipeline_service import run_video_pipeline
from ..utils.file_manager import save_upload_file
from ..config import UPLOAD_DIR
import os


async def analyze_video(
    video_before: UploadFile,
    video_after: UploadFile,
    thermal_video_before: Optional[UploadFile] = None,
    thermal_video_after: Optional[UploadFile] = None,
):
    uid = str(uuid.uuid4())
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    vb_path = save_upload_file(video_before, f"{uid}_video_before")
    va_path = save_upload_file(video_after, f"{uid}_video_after")
    tb_path = None
    ta_path = None
    if thermal_video_before:
        tb_path = save_upload_file(thermal_video_before, f"{uid}_thermal_video_before")
    if thermal_video_after:
        ta_path = save_upload_file(thermal_video_after, f"{uid}_thermal_video_after")

    result = await run_video_pipeline(vb_path, va_path, tb_path, ta_path, uid)
    return result
