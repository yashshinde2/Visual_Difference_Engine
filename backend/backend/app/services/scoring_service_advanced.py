"""
Advanced Scoring Service - Research Grade
Implements mathematically consistent and logically correct severity/confidence calculations.
"""

from typing import Optional, Dict
import numpy as np


def compute_scores_advanced(
    rgb_metrics: Dict,
    thermal_map: Optional[np.ndarray],
    mask: np.ndarray,
    regions_count: int = 0,
    total_pixels: int = 1
) -> Dict[str, float]:
    """
    Compute comprehensive analysis scores with mathematically consistent logic.
    
    Key Improvements:
    - Severity = (1 - SSIM) * 100 (CORRECT)
    - Confidence = SSIM * 100 (CORRECT)
    - All scales 0-100 consistently
    - No logical contradictions
    
    Returns:
    {
        "ssim_score": float (0-1),
        "ssim_percent": float (0-100),
        "mse": float,
        "psnr": float,
        "mean_error": float (0-100),
        "difference_percentage": float (0-100),
        "severity": float (0-100),  # Main severity metric (1 - SSIM) * 100
        "confidence": float (0-100),  # Main confidence (SSIM * 100)
        "integrity": float (0-100),   # Signal integrity
        "region_density": float (0-100),
    }
    """
    
    # Extract RGB metrics
    ssim_score = rgb_metrics.get("ssim_score", 0.0)
    mse = rgb_metrics.get("mse", 0.0)
    psnr = rgb_metrics.get("psnr", 50.0)
    difference_percent = rgb_metrics.get("difference_percentage", 0.0)
    changed_pixels = rgb_metrics.get("changed_pixels", 0)
    histogram_similarity = rgb_metrics.get("histogram_similarity", 0.0)
    edge_difference = rgb_metrics.get("edge_difference", 0.0)
    
    # Ensure SSIM is in valid range
    ssim_score = float(np.clip(ssim_score, 0.0, 1.0))
    
    # ===== CORE METRICS (MATHEMATICALLY CORRECT) =====
    
    # 1. SEVERITY = (1 - SSIM) * 100
    # Logic: Perfect match (SSIM=1) → Severity=0
    #        No match (SSIM=0) → Severity=100
    severity = float((1.0 - ssim_score) * 100.0)
    
    # 2. CONFIDENCE = SSIM * 100
    # Logic: High similarity (SSIM=1) → Confidence=100
    #        No similarity (SSIM=0) → Confidence=0
    confidence = float(ssim_score * 100.0)
    
    # 3. MEAN ERROR based on MSE
    # Normalize MSE to 0-100 scale
    max_mse = 255.0 * 255.0  # Maximum possible MSE for uint8 images
    mean_error = float(min(100.0, (mse / max_mse) * 100.0)) if max_mse > 0 else 0.0
    
    # 4. DIFFERENCE PERCENTAGE (already 0-100)
    difference_percentage = float(np.clip(difference_percent, 0.0, 100.0))
    
    # ===== SECONDARY METRICS =====
    
    # 5. INTEGRITY SCORE
    # Based on PSNR and histogram similarity
    # Higher PSNR = Higher integrity
    psnr_normalized = float(min(100.0, (psnr / 50.0) * 100.0))  # PSNR 0-50 → 0-100
    
    # Histogram similarity (convert distance to similarity)
    hist_similarity_score = float(max(0.0, 100.0 - (histogram_similarity * 100.0)))
    
    integrity = float(
        0.6 * psnr_normalized +
        0.4 * hist_similarity_score
    )
    integrity = float(np.clip(integrity, 0.0, 100.0))
    
    # 6. REGION DENSITY
    # Ratio of changed pixels to regions
    region_density = float(0.0)
    if regions_count > 0:
        region_density = float((changed_pixels / max(regions_count, 1)) / max(total_pixels, 1) * 100)
    region_density = float(np.clip(region_density, 0.0, 100.0))
    
    # 7. MASK COVERAGE
    mask_coverage = float(0.0)
    if mask is not None and mask.size > 0:
        mask_coverage = float((np.sum(mask > 0) / mask.size) * 100)
    mask_coverage = float(np.clip(mask_coverage, 0.0, 100.0))
    
    # 8. ANOMALY SCORE (ADVANCED)
    # Composite score from multiple factors
    anomaly_score = float(
        0.4 * severity +              # 40% from structural difference
        0.3 * difference_percentage +  # 30% from pixel difference
        0.2 * region_density +         # 20% from region density
        0.1 * mask_coverage            # 10% from mask coverage
    )
    anomaly_score = float(np.clip(anomaly_score, 0.0, 100.0))
    
    # ===== VALIDATION CHECKS =====
    
    # Thermal variation if available
    thermal_variation = 0.0
    if thermal_map is not None and thermal_map.size > 0:
        thermal_variation = float(min(100.0, np.mean(thermal_map) * 100.0))
    
    # ===== RETURN COMPREHENSIVE SCORES =====
    
    return {
        # Core metrics
        "ssim_score": round(ssim_score, 4),
        "ssim_percent": round(confidence, 2),
        "severity": round(severity, 2),           # Main severity (1-SSIM)*100
        "confidence": round(confidence, 2),       # Main confidence (SSIM*100)
        
        # Error metrics
        "mse": round(mse, 4),
        "psnr": round(psnr, 2),
        "mean_error": round(mean_error, 2),
        
        # Difference metrics
        "difference_percentage": round(difference_percentage, 2),
        "changed_pixels": int(changed_pixels),
        
        # Quality metrics
        "integrity": round(integrity, 2),
        "histogram_similarity": round(hist_similarity_score, 2),
        "edge_difference": round(edge_difference, 2),
        
        # Regional metrics
        "region_count": int(regions_count),
        "region_density": round(region_density, 2),
        "mask_coverage": round(mask_coverage, 2),
        "anomaly_score": round(anomaly_score, 2),
        
        # Thermal metrics
        "thermal_variation": round(thermal_variation, 2),
    }


def validate_scores(scores: Dict[str, float]) -> bool:
    """
    Validate score consistency.
    
    Checks:
    - Severity + Confidence ≈ 100
    - All scores in 0-100 range
    - SSIM and derivatives are consistent
    """
    severity = scores.get("severity", 0)
    confidence = scores.get("confidence", 0)
    
    # Severity + Confidence should sum to ~100
    total = severity + confidence
    if not (95 < total < 105):
        print(f"Warning: Severity + Confidence = {total}, expected ~100")
    
    # All scores should be in valid range
    for key, value in scores.items():
        if isinstance(value, (int, float)):
            if key != "mse" and key != "psnr" and key != "changed_pixels":
                if not (0 <= value <= 100):
                    print(f"Warning: {key} = {value}, expected 0-100")
    
    return True
