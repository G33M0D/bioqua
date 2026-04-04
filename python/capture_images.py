# ============================================================
# AquaGuard: AI-Powered Bacteria Detection for Safe Drinking Water
#
# Original Author : Guillanne Marie Agreda
# Year            : 2026
# License         : MIT License
#
# This project is the original work of the author.
# Unauthorized removal of this notice is prohibited.
# ============================================================

"""
Capture Training Images
========================
This script helps you collect bacteria images for training the AI.
It shows a live feed from the microscope and lets you save images
into the correct training folders with a single key press.

HOW TO RUN:
  python capture_images.py

KEYBOARD CONTROLS:
  1 = Save as Gram+ Cocci
  2 = Save as Gram+ Bacilli
  3 = Save as Gram- Cocci
  4 = Save as Gram- Bacilli
  5 = Save as No Bacteria (empty/clean field)
  q = Quit

WHAT YOU SHOULD SEE:
  - A live video window from the microscope
  - The current count of images per class
  - A "Saved!" message when you press a number key
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import cv2
except ImportError:
    print("ERROR: OpenCV not installed. Run: pip install opencv-python")
    sys.exit(1)

from config import CAMERA_INDEX, PROJECT_ROOT

# Training classes and their keyboard shortcuts
CLASSES = {
    ord('1'): "gram_positive_cocci",
    ord('2'): "gram_positive_bacilli",
    ord('3'): "gram_negative_cocci",
    ord('4'): "gram_negative_bacilli",
    ord('5'): "no_bacteria",
}

CLASS_LABELS = {
    "gram_positive_cocci": "Gram+ Cocci (purple, round)",
    "gram_positive_bacilli": "Gram+ Bacilli (purple, rod)",
    "gram_negative_cocci": "Gram- Cocci (pink, round)",
    "gram_negative_bacilli": "Gram- Bacilli (pink, rod)",
    "no_bacteria": "No Bacteria (empty field)",
}


def count_images(class_dir):
    """Count how many images are in a folder."""
    if not os.path.exists(class_dir):
        return 0
    return len([f for f in os.listdir(class_dir)
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))])


def main():
    print("=" * 60)
    print("  AquaGuard Image Capture Tool")
    print("  Original Author: Guillanne Marie Agreda")
    print("=" * 60)
    print()

    data_dir = os.path.join(PROJECT_ROOT, "training_data")

    # Show current counts
    print("Current image counts:")
    for key_code, class_name in sorted(CLASSES.items()):
        class_dir = os.path.join(data_dir, class_name)
        count = count_images(class_dir)
        label = CLASS_LABELS[class_name]
        key = chr(key_code)
        status = "OK" if count >= 30 else f"need {30 - count} more"
        print(f"  [{key}] {label}: {count} ({status})")

    print()
    print("Press the number key to save the current frame to that class.")
    print("Press [q] to quit.")
    print("-" * 60)

    # Open camera
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f"ERROR: Could not open camera at index {CAMERA_INDEX}")
        print("TIP: Change CAMERA_INDEX in config.py")
        sys.exit(1)

    saved_message = ""
    saved_time = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Create display frame with instructions
        display = frame.copy()
        h, w = display.shape[:2]

        # Draw instruction bar at bottom
        cv2.rectangle(display, (0, h - 100), (w, h), (0, 0, 0), -1)

        y = h - 80
        for key_code, class_name in sorted(CLASSES.items()):
            key = chr(key_code)
            count = count_images(os.path.join(data_dir, class_name))
            short_name = class_name.replace("gram_positive_", "G+").replace("gram_negative_", "G-").replace("no_bacteria", "Empty")
            cv2.putText(display, f"[{key}] {short_name}: {count}",
                        (10 + (key_code - ord('1')) * (w // 5), y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

        cv2.putText(display, "[q] Quit", (10, h - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 255), 1)

        # Show saved message briefly
        if saved_message and (time.time() - saved_time) < 2:
            cv2.putText(display, saved_message, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow("AquaGuard - Capture Training Images", display)

        key = cv2.waitKey(100) & 0xFF

        if key == ord('q'):
            break
        elif key in CLASSES:
            class_name = CLASSES[key]
            class_dir = os.path.join(data_dir, class_name)
            os.makedirs(class_dir, exist_ok=True)

            # Save with timestamp filename
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            count = count_images(class_dir)
            filename = f"{class_name}_{timestamp}_{count + 1:04d}.jpg"
            filepath = os.path.join(class_dir, filename)
            cv2.imwrite(filepath, frame)

            saved_message = f"Saved to {class_name}/ ({count + 1} total)"
            saved_time = time.time()
            print(f"  Saved: {filepath}")

    cap.release()
    cv2.destroyAllWindows()

    # Print final summary
    print()
    print("Final image counts:")
    for key_code, class_name in sorted(CLASSES.items()):
        count = count_images(os.path.join(data_dir, class_name))
        print(f"  {CLASS_LABELS[class_name]}: {count}")

    print()
    print("Next step: Train your model with:")
    print("  python train_model.py")


if __name__ == "__main__":
    main()
