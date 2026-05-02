import numpy as np
import cv2
from typing import Optional, List


def create_heatmap_overlay(
    image, 
    fused_map: np.ndarray, 
    out_path: str,
    opacity: float = 0.3, 
    colormap: int = cv2.COLORMAP_JET
):
    """
    Create overlay with proper heatmap normalization.
    """
    # Ensure fused_map is normalized 0-1
    if fused_map.max() > 1.0:
        fused_map = fused_map / 255.0
    
    # Normalize difference map properly: stretch to full 0-255 range
    heat_norm = cv2.normalize(fused_map, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    
    # Apply Gaussian blur to smooth the heatmap
    heat_smooth = cv2.GaussianBlur(heat_norm, (5, 5), 0)
    
    # Apply colormap
    heat_color = cv2.applyColorMap(heat_smooth, colormap)
    
    # Prepare base image
    base = image.copy()
    if base.ndim == 3:
        base_bgr = cv2.cvtColor(base, cv2.COLOR_RGB2BGR)
    else:
        base_bgr = cv2.cvtColor(base, cv2.COLOR_GRAY2BGR)
    
    # Blend: opacity controls heatmap contribution
    overlay = cv2.addWeighted(base_bgr, 1.0 - opacity, heat_color, opacity, 0)
    cv2.imwrite(out_path, overlay)


def save_image(img, path: str):
    """Save image to path, creating directories as needed."""
    import os
    dirname = os.path.dirname(path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    if img.ndim == 2:
        cv2.imwrite(path, img)
    else:
        # assume RGB
        cv2.imwrite(path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))


def save_regions(image, regions: List, base_path: str) -> List[str]:
    """
    Save cropped regions from image to individual files.
    
    Args:
        image: Image array (RGB)
        regions: List of region dicts with 'bbox' = [x, y, w, h]
        base_path: Base path for output files
    
    Returns:
        List of output file paths
    """
    out = []
    img = image.copy()
    
    for i, r in enumerate(regions):
        x, y, w, h = r.get('bbox', [0, 0, 0, 0])
        
        # pad bounding box slightly to avoid tiny strips and to include context
        pad = 8
        x0 = max(0, x - pad)
        y0 = max(0, y - pad)
        x1 = min(img.shape[1], x + w + pad)
        y1 = min(img.shape[0], y + h + pad)

        # Validate coordinates
        if x0 >= img.shape[1] or y0 >= img.shape[0] or x1 <= x0 or y1 <= y0:
            continue

        crop = img[y0:y1, x0:x1]

        # If crop is very small (noise), try to expand a bit; otherwise skip
        ch, cw = crop.shape[0], crop.shape[1]
        min_dim = 20
        if ch < min_dim or cw < min_dim:
            # attempt to expand to at least min_dim centered on original bbox
            cx = x + w // 2
            cy = y + h // 2
            half = max(min_dim // 2, pad)
            x0 = max(0, cx - half)
            y0 = max(0, cy - half)
            x1 = min(img.shape[1], cx + half)
            y1 = min(img.shape[0], cy + half)
            crop = img[y0:y1, x0:x1]
            ch, cw = crop.shape[0], crop.shape[1]
            if ch < min_dim or cw < min_dim:
                # still too small, skip
                continue

        path = f"{base_path}_region_{i+1}.png"
        
        # Write as BGR
        if crop.ndim == 3:
            cv2.imwrite(path, cv2.cvtColor(crop, cv2.COLOR_RGB2BGR))
        else:
            cv2.imwrite(path, crop)
        
        out.append(path)
    
    return out


def draw_regions_on_image(image_path: str, regions: List, color=(0, 0, 255), thickness: int = 2):
    """
    Draw bounding boxes and labels onto an existing image file.
    Modifies the file in-place.
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return

        for i, r in enumerate(regions):
            bbox = r.get('bbox', [0, 0, 0, 0])
            x, y, w, h = map(int, bbox)
            # ensure bbox within image
            x = max(0, x)
            y = max(0, y)
            x2 = min(img.shape[1]-1, x + w)
            y2 = min(img.shape[0]-1, y + h)
            cv2.rectangle(img, (x, y), (x2, y2), color, thickness)
            label = f"#{i+1}"
            cv2.putText(img, label, (x + 4, y + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)

        cv2.imwrite(image_path, img)
    except Exception:
        pass
