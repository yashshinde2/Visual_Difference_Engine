"""
Advanced Visualization Functions - Research Grade
Improved heatmap rendering and region extraction.
"""

import cv2
import numpy as np
from typing import List, Dict
from pathlib import Path


def normalize_diff_map(diff_map: np.ndarray) -> np.ndarray:
    """
    Properly normalize difference map for visualization.
    Handles edge cases and ensures full color range usage.
    """
    if diff_map.size == 0:
        return diff_map
    
    # Remove NaN and Inf
    diff_map = np.nan_to_num(diff_map, nan=0.0, posinf=1.0, neginf=0.0)
    
    # Normalize to 0-255
    min_val = np.min(diff_map)
    max_val = np.max(diff_map)
    
    if max_val > min_val:
        normalized = ((diff_map - min_val) / (max_val - min_val) * 255).astype(np.uint8)
    else:
        normalized = np.zeros_like(diff_map, dtype=np.uint8)
    
    return normalized


def create_heatmap_overlay_advanced(
    original: np.ndarray,
    diff_map: np.ndarray,
    output_path: str,
    opacity: float = 0.35,
    colormap: int = cv2.COLORMAP_INFERNO
) -> None:
    """
    Create advanced heatmap overlay with proper intensity mapping.
    
    Args:
        original: Original RGB image
        diff_map: Difference map (0-1 float or 0-255 range)
        output_path: Path to save result
        opacity: Overlay opacity (0-1)
        colormap: OpenCV colormap
    """
    # Ensure same size
    if original.shape[:2] != diff_map.shape[:2]:
        diff_map = cv2.resize(diff_map, (original.shape[1], original.shape[0]))
    
    # Normalize difference map to 0-255
    diff_normalized = normalize_diff_map(diff_map)
    
    # Apply colormap to get heatmap
    heatmap = cv2.applyColorMap(diff_normalized, colormap)
    
    # Prepare original image in BGR format
    if original.ndim == 3 and original.shape[2] == 3:
        # Check if RGB or BGR by examining array values
        if original.dtype == np.uint8:
            original_bgr = cv2.cvtColor(original, cv2.COLOR_RGB2BGR)
        else:
            # Float format, convert to uint8 first
            original_normalized = normalize_diff_map(original)
            original_bgr = cv2.cvtColor(original_normalized, cv2.COLOR_RGB2BGR)
    else:
        # Grayscale - convert to 3-channel
        if original.dtype != np.uint8:
            original_normalized = normalize_diff_map(original)
        else:
            original_normalized = original
        original_bgr = cv2.cvtColor(original_normalized, cv2.COLOR_GRAY2BGR)
    
    # Blend with opacity
    overlay = cv2.addWeighted(
        original_bgr,
        1.0 - opacity,
        heatmap,
        opacity,
        0
    )
    
    cv2.imwrite(output_path, overlay)


def save_image(image: np.ndarray, output_path: str) -> None:
    """
    Save image properly handling format conversion.
    Assumes input is BGR (from OpenCV operations) or needs conversion.
    """
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Handle different input formats
    if image.dtype != np.uint8:
        # Convert float to uint8
        if image.max() <= 1.0:
            image = (image * 255).astype(np.uint8)
        else:
            image = image.astype(np.uint8)
    
    # Handle different channel configurations
    if image.ndim == 3 and image.shape[2] == 3:
        # Already 3-channel (should be BGR from OpenCV operations)
        cv2.imwrite(output_path, image)
    elif image.ndim == 3 and image.shape[2] == 4:
        # RGBA - convert to BGR
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
        cv2.imwrite(output_path, image_bgr)
    elif image.ndim == 2:
        # Grayscale
        cv2.imwrite(output_path, image)
    else:
        cv2.imwrite(output_path, image)


