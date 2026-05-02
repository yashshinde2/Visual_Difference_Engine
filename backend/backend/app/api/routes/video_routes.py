from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import Optional
from ...controllers.video_controller import analyze_video
from ...dependencies import get_logger_dep

router = APIRouter()


@router.post("/analyze")
async def analyze(
    video_before: UploadFile = File(...),
    video_after: UploadFile = File(...),
    thermal_video_before: Optional[UploadFile] = File(None),
    thermal_video_after: Optional[UploadFile] = File(None),
    logger=Depends(get_logger_dep),
):
    try:
        result = await analyze_video(
            video_before, video_after, thermal_video_before, thermal_video_after
        )
        return result
    except Exception as e:
        logger.error("Video analysis failed: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))
