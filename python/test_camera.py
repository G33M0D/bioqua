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
Test Camera Connection
=======================
Run this to check if your USB microscope is detected.
It will try camera indices 0, 1, and 2 and show which works.

HOW TO RUN:
  python test_camera.py

WHAT YOU SHOULD SEE:
  - A live video window from the microscope
  - "Camera at index X works!" message

IF NOTHING WORKS:
  - Make sure the USB microscope is plugged in
  - Try unplugging and plugging it back in
  - On Windows: check Device Manager for the camera
  - On Mac: check System Preferences → Security → Camera
"""

import sys

try:
    import cv2
except ImportError:
    print("ERROR: OpenCV not installed.")
    print("Run: pip install opencv-python")
    sys.exit(1)


def main():
    print("=" * 50)
    print("  AquaGuard Camera Test")
    print("=" * 50)
    print()
    print("Testing camera indices 0, 1, 2...")
    print()

    working_cameras = []

    for index in range(3):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                h, w = frame.shape[:2]
                print(f"  [+] Camera index {index}: WORKS ({w}x{h})")
                working_cameras.append(index)
            else:
                print(f"  [-] Camera index {index}: Opens but can't read frames")
            cap.release()
        else:
            print(f"  [-] Camera index {index}: Not available")

    print()

    if not working_cameras:
        print("ERROR: No working cameras found!")
        print("  - Is the USB microscope plugged in?")
        print("  - Try unplugging and plugging it back in")
        print("  - On Windows: check Device Manager → Cameras")
        return

    print(f"Found {len(working_cameras)} working camera(s).")
    print()

    # Show live feed from first working camera
    index = working_cameras[0]
    if len(working_cameras) > 1:
        print(f"Showing camera index {index}. Press number keys to switch.")
    print("Press [q] to quit.")
    print()

    cap = cv2.VideoCapture(index)

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Add info overlay
        cv2.putText(frame, f"Camera index: {index} | Press [q] to quit",
                    (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.imshow("AquaGuard Camera Test", frame)

        key = cv2.waitKey(100) & 0xFF
        if key == ord('q'):
            break
        elif key in (ord('0'), ord('1'), ord('2')):
            new_index = key - ord('0')
            if new_index in working_cameras:
                cap.release()
                index = new_index
                cap = cv2.VideoCapture(index)
                print(f"Switched to camera index {index}")

    cap.release()
    cv2.destroyAllWindows()

    print()
    print(f"Set CAMERA_INDEX = {working_cameras[0]} in python/config.py")
    print("(or whichever camera showed the microscope feed)")


if __name__ == "__main__":
    main()
