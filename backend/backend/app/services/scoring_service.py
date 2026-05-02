from typing import Optional, Dict
import numpy as np


def compute_scores(
    rgb_metrics: Dict,
    thermal_map: Optional[np.ndarray],
    mask: np.ndarray,
    regions_count: int = 0
) -> Dict[str, float]:
    """
    Compute comprehensive analysis scores from metrics and masks.
    
    Returns:
    {
        "ssim_score": float (0-1),
        "ssim_percent": float (0-100),
        "mse": float,
        "mean_error": float (0-100),
        "difference_percentage": float (0-100),
        "anomaly_severity": float (0-100),
        "temporal_change": float (0-100),
        "confidence": float (0-100)
    }
    """
    
    # Extract RGB metrics
    ssim_score = rgb_metrics.get("ssim_score", 0.0)
    mse = rgb_metrics.get("mse", 0.0)
    difference_percent = rgb_metrics.get("difference_percentage", 0.0)
    changed_pixels = rgb_metrics.get("changed_pixels", 0)
    total_pixels = rgb_metrics.get("total_pixels", 1)
    
    # Normalize MSE to 0-100 (max MSE for uint8 is 255²=65025)
    max_mse = 255 * 255
    mean_error = float(min(100.0, (mse / max_mse) * 100)) if mse > 0 else 0.0
    
    # SSIM percentage
    ssim_percent = float(ssim_score * 100)
    
    # Anomaly severity based on mask coverage and region detection
    mask_area = np.sum(mask) if mask is not None else 0
    mask_percent = float((mask_area / max(total_pixels, 1)) * 100) if mask is not None else 0.0
    
    # Weighted severity: combines % changed pixels, mask coverage, and region count
    region_factor = min(1.0, regions_count / 10.0)  # normalize to 0-1
    anomaly_severity = (
        0.5 * difference_percent +      # 50% from pixel difference
        0.3 * mask_percent +             # 30% from mask coverage
        0.2 * (region_factor * 100)      # 20% from region count
    )
    anomaly_severity = float(min(100.0, max(0.0, anomaly_severity)))
    
    # Temporal change (similar to difference %)
    temporal_change = float(difference_percent)
    
    # Confidence: inverse of error (higher accuracy = higher confidence)
    confidence = float(max(0.0, 100.0 - mean_error))
    
    # Thermal variation if thermal data exists
    thermal_variation = 0.0
    if thermal_map is not None:
        thermal_variation = float(min(100.0, np.mean(thermal_map) * 100)) if np.size(thermal_map) > 0 else 0.0
    
    return {
        "ssim_score": round(ssim_score, 4),
        "ssim_percent": round(ssim_percent, 2),
        "mse": round(mse, 4),
        "mean_error": round(mean_error, 2),
        "difference_percentage": round(difference_percent, 2),
        "anomaly_severity": round(anomaly_severity, 2),
        "temporal_change": round(temporal_change, 2),
        "confidence": round(confidence, 2),
        "thermal_variation": round(thermal_variation, 2),
    }
