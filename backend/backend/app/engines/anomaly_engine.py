import cv2
import numpy as np
from typing import List, Dict, Tuple


def detect_anomalies(fused_map, thresh: float = 0.15, min_area: int = 200) -> Tuple[List[Dict], np.ndarray]:
    """
    Detect anomalous regions from fused difference map.
    
    Args:
        fused_map: Normalized difference map (0-1)
        thresh: Threshold for binary segmentation
        min_area: Minimum pixel area to be considered a valid region
    
    Returns:
        - List of region dictionaries with bbox and area
        - Binary mask of detected regions
    """
    # fused_map expected 0-1 float
    gray = (fused_map * 255).astype('uint8')
    
    # Adaptive thresholding for better detection
    _, bw = cv2.threshold(gray, int(thresh * 255), 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Morphological operations to clean up noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    bw = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel, iterations=2)  # fill holes
    bw = cv2.morphologyEx(bw, cv2.MORPH_OPEN, kernel, iterations=1)   # remove noise

    # Find contours
    contours, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    regions = []
    mask = np.zeros_like(bw, dtype='uint8')
    
    for contour in contours:
        area = cv2.contourArea(contour)
        
        # Filter by minimum area to remove noise
        if area < min_area:
            continue
            
        x, y, w, h = cv2.boundingRect(contour)
        
        # Validate region dimensions
        if w < 5 or h < 5:  # too small
            continue
        
        regions.append({
            "bbox": [int(x), int(y), int(w), int(h)],
            "area": int(area),
            "contour": contour
        })
        
        # Draw on mask
        cv2.drawContours(mask, [contour], 0, 255, -1)

    return regions, mask
