"""
Advanced Image Pipeline Service - Research Grade
Uses advanced engines for comprehensive change detection.
"""

from typing import Optional, Dict, Any
import numpy as np
import cv2
import asyncio
import os

from ..engines.alignment_engine import align_images
from ..engines.rgb_engine_advanced import compute_rgb_diff_advanced
from ..engines.multiscale_engine import detect_multiscale_anomalies
from ..engines.thermal_engine import compute_thermal_diff
from ..services.fusion_service import fuse_maps
from ..services.scoring_service_advanced import compute_scores_advanced, validate_scores
from ..utils.visualization import create_heatmap_overlay_advanced, save_image
from ..utils.file_manager import unique_output_path
from ..utils.performance_logger import PerformanceTracker
from ..config import OUTPUT_DIR


async def run_image_pipeline_advanced(
    rgb_before_path: str,
    rgb_after_path: str,
    thermal_before_path: Optional[str],
    thermal_after_path: Optional[str],
    analysis_id: str,
) -> Dict[str, Any]:
    """
    Advanced image analysis pipeline with research-grade quality.
    
    Stages:
    1. Load images
    2. Align with RANSAC
    3. Compute advanced RGB metrics
    4. Compute thermal metrics (if available)
    5. Multi-scale anomaly detection
    6. Advanced scoring
    7. Visualization
    8. Performance logging
    """
    
    perf = PerformanceTracker()
    
    # Stage 1: Load Images
    perf.start_stage("Load Images")
    img_b = cv2.cvtColor(cv2.imread(rgb_before_path), cv2.COLOR_BGR2RGB)
    img_a = cv2.cvtColor(cv2.imread(rgb_after_path), cv2.COLOR_BGR2RGB)
    
    mode = "rgb"
    thermal_map = None
    if thermal_before_path and thermal_after_path:
        t_b = cv2.imread(thermal_before_path, cv2.IMREAD_UNCHANGED)
        t_a = cv2.imread(thermal_after_path, cv2.IMREAD_UNCHANGED)
        mode = "hybrid"
    else:
        t_b = t_a = None
    perf.end_stage()
    
    # Stage 2: Image Alignment
    perf.start_stage("Image Alignment")
    aligned_a = align_images(img_b, img_a)
    perf.end_stage()
    
    # Stage 3: Advanced RGB Difference Computation
    perf.start_stage("RGB Difference Computation")
    rgb_diff, rgb_metrics = compute_rgb_diff_advanced(img_b, aligned_a, remove_borders=True)
    perf.end_stage()
    
    # Stage 4: Thermal Processing (if available)
    perf.start_stage("Thermal Processing")
    if t_b is not None and t_a is not None:
        thermal_map = compute_thermal_diff(t_b, t_a)
    perf.end_stage()
    
    # Stage 5: Fusion
    perf.start_stage("Map Fusion")
    fused = fuse_maps(rgb_diff, thermal_map)
    perf.end_stage()
    
    # Stage 6: Multi-Scale Anomaly Detection
    perf.start_stage("Multi-Scale Detection")
    detection_result = detect_multiscale_anomalies(fused, thresh=0.15, min_area=200)
    regions = detection_result["regions"]
    mask = detection_result["mask"]
    perf.end_stage()
    
    # Stage 7: Advanced Scoring
    perf.start_stage("Metrics Computation")
    total_pixels = rgb_metrics.get("total_pixels", 1)
    scores = compute_scores_advanced(
        rgb_metrics,
        thermal_map,
        mask,
        regions_count=len(regions),
        total_pixels=total_pixels
    )
    
    # Validate scores
    validate_scores(scores)
    perf.end_stage()
    
    # Stage 8: Visualization
    perf.start_stage("Visualization Generation")
    
    # Heatmap - improved rendering
    heatmap_path = unique_output_path(OUTPUT_DIR, f"{analysis_id}_heatmap.png")
    save_image(mask * 255, heatmap_path)
    
    # Overlay with proper intensity mapping
    overlay_path = unique_output_path(OUTPUT_DIR, f"{analysis_id}_overlay.png")
    create_heatmap_overlay_advanced(aligned_a, fused, overlay_path, opacity=0.35)
    
    # Region extraction
    region_base = unique_output_path(OUTPUT_DIR, f"{analysis_id}_region")
    region_paths = []
    if regions:
        from ..utils.visualization import save_regions_advanced
        region_paths = save_regions_advanced(aligned_a, regions, region_base)
    
    # SSIM map visualization
    ssim_map_path = unique_output_path(OUTPUT_DIR, f"{analysis_id}_ssim_map.png")
    # For visualization, we'll save the fused map as a pseudo-SSIM map
    save_image((fused * 255).astype(np.uint8), ssim_map_path)
    
    perf.end_stage()
    
    # Stage 9: Get Performance Report
    perf_report = perf.get_report()
    perf.print_report()
    
    # Build comprehensive result
    result = {
        "analysis_id": analysis_id,
        "mode": mode,
        "timestamp": perf_report["timestamp"],
        "processing_time_ms": perf_report["total_time_ms"],
        "processing_time_sec": perf_report["total_time_sec"],
        
        # Metrics (comprehensive)
        "metrics": {
            "severity": scores.get("severity"),
            "confidence": scores.get("confidence"),
            "integrity": scores.get("integrity"),
            "anomaly_score": scores.get("anomaly_score"),
            "ssim_score": scores.get("ssim_score"),
            "ssim_percent": scores.get("ssim_percent"),
            "mse": scores.get("mse"),
            "psnr": scores.get("psnr"),
            "mean_error": scores.get("mean_error"),
            "difference_percentage": scores.get("difference_percentage"),
            "changed_pixels": scores.get("changed_pixels"),
            "region_count": scores.get("region_count"),
            "region_density": scores.get("region_density"),
            "mask_coverage": scores.get("mask_coverage"),
            "histogram_similarity": scores.get("histogram_similarity"),
            "edge_difference": scores.get("edge_difference"),
            "thermal_variation": scores.get("thermal_variation"),
        },
        
        # Output images
        "output": {
            "overlay_image": str(overlay_path),
            "heatmap_image": str(heatmap_path),
            "ssim_map": str(ssim_map_path),
            "regions": region_paths,
        },
        
        # Performance breakdown
        "performance": perf_report["stages"],
        
        # Validation status
        "validation_status": "PASS" if validate_scores(scores) else "FAIL",
    }
    
    return result


async def run_image_pipeline(
    rgb_before_path: str,
    rgb_after_path: str,
    thermal_before_path: Optional[str],
    thermal_after_path: Optional[str],
    analysis_id: str,
) -> Dict[str, Any]:
    """
    Wrapper that uses advanced pipeline (for backwards compatibility).
    """
    return await run_image_pipeline_advanced(
        rgb_before_path,
        rgb_after_path,
        thermal_before_path,
        thermal_after_path,
        analysis_id,
    )
