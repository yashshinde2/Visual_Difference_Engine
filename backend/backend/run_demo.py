import asyncio
import numpy as np
import cv2
import os
from pathlib import Path

from app.services.pipeline_service import run_image_pipeline


def make_demo_images(base_dir: Path):
    base_dir.mkdir(parents=True, exist_ok=True)
    before = np.zeros((300, 300, 3), dtype='uint8')
    after = before.copy()
    # draw a white square in after image
    cv2.rectangle(after, (80, 80), (220, 220), (255, 255, 255), -1)

    b_path = str(base_dir / "rgb_before.png")
    a_path = str(base_dir / "rgb_after.png")
    cv2.imwrite(b_path, cv2.cvtColor(before, cv2.COLOR_RGB2BGR))
    cv2.imwrite(a_path, cv2.cvtColor(after, cv2.COLOR_RGB2BGR))
    return b_path, a_path


async def main():
    tmp = Path("./demo_tmp")
    b, a = make_demo_images(tmp)
    analysis_id = "demo"
    result = await run_image_pipeline(b, a, None, None, analysis_id)
    print("Pipeline result:")
    print(result)
    print("Outputs:")
    for k, v in result.get('output', {}).items():
        print(f" - {k}: {v}")


if __name__ == '__main__':
    asyncio.run(main())
