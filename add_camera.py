#!/usr/bin/env python3
"""Add or update a camera in the project's database.

Usage examples:
  python add_camera.py --id cam_local --name "Local File" --type file --source scripts/sample.mp4 --active
  python add_camera.py --id cam_parking --name "Parking Lot" --type rtsp --source "rtsp://user:pass@192.168.1.100:554/stream1" --active
  python add_camera.py --id cam_webcam --name "Lobby Cam" --type webcam --source 0 --active

Run this from the repository root so imports resolve automatically.
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Ensure repo root is on sys.path so imports like `backend` work when running this script
repo_root = Path(__file__).resolve().parent
sys.path.insert(0, str(repo_root))

from config.settings import Settings
from backend.db.session import create_engine_and_session
from backend.db.models import CameraORM
from sqlalchemy import select


async def _add_camera(camera_id: str, name: str, source_type: str, source_url: str, is_active: bool):
    settings = Settings()
    engine, session_factory = create_engine_and_session(settings)

    async with session_factory() as db:
        stmt = select(CameraORM).where(CameraORM.id == camera_id)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            existing.name = name
            existing.source_type = source_type
            existing.source_url = source_url
            existing.is_active = is_active
            db.add(existing)
            print(f"Updated camera: {camera_id}")
        else:
            cam = CameraORM(
                id=camera_id,
                name=name,
                source_type=source_type,
                source_url=source_url,
                is_active=is_active,
            )
            db.add(cam)
            print(f"Added camera: {camera_id}")

        await db.commit()

    await engine.dispose()


def main():
    parser = argparse.ArgumentParser(description="Add or update camera in DB")
    parser.add_argument("--id", required=True, help="Camera id (unique)")
    parser.add_argument("--name", required=True, help="Camera display name")
    parser.add_argument("--type", choices=("file", "rtsp", "webcam"), default="file")
    parser.add_argument("--source", required=True, help="File path, RTSP URL, or webcam id")
    parser.add_argument("--active", action="store_true", help="Mark camera active")

    args = parser.parse_args()

    # Normalize source to string
    source_url = str(args.source)

    asyncio.run(_add_camera(args.id, args.name, args.type, source_url, args.active))


if __name__ == "__main__":
    main()
