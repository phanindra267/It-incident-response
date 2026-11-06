import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio.v3 as iio

# Ensure slides directory exists
slides_dir = "slides_export"
slide_files = [f"Slide{i}.JPG" for i in range(1, 12)]

for sf in slide_files:
    if not os.path.exists(os.path.join(slides_dir, sf)):
        raise FileNotFoundError(f"Missing slide: {sf}")

print("Found all 11 slide images.")

# Settings
FPS = 24
SECONDS_PER_SLIDE = 5
TRANSITION_FRAMES = 12  # 0.5s smooth crossfade
SLIDE_HOLD_FRAMES = int(FPS * SECONDS_PER_SLIDE) - TRANSITION_FRAMES

TARGET_W = 1280
TARGET_H = 720

output_video_path = "IT_Incident_Response_WarRoom_Presentation.mp4"

def load_and_resize(img_path):
    img = Image.open(img_path).convert("RGB")
    if img.size != (TARGET_W, TARGET_H):
        img = img.resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)
    return np.array(img, dtype=np.uint8)

slide_arrays = [load_and_resize(os.path.join(slides_dir, sf)) for sf in slide_files]

# Slide Titles for Bottom Indicator
slide_labels = [
    "01. Title & Executive Vision",
    "02. Problem: Chaotic War-Rooms",
    "03. Blackboard Architecture",
    "04. Diagnostic Specialists",
    "05. Remediation Specialists",
    "06. Microsoft Semantic Kernel",
    "07. Live Execution Trace",
    "08. Group Add-on: Comms Agent",
    "09. Production Architecture & UI",
    "10. Quantified Business Impact",
    "11. Conclusion & Next Milestones"
]

def add_hud(frame_arr, current_slide_idx, total_slides, progress_in_slide):
    # Convert numpy to PIL
    img = Image.fromarray(frame_arr)
    draw = ImageDraw.Draw(img)
    
    # Bottom HUD background bar
    bar_h = 32
    draw.rectangle([0, TARGET_H - bar_h, TARGET_W, TARGET_H], fill=(10, 15, 29, 220))
    
    # Progress indicator line
    overall_progress = (current_slide_idx + progress_in_slide) / total_slides
    draw.rectangle([0, TARGET_H - 3, int(TARGET_W * overall_progress), TARGET_H], fill=(14, 165, 233))
    
    # HUD Label Text
    label = f"Group 10 War-Room | {slide_labels[current_slide_idx]}  [{current_slide_idx + 1} / {total_slides}]"
    draw.text((16, TARGET_H - 24), label, fill=(200, 215, 235))
    
    # Subtitle watermark
    draw.text((TARGET_W - 250, TARGET_H - 24), "Multi-Agent Blackboard Architecture", fill=(100, 130, 165))
    
    return np.array(img)

print("Encoding animated presentation video...")

frames = []
total_slides = len(slide_arrays)

for i in range(total_slides):
    current_arr = slide_arrays[i]
    next_arr = slide_arrays[(i + 1) % total_slides] if i < total_slides - 1 else None
    
    # Hold slide
    for f in range(SLIDE_HOLD_FRAMES):
        prog = f / (SLIDE_HOLD_FRAMES + TRANSITION_FRAMES)
        frame_with_hud = add_hud(current_arr, i, total_slides, prog)
        frames.append(frame_with_hud)
        
    # Crossfade to next slide (if not last)
    if next_arr is not None:
        for f in range(TRANSITION_FRAMES):
            alpha = (f + 1) / (TRANSITION_FRAMES + 1)
            blended = (current_arr.astype(np.float32) * (1.0 - alpha) + next_arr.astype(np.float32) * alpha).astype(np.uint8)
            prog = (SLIDE_HOLD_FRAMES + f) / (SLIDE_HOLD_FRAMES + TRANSITION_FRAMES)
            frame_with_hud = add_hud(blended, i, total_slides, prog)
            frames.append(frame_with_hud)
    else:
        # Last slide hold extra frames
        for f in range(TRANSITION_FRAMES):
            frame_with_hud = add_hud(current_arr, i, total_slides, 1.0)
            frames.append(frame_with_hud)

# Write video file using imageio ffmpeg writer with H.264 codec
print(f"Total video frames: {len(frames)}. Writing to {output_video_path}...")
import imageio
writer = imageio.get_writer(output_video_path, fps=FPS, codec="libx264", quality=8)
for frame in frames:
    writer.append_data(frame)
writer.close()

file_size = os.path.getsize(output_video_path)
print(f"SUCCESS: Video exported to {output_video_path} ({file_size:,} bytes)")
