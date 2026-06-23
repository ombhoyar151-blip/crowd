"""Generate a synthetic crowd test video using OpenCV."""
import cv2
import numpy as np
import random
import os

OUTPUT = "scripts/sample.mp4"
FPS = 25
FRAMES = 375  # 15 seconds
W, H = 1280, 720

random.seed(42)
out = cv2.VideoWriter(OUTPUT, cv2.VideoWriter_fourcc(*"mp4v"), FPS, (W, H))

# 8 simulated "people" — tall moving rectangles with heads
people = [
    {
        "x": float(random.randint(80, 600)),
        "y": float(random.randint(150, 500)),
        "vx": float(random.choice([-1, 1]) * random.randint(3, 6)),
        "vy": float(random.choice([-1, 1]) * random.randint(1, 3)),
        "color": (
            random.randint(160, 230),
            random.randint(160, 220),
            random.randint(200, 255),
        ),
    }
    for _ in range(8)
]

for frame_num in range(FRAMES):
    frame = np.full((H, W, 3), (18, 18, 28), dtype=np.uint8)

    # Grid background
    for x in range(0, W, 120):
        cv2.line(frame, (x, 0), (x, H), (35, 35, 48), 1)
    for y in range(0, H, 80):
        cv2.line(frame, (0, y), (W, y), (35, 35, 48), 1)

    # Frame counter text
    cv2.putText(
        frame,
        f"Frame: {frame_num:04d}  Synthetic Crowd Test",
        (20, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (100, 100, 120),
        1,
    )

    for p in people:
        # Update
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        # Bounce off walls
        if p["x"] < 30 or p["x"] > W - 80:
            p["vx"] *= -1
        if p["y"] < 80 or p["y"] > H - 120:
            p["vy"] *= -1

        x, y = int(p["x"]), int(p["y"])
        c = p["color"]

        # Body (torso)
        cv2.rectangle(frame, (x, y), (x + 36, y + 70), c, -1)
        # Head
        cv2.circle(frame, (x + 18, y - 18), 16, (220, 195, 170), -1)
        # Shadow
        cv2.ellipse(
            frame,
            (x + 18, y + 72),
            (20, 6),
            0,
            0,
            360,
            (10, 10, 15),
            -1,
        )

    out.write(frame)

out.release()
size_kb = os.path.getsize(OUTPUT) / 1024
print(f"Created {OUTPUT}: {FRAMES} frames @ {FPS}fps = {FRAMES/FPS:.0f}s, {size_kb:.0f} KB")