def save_regions_advanced(
    image: np.ndarray,
    regions: List[Dict],
    output_base: str,
    padding: int = 10
) -> List[str]:
    """
    Extract and save regions of interest with padding and enhancement.
    
    Args:
        image: Original image (RGB format)
        regions: List of region dictionaries with bbox
        output_base: Base path for saving (without extension)
        padding: Pixel padding around region
    
    Returns:
        List of saved region paths
    """
    region_paths = []
    h, w = image.shape[:2]
    
    for idx, region in enumerate(regions):
        bbox = region.get("bbox", [])
        if not bbox or len(bbox) < 4:
            continue
        
        x, y, region_w, region_h = bbox
        
        # Apply padding
        x_start = max(0, x - padding)
        y_start = max(0, y - padding)
        x_end = min(w, x + region_w + padding)
        y_end = min(h, y + region_h + padding)
        
        # Extract region
        cropped = image[y_start:y_end, x_start:x_end].copy()
        
        if cropped.size == 0:
            continue
        
        # Ensure it's uint8
        if cropped.dtype != np.uint8:
            if cropped.max() <= 1.0:
                cropped = (cropped * 255).astype(np.uint8)
            else:
                cropped = cropped.astype(np.uint8)
        
        # Enhance contrast for better visibility
        if cropped.ndim == 3 and cropped.shape[2] == 3:
            # RGB to HSV for brightness enhancement
            hsv = cv2.cvtColor(cropped, cv2.COLOR_RGB2HSV)
            hsv[:, :, 2] = cv2.equalizeHist(hsv[:, :, 2])
            cropped_enhanced = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
        else:
            # Grayscale histogram equalization
            cropped_enhanced = cv2.equalizeHist(cropped)
        
        # Save as BGR (OpenCV writes BGR)
        region_path = f"{output_base}_{idx}.png"
        if cropped_enhanced.ndim == 3 and cropped_enhanced.shape[2] == 3:
            # Convert RGB to BGR for saving
            cropped_bgr = cv2.cvtColor(cropped_enhanced, cv2.COLOR_RGB2BGR)
            cv2.imwrite(region_path, cropped_bgr)
        else:
            cv2.imwrite(region_path, cropped_enhanced)
        
        region_paths.append(region_path)
    
    return region_paths


def create_comparison_image(
    img_before: np.ndarray,
    img_after: np.ndarray,
    heatmap: np.ndarray,
    output_path: str
) -> None:
    """
    Create a 3-panel comparison image (Before | After | Heatmap).
    """
    # Ensure same size
    h, w = img_before.shape[:2]
    img_after = cv2.resize(img_after, (w, h))
    heatmap = cv2.resize(heatmap, (w, h))
    
    # Create separator (vertical lines)
    sep_color = np.full((h, 2, 3), 128, dtype=np.uint8)
    
    # Stack horizontally with separators
    if img_before.ndim == 3 and img_before.shape[2] == 3:
        img_before_bgr = cv2.cvtColor(img_before.astype(np.uint8), cv2.COLOR_RGB2BGR)
    else:
        img_before_bgr = img_before
    
    if img_after.ndim == 3 and img_after.shape[2] == 3:
        img_after_bgr = cv2.cvtColor(img_after.astype(np.uint8), cv2.COLOR_RGB2BGR)
    else:
        img_after_bgr = img_after
    
    heatmap_colored = cv2.applyColorMap(
        normalize_diff_map(heatmap),
        cv2.COLORMAP_INFERNO
    )
    
    comparison = np.hstack([img_before_bgr, sep_color, img_after_bgr, sep_color, heatmap_colored])
    cv2.imwrite(output_path, comparison)


def create_metric_visualization(
    metrics: Dict,
    output_path: str,
    image_size: tuple = (800, 600)
) -> None:
    """
    Create a text-based metric visualization image.
    """
    width, height = image_size
    image = np.ones((height, width, 3), dtype=np.uint8) * 240
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    thickness = 1
    line_height = 25
    x_pos = 20
    y_pos = 30
    
    # Title
    cv2.putText(image, "ANALYSIS METRICS", (x_pos, y_pos), font, 1.2, (0, 0, 0), 2)
    y_pos += line_height * 1.5
    
    # Metrics
    metric_items = [
        ("Severity", metrics.get("severity", 0)),
        ("Confidence", metrics.get("confidence", 0)),
        ("SSIM Score", metrics.get("ssim_score", 0)),
        ("Mean Error %", metrics.get("mean_error", 0)),
        ("Difference %", metrics.get("difference_percentage", 0)),
        ("Regions Detected", metrics.get("region_count", 0)),
        ("Mask Coverage %", metrics.get("mask_coverage", 0)),
        ("Processing Time ms", metrics.get("processing_time_ms", 0)),
    ]
    
    for label, value in metric_items:
        text = f"{label}: {value}"
        cv2.putText(image, text, (x_pos, y_pos), font, font_scale, (0, 0, 0), thickness)
        y_pos += line_height
    
    cv2.imwrite(output_path, image)
