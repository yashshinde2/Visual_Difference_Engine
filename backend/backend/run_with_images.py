import asyncio
import sys
from pathlib import Path

from app.services.pipeline_service import run_image_pipeline


async def main():
    if len(sys.argv) < 3:
        print("Usage: run_with_images.py rgb_before rgb_after [thermal_before thermal_after]")
        raise SystemExit(1)
    rgb_before = sys.argv[1]
    rgb_after = sys.argv[2]
    t_before = sys.argv[3] if len(sys.argv) > 3 else None
    t_after = sys.argv[4] if len(sys.argv) > 4 else None

    result = await run_image_pipeline(rgb_before, rgb_after, t_before, t_after, "user_run")
    print("Pipeline result:")
    print(result)
    print("Outputs:")
    for k, v in result.get('output', {}).items():
        print(f" - {k}: {v}")


if __name__ == '__main__':
    asyncio.run(main())
