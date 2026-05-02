from pydantic import BaseModel
from typing import Dict, Any, Optional, List


class OutputPaths(BaseModel):
    overlay_image: Optional[str] = None
    heatmap_image: Optional[str] = None
    processed_video: Optional[str] = None
    regions: Optional[List[str]] = None


class Scores(BaseModel):
    """Comprehensive analysis scores"""
    ssim_score: Optional[float] = None
    ssim_percent: Optional[float] = None
    mse: Optional[float] = None
    mean_error: Optional[float] = None
    difference_percentage: Optional[float] = None
    anomaly_severity: Optional[float] = None
    temporal_change: Optional[float] = None
    confidence: Optional[float] = None
    thermal_variation: Optional[float] = None


class Metrics(BaseModel):
    """Detailed metrics for analysis"""
    ssim_score: Optional[float] = None
    ssim_percent: Optional[float] = None
    mse: Optional[float] = None
    difference_percent: Optional[float] = None
    changed_pixels: Optional[int] = None
    total_pixels: Optional[int] = None
    regions_detected: Optional[int] = None
    severity_score: Optional[float] = None


class AnalyzeResponse(BaseModel):
    analysis_id: str
    mode: str
    scores: Scores
    metrics: Optional[Metrics] = None
    regions_detected: int
    output: OutputPaths
