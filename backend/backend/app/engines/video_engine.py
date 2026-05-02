import cv2
import os
import numpy as np
from .alignment_engine import align_images
from .rgb_engine import compute_rgb_diff
from .thermal_engine import compute_thermal_diff
from ..engines.anomaly_engine import detect_anomalies
from ..config import VIDEO_FPS


def extract_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # convert BGR to RGB
        frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    cap.release()
    return frames


def write_video(frames, out_path, fps=VIDEO_FPS):
    if len(frames) == 0:
        return
    h, w = frames[0].shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(out_path, fourcc, fps, (w, h))
    for f in frames:
        writer.write(cv2.cvtColor(f.astype('uint8'), cv2.COLOR_RGB2BGR))
    writer.release()


def process_video_pair(vb_path, va_path, tb_path, ta_path, out_video_path):
    frames_b = extract_frames(vb_path)
    frames_a = extract_frames(va_path)

    mode = "rgb"
    if tb_path and ta_path:
        t_b_frames = extract_frames(tb_path)
        t_a_frames = extract_frames(ta_path)
        mode = "hybrid"
    else:
        t_b_frames = t_a_frames = [None] * len(frames_b)

    processed_frames = []
    all_scores = []
    regions_total = 0

    n = min(len(frames_b), len(frames_a))
    # import fusion and scoring locally to avoid circular imports
    from ..services.fusion_service import fuse_maps
    from ..services.scoring_service import compute_scores

    for i in range(n):
        try:
            a_aligned = align_images(frames_b[i], frames_a[i])
            rgb_map, ssim_map = compute_rgb_diff(frames_b[i], a_aligned)
            thermal_map = None
            if mode == "hybrid" and t_b_frames and t_a_frames and i < len(t_b_frames):
                thermal_map = compute_thermal_diff(t_b_frames[i], t_a_frames[i])
            fused = fuse_maps(rgb_map, thermal_map)
            regions, mask = detect_anomalies(fused)
            scores = compute_scores(rgb_map, thermal_map, mask)
            regions_total += len(regions)
            all_scores.append(scores.get("overall", 0.0))

            # create simple visualization (overlay fused heat as red)
            overlay = frames_a[i].copy()
            heat = (fused * 255).astype('uint8')
            heat_color = cv2.applyColorMap(heat, cv2.COLORMAP_JET)
            overlay = cv2.addWeighted(cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR), 0.7, heat_color, 0.3, 0)
            processed_frames.append(cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB))
        except Exception:
            processed_frames.append(frames_a[i])

    write_video(processed_frames, out_video_path)
    avg_score = float(sum(all_scores) / len(all_scores)) if all_scores else 0.0

    return {"mode": mode, "scores": {"overall": avg_score}, "regions_detected": regions_total}
