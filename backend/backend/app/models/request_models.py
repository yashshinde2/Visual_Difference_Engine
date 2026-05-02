from pydantic import BaseModel
from typing import Optional


class ImageAnalyzeRequest(BaseModel):
    # Files are uploaded directly; this model used when needed
    rgb_before: Optional[str]
    rgb_after: Optional[str]
    thermal_before: Optional[str] = None
    thermal_after: Optional[str] = None


class VideoAnalyzeRequest(BaseModel):
    video_before: Optional[str]
    video_after: Optional[str]
    thermal_video_before: Optional[str] = None
    thermal_video_after: Optional[str] = None
