from fastapi import UploadFile
from typing import Optional
import uuid
from ..services.pipeline_service import run_image_pipeline
from ..utils.file_manager import save_upload_file
from ..config import UPLOAD_DIR
import os


async def analyze_image(
    rgb_before: UploadFile,
    rgb_after: UploadFile,
    thermal_before: Optional[UploadFile] = None,
    thermal_after: Optional[UploadFile] = None,
):
    uid = str(uuid.uuid4())
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    rb_path = save_upload_file(rgb_before, f"{uid}_rgb_before")
    ra_path = save_upload_file(rgb_after, f"{uid}_rgb_after")
    tb_path = None
    ta_path = None
    if thermal_before:
        tb_path = save_upload_file(thermal_before, f"{uid}_thermal_before")
    if thermal_after:
        ta_path = save_upload_file(thermal_after, f"{uid}_thermal_after")

    result = await run_image_pipeline(rb_path, ra_path, tb_path, ta_path, uid)
    # convert absolute output paths to URLs relative to mounted '/outputs' and '/uploads'
    def to_url(path: str):
        if not path:
            return path
        try:
            # find outputs/ or uploads/ in path
            p = str(path).replace('\\', '/')
            idx = p.rfind('/outputs/')
            if idx != -1:
                return f"/outputs/{p[idx+9:]}"
            idx = p.rfind('/uploads/')
            if idx != -1:
                return f"/uploads/{p[idx+9:]}"
        except Exception:
            pass
        return path

    out = result.get('output', {})
    # overlay, heatmap, and difference map
    for k in ['overlay_image', 'heatmap_image', 'difference_map']:
        if out.get(k):
            out[k] = to_url(out[k])
    # regions list
    if out.get('regions'):
        out['regions'] = [to_url(p) for p in out['regions']]

    result['output'] = out
    return result
