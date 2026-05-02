from typing import Optional
import numpy as np
from ..config import DEFAULT_FUSION_WEIGHT_RGB, DEFAULT_FUSION_WEIGHT_THERMAL


def fuse_maps(rgb_map: np.ndarray, thermal_map: Optional[np.ndarray],
              rgb_weight: float = DEFAULT_FUSION_WEIGHT_RGB,
              thermal_weight: float = DEFAULT_FUSION_WEIGHT_THERMAL) -> np.ndarray:
    if thermal_map is None:
        return rgb_map.astype(float)

    # Ensure both maps are same size
    if rgb_map.shape != thermal_map.shape:
        from skimage.transform import resize

        thermal_map = resize(thermal_map, rgb_map.shape, preserve_range=True)

    fused = rgb_weight * rgb_map.astype(float) + thermal_weight * thermal_map.astype(float)
    fused = fused / fused.max() if fused.max() > 0 else fused
    return fused
