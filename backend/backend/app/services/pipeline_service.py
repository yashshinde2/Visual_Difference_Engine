from typing import Optional, Dict, Any
from ..engines.alignment_engine import align_images
from ..engines.rgb_engine_advanced import compute_rgb_diff_advanced
from ..engines.thermal_engine import compute_thermal_diff
from ..engines.multiscale_engine import detect_multiscale_anomalies
from ..services.fusion_service import fuse_maps
from ..services.scoring_service_advanced import compute_scores_advanced, validate_scores
from ..utils.visualization_advanced import create_heatmap_overlay_advanced, save_image, save_regions_advanced
from ..utils.file_manager import unique_output_path
from ..utils.logger import get_logger
from ..utils.performance_logger import PerformanceTracker
from ..engines.video_engine import process_video_pair
from ..config import OUTPUT_DIR
import asyncio
import numpy as np
import os
import cv2
import time


logger = get_logger(__name__)


async def run_image_pipeline(
    rgb_before_path: str,
    rgb_after_path: str,
    thermal_before_path: Optional[str],
    thermal_after_path: Optional[str],
    analysis_id: str,
) -> Dict[str, Any]:
    """
    Advanced image analysis pipeline - Research Grade.
    
    Uses:
    - Advanced RGB engine with illumination robustness
    - Multi-scale anomaly detection
    - Comprehensive scoring system
    - Performance tracking
    """
    try:
        perf = PerformanceTracker()
        logger.info(f"Starting advanced analysis pipeline for {analysis_id}")
        
        # Stage 1: Load Images
        perf.start_stage("Load Images")
        img_b = cv2.cvtColor(cv2.imread(rgb_before_path), cv2.COLOR_BGR2RGB)
        img_a = cv2.cvtColor(cv2.imread(rgb_after_path), cv2.COLOR_BGR2RGB)
        
        if img_b is None or img_a is None:
            raise ValueError("Failed to read RGB images")
        
        logger.debug(f"RGB Before shape: {img_b.shape}, RGB After shape: {img_a.shape}")
        
        mode = "rgb"
        thermal_map = None
        t_b = t_a = None
        if thermal_before_path and thermal_after_path:
            t_b = cv2.imread(thermal_before_path, cv2.IMREAD_UNCHANGED)
            t_a = cv2.imread(thermal_after_path, cv2.IMREAD_UNCHANGED)
            if t_b is not None and t_a is not None:
                mode = "hybrid"
                logger.debug("Thermal images loaded for hybrid analysis")
        perf.end_stage()
        
        # Stage 2: Image Alignment
        perf.start_stage("Image Alignment")
        logger.debug("Aligning images with RANSAC...")
        aligned_a = align_images(img_b, img_a)
        perf.end_stage()
        
        # Stage 3: Advanced RGB Difference
        perf.start_stage("RGB Difference Computation")
        logger.debug("Computing advanced RGB differences...")
        rgb_diff, rgb_metrics = compute_rgb_diff_advanced(img_b, aligned_a, remove_borders=True)
        logger.info(f"RGB Metrics: SSIM={rgb_metrics.get('ssim_score'):.4f}, Diff%={rgb_metrics.get('difference_percentage'):.2f}%")
        perf.end_stage()
        
        # Stage 4: Thermal Processing
        perf.start_stage("Thermal Processing")
        if t_b is not None and t_a is not None:
            logger.debug("Computing thermal differences...")
            thermal_map = compute_thermal_diff(t_b, t_a)
        perf.end_stage()
        
        # Stage 5: Fusion
        perf.start_stage("Map Fusion")
        logger.debug("Fusing difference maps...")
        fused = fuse_maps(rgb_diff, thermal_map)
        perf.end_stage()
        
        # Stage 6: Multi-Scale Anomaly Detection
        perf.start_stage("Multi-Scale Detection")
        logger.debug("Detecting anomalies with multi-scale approach...")
        detection_result = detect_multiscale_anomalies(fused, thresh=0.15, min_area=200)
        regions = detection_result["regions"]
        mask = detection_result["mask"]
        logger.info(f"Regions detected: {len(regions)}")
        perf.end_stage()
        
        # Stage 7: Advanced Scoring
        perf.start_stage("Metrics Computation")
        logger.debug("Computing advanced scores...")
        total_pixels = rgb_metrics.get("total_pixels", 1)
        scores = compute_scores_advanced(
            rgb_metrics,
            thermal_map,
            mask,
            regions_count=len(regions),
            total_pixels=total_pixels
        )
        validate_scores(scores)
        logger.info(f"Scores: Severity={scores.get('severity'):.2f}, Confidence={scores.get('confidence'):.2f}")
        perf.end_stage()
        
        # Stage 8: Visualization
        perf.start_stage("Visualization Generation")
        logger.debug("Generating visualizations...")
        
        # Paths
        overlay_path = unique_output_path(OUTPUT_DIR, f"{analysis_id}_overlay.png")
        heatmap_path = unique_output_path(OUTPUT_DIR, f"{analysis_id}_heatmap.png")
        difference_map_path = unique_output_path(OUTPUT_DIR, f"{analysis_id}_difference.png")
        
        # 1. Overlay: Original image with heatmap overlay (35% opacity)
        create_heatmap_overlay_advanced(aligned_a, fused, overlay_path, opacity=0.35)
        logger.debug(f"Overlay saved to {overlay_path}")
        
        # 2. Heatmap: Colored difference map (full intensity)
        from ..utils.visualization_advanced import normalize_diff_map
        heatmap_normalized = normalize_diff_map(fused)
        heatmap_colored = cv2.applyColorMap(heatmap_normalized, cv2.COLORMAP_INFERNO)
        cv2.imwrite(heatmap_path, heatmap_colored)
        logger.debug(f"Heatmap saved to {heatmap_path}")
        
        # 3. Difference map: Binary mask of detected regions
        save_image(mask * 255, difference_map_path)
        logger.debug(f"Difference map saved to {difference_map_path}")
        
        # Regions
        region_base = unique_output_path(OUTPUT_DIR, f"{analysis_id}_region")
        region_paths = []
        if regions:
            region_paths = save_regions_advanced(aligned_a, regions, region_base, padding=10) 
            logger.debug(f"Saved {len(region_paths)} region images")
        
        perf.end_stage()
        
        # Performance Report
        perf_report = perf.get_report()
        perf.print_report()
        
        # Build Result
        result = {
            "analysis_id": analysis_id,
            "mode": mode,
            "timestamp": perf_report["timestamp"],
            "processing_time_ms": perf_report["total_time_ms"],
            "processing_time_sec": perf_report["total_time_sec"],
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
            "regions_detected": len(regions),
            "output": {
                "overlay_image": str(overlay_path),
                "heatmap_image": str(heatmap_path),
                "difference_map": str(difference_map_path),
                "regions": region_paths,
            },
            "performance": perf_report["stages"],
            "validation_status": "PASS" if validate_scores(scores) else "FAIL",
        }
        
        logger.info(f"Analysis {analysis_id} completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Pipeline error for {analysis_id}: {str(e)}", exc_info=True)
        raise


async def run_video_pipeline(
    video_before_path: str,
    video_after_path: str,
    thermal_before_path: Optional[str],
    thermal_after_path: Optional[str],
    analysis_id: str,
) -> Dict[str, Any]:
    """Video pipeline (placeholder for now)."""
    from ..engines.video_engine import process_video_pair
    out_video = unique_output_path(OUTPUT_DIR, f"{analysis_id}_processed.mp4")
    stats = await asyncio.to_thread(
        process_video_pair,
        video_before_path,
        video_after_path,
        thermal_before_path,
        thermal_after_path,
        out_video,
    )

    result = {
        "analysis_id": analysis_id,
        "mode": stats.get("mode", "rgb"),
        "scores": stats.get("scores", {}),
        "regions_detected": stats.get("regions_detected", 0),
        "output": {
            "processed_video": str(out_video),
        },
    }
    return result
