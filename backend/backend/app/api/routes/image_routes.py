from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import Optional
from ...controllers.image_controller import analyze_image
from ...dependencies import get_logger_dep

router = APIRouter()


@router.post("/analyze")
async def analyze(
    rgb_before: UploadFile = File(...),
    rgb_after: UploadFile = File(...),
    thermal_before: Optional[UploadFile] = File(None),
    thermal_after: Optional[UploadFile] = File(None),
    logger=Depends(get_logger_dep),
):
    try:
        result = await analyze_image(
            rgb_before, rgb_after, thermal_before, thermal_after
        )
        return result
    except Exception as e:
        logger.error("Image analysis failed: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))
