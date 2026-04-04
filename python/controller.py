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
AquaGuard Controller — The Brain
=================================
This is the main script that runs on your laptop. It:
  1. Connects to the Arduino via USB serial
  2. Reads pH and EC sensor data from Arduino
  3. Captures images from the USB microscope
  4. Runs the AI model to classify bacteria
  5. Calculates a risk level (LOW / MODERATE / HIGH)
  6. Sends the result back to the Arduino LCD
  7. Shows a live video feed with overlay on your laptop

HOW TO RUN:
  python controller.py

WHAT YOU SHOULD SEE:
  - A video window showing the microscope feed
  - Sensor readings + bacteria classification in the terminal
  - Results displayed on the Arduino LCD

KEYBOARD CONTROLS:
  q = Quit
  s = Start staining sequence
  c = Capture a single image
  r = Generate PDF report (if enabled)
  l = Open learning modules (if enabled)
"""

import sys
import os
import time
import signal

# Add project root to path so we can import config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import cv2
    import numpy as np
except ImportError:
    print("ERROR: Missing required packages.")
    print("Run this command to install them:")
    print("  pip install opencv-python numpy tensorflow pyserial")
    sys.exit(1)

from config import *


def load_model():
    """Load the trained AI model."""
    if not os.path.exists(AI_MODEL_PATH):
        print(f"WARNING: No AI model found at {AI_MODEL_PATH}")
        print("The system will run without AI classification.")
        print("To train a model:")
        print("  1. Collect images using: python capture_images.py")
        print("  2. Train the model using: python train_model.py")
        print("  OR use Google Teachable Machine and export the model.")
        return None

    try:
        import json
        from tensorflow.keras.models import load_model as keras_load
        model = keras_load(AI_MODEL_PATH, compile=False)
        print(f"AI model loaded from {AI_MODEL_PATH}")

        # Load saved class mapping if available (from train_model.py)
        class_map_path = AI_MODEL_PATH.replace('.h5', '_classes.json')
        if os.path.exists(class_map_path):
            with open(class_map_path) as f:
                idx_to_class = json.load(f)
            # Update CLASS_NAMES to match training order
            global CLASS_NAMES
            CLASS_NAMES = [idx_to_class[str(i)] for i in range(len(idx_to_class))]
            # Convert folder names to display names
            CLASS_NAMES = [n.replace("gram_negative_", "Gram- ").replace("gram_positive_", "Gram+ ")
                           .replace("_", " ").title().replace("No Bacteria", "No Bacteria")
                           for n in CLASS_NAMES]
            print(f"  Class mapping loaded: {CLASS_NAMES}")

        return model
    except Exception as e:
        print(f"WARNING: Could not load AI model: {e}")
        return None


def connect_arduino():
    """Connect to the Arduino via serial port."""
    try:
        import serial
        arduino = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=0.1)
        time.sleep(2)  # Wait for Arduino to reset after connection
        print(f"Arduino connected on {SERIAL_PORT}")

        # Wait for ready signal
        for _ in range(10):
            line = arduino.readline().decode('utf-8', errors='ignore').strip()
            if line == "AQUAGUARD_READY":
                print("Arduino is ready!")
                return arduino
            elif line:
                print(f"  Arduino: {line}")

        print("Arduino connected (no ready signal received)")
        return arduino
    except ImportError:
        print("WARNING: pyserial not installed. Run: pip install pyserial")
        print("Running in camera-only mode (no Arduino).")
        return None
    except Exception as e:
        print(f"WARNING: Could not connect to Arduino on {SERIAL_PORT}: {e}")
        print("Running in camera-only mode.")
        print("TIP: Check your serial port in config.py (SERIAL_PORT setting)")
        return None


def connect_camera():
    """Connect to the USB microscope camera."""
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f"ERROR: Could not open camera at index {CAMERA_INDEX}")
        print("TIP: Try changing CAMERA_INDEX in config.py (0, 1, or 2)")
        print("TIP: Run 'python test_camera.py' to find the right index")
        return None

    print(f"Camera connected (index {CAMERA_INDEX})")
    return cap


# Track whether we have real hardware
_has_arduino = False


def classify_image(model, frame):
    """Run the AI model on a microscope image."""
    if model is None:
        return "No Model", 0.0

    # Resize to what the model expects (224x224 for Teachable Machine)
    img = cv2.resize(frame, AI_IMAGE_SIZE)
    img_array = np.expand_dims(img / 255.0, axis=0).astype(np.float32)

    # Predict
    predictions = model.predict(img_array, verbose=0)
    class_idx = np.argmax(predictions[0])
    confidence = float(predictions[0][class_idx])

    if confidence < AI_CONFIDENCE_THRESHOLD:
        return "Uncertain", confidence

    if class_idx >= len(CLASS_NAMES):
        print(f"WARNING: Model output class {class_idx} but only {len(CLASS_NAMES)} classes defined.")
        print("  Your model may have more classes than CLASS_NAMES in config.py.")
        return f"Unknown (class {class_idx})", confidence

    return CLASS_NAMES[class_idx], confidence


def classify_with_hsv(frame):
    """
    Fallback classification using HSV color thresholding.
    Use this if no AI model is available.
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Detect purple (Gram-positive)
    mask_pos = cv2.inRange(hsv,
                           np.array(HSV_GRAM_POSITIVE[0]),
                           np.array(HSV_GRAM_POSITIVE[1]))

    # Detect pink (Gram-negative)
    mask_neg1 = cv2.inRange(hsv,
                            np.array(HSV_GRAM_NEGATIVE_1[0]),
                            np.array(HSV_GRAM_NEGATIVE_1[1]))
    mask_neg2 = cv2.inRange(hsv,
                            np.array(HSV_GRAM_NEGATIVE_2[0]),
                            np.array(HSV_GRAM_NEGATIVE_2[1]))
    mask_neg = cv2.bitwise_or(mask_neg1, mask_neg2)

    purple_count = cv2.countNonZero(mask_pos)
    pink_count = cv2.countNonZero(mask_neg)

    total_pixels = frame.shape[0] * frame.shape[1]
    purple_ratio = purple_count / total_pixels
    pink_ratio = pink_count / total_pixels

    # Determine Gram type
    if purple_ratio < 0.01 and pink_ratio < 0.01:
        gram = "No Bacteria"
    elif purple_ratio > pink_ratio:
        gram = "Gram+"
    else:
        gram = "Gram-"

    # Detect shapes using contours
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 0, 255,
                              cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)

    circularities = []
    aspect_ratios = []

    for c in contours:
        area = cv2.contourArea(c)
        if area < MIN_CONTOUR_AREA:
            continue
        perimeter = cv2.arcLength(c, True)
        x, y, w, h = cv2.boundingRect(c)
        if perimeter > 1 and h > 0:
            circularities.append((4 * 3.14159 * area) / (perimeter ** 2 + 1e-6))
            aspect_ratios.append(w / h)

    # Determine shape
    if not circularities:
        shape = ""
    else:
        avg_circ = sum(circularities) / len(circularities)
        avg_ar = sum(aspect_ratios) / len(aspect_ratios)
        if avg_circ > CIRCULARITY_COCCI:
            shape = "Cocci"
        elif avg_ar > ASPECT_RATIO_BACILLI or avg_ar < (1 / ASPECT_RATIO_BACILLI):
            shape = "Bacilli"
        else:
            shape = "Spirilla"

    if gram == "No Bacteria":
        return "No Bacteria", max(purple_ratio, pink_ratio)

    result = f"{gram} {shape}" if shape else gram
    confidence = max(purple_ratio, pink_ratio)
    return result, confidence


def calculate_risk(ph, ec, bacteria_class):
    """
    Combine sensor readings + bacteria classification into a risk level.

    Risk Levels:
      HIGH     = Gram-negative detected OR extreme pH
      MODERATE = Any bacteria detected OR pH/EC slightly off
      LOW      = Clean water, normal readings
    """
    # Extreme pH = always high risk (wider margin than normal range)
    extreme_low = PH_NORMAL_MIN - 1.5   # 5.0 by default
    extreme_high = PH_NORMAL_MAX + 0.5  # 9.0 by default
    if ph < extreme_low or ph > extreme_high:
        return "HIGH"

    # Gram-negative bacteria = potential pathogens
    if "Gram-" in bacteria_class:
        return "HIGH"

    # Slightly abnormal pH or EC
    if ph < PH_NORMAL_MIN or ph > PH_NORMAL_MAX:
        return "MODERATE"
    if ec > EC_NORMAL_MAX:
        return "MODERATE"

    # Any bacteria present
    if bacteria_class != "No Bacteria" and bacteria_class != "No Model" and bacteria_class != "Uncertain":
        return "MODERATE"

    return "LOW"


def read_arduino_sensors(arduino):
    """Read pH and EC values from Arduino serial output."""
    if arduino is None:
        return 7.0, 500.0  # Demo defaults when no Arduino (UI shows warning)

    try:
        line = arduino.readline().decode('utf-8', errors='ignore').strip()
        if not line:
            return None, None

        # Handle Arduino status messages — staining state synchronization
        if line == "STAINING_START":
            print("  Arduino: Staining sequence started")
            return "STAINING_START", None
        elif line == "STAINING_DONE":
            print("  Arduino: Staining complete — ready for classification")
            return "STAINING_DONE", None
        elif line.startswith(("STEP:", "STAINING", "AQUAGUARD", "STATUS:")):
            print(f"  Arduino: {line}")
            return None, None

        # Only parse sensor CSV if line contains comma
        if ',' not in line:
            return None, None

        parts = line.split(',')
        ph = float(parts[0])
        ec = float(parts[1])
        return ph, ec
    except (ValueError, IndexError):
        return None, None


def main():
    """Main control loop."""
    print("=" * 60)
    print("  AquaGuard: AI-Powered Bacteria Detection")
    print("  Original Author: Guillanne Marie Agreda")
    print("=" * 60)
    print()

    # Connect to hardware
    global _has_arduino
    model = load_model()
    arduino = connect_arduino()
    _has_arduino = arduino is not None
    camera = connect_camera()

    if camera is None:
        print("\nCannot continue without a camera. Exiting.")
        sys.exit(1)

    # Initialize optional features
    data_logger = None
    if FEATURE_DATA_LOGGING:
        try:
            from data_logger import DataLogger
            data_logger = DataLogger()
            print("Data logging ENABLED")
        except ImportError:
            print("WARNING: data_logger.py not found, logging disabled")

    # Note: FEATURE_MODULAR_SENSORS is reserved for future use.
    # When enabled, additional sensors (temperature, turbidity) will be
    # read and included in risk scoring. For now, core pH/EC sensors
    # are read directly from the Arduino serial stream.

    print()
    print("Controls: [q]uit  [s]tart staining  [c]apture image  [r]eport")
    print("-" * 60)

    # Track latest sensor readings and last sent result (avoid flooding)
    last_ph = 7.0
    last_ec = 500.0
    last_sent_result = ""
    staining_in_progress = False  # Pause classification during staining

    try:
        while True:
            # Read sensors from Arduino
            if arduino:
                ph, ec = read_arduino_sensors(arduino)
                if ph == "STAINING_START":
                    staining_in_progress = True
                    continue
                elif ph == "STAINING_DONE":
                    staining_in_progress = False
                    last_sent_result = ""  # Reset so result is always sent after staining
                    # Don't continue — let it proceed to classify the stained slide
                    ph = last_ph  # Restore float value to prevent TypeError downstream
                    ec = last_ec
                elif ph is not None:
                    last_ph = ph
                    last_ec = ec

            # Capture microscope frame
            ret, frame = camera.read()
            if not ret:
                continue

            # Skip classification while staining is in progress
            if staining_in_progress:
                display_frame = frame.copy()
                cv2.rectangle(display_frame, (0, 0), (display_frame.shape[1], 40), (0, 0, 0), -1)
                cv2.putText(display_frame, "Staining in progress... please wait",
                            (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)
                cv2.imshow("AquaGuard - Live Feed", display_frame)
                cv2.waitKey(1000)
                continue

            # Classify bacteria
            if model is not None:
                bacteria_class, confidence = classify_image(model, frame)
            else:
                bacteria_class, confidence = classify_with_hsv(frame)

            # Calculate risk
            risk = calculate_risk(last_ph, last_ec, bacteria_class)

            # Display on laptop screen
            display_frame = frame.copy()

            # Color-coded risk bar
            risk_colors = {"LOW": (0, 200, 0), "MODERATE": (0, 165, 255), "HIGH": (0, 0, 255)}
            color = risk_colors.get(risk, (255, 255, 255))

            bar_height = 50 if not _has_arduino else 40
            cv2.rectangle(display_frame, (0, 0), (display_frame.shape[1], bar_height), (0, 0, 0), -1)
            cv2.putText(display_frame,
                        f"{bacteria_class} ({confidence:.0%}) | Risk: {risk} | pH:{last_ph:.1f} EC:{last_ec:.0f}",
                        (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            if not _has_arduino:
                cv2.putText(display_frame, "NO SENSOR — demo mode (values are defaults)",
                            (10, 46), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

            cv2.imshow("AquaGuard - Live Feed", display_frame)

            # Check if classification result changed
            current_result = f"{bacteria_class},{risk}"
            result_changed = (current_result != last_sent_result)

            # Log data BEFORE updating last_sent_result (so the check works)
            if data_logger and result_changed and bacteria_class not in ("No Model",):
                data_logger.log(last_ph, last_ec, bacteria_class, confidence, risk, frame)

            # Send result to Arduino LCD (only when it changes, to avoid flooding)
            if arduino and result_changed and bacteria_class not in ("No Model", "Uncertain"):
                try:
                    arduino.write(f"RESULT:{current_result}\n".encode())
                except Exception:
                    pass

            # Update last sent result after both logging and sending
            if result_changed:
                last_sent_result = current_result

            # Handle keyboard input
            key = cv2.waitKey(100) & 0xFF  # 100ms between frames for responsive UI

            if key == ord('q'):
                print("\nShutting down AquaGuard...")
                break
            elif key == ord('s'):
                # Send start staining command to Arduino
                if arduino:
                    print("\nStarting Gram stain sequence...")
                    arduino.write(b"START\n")
                else:
                    print("\nNo Arduino connected — cannot start staining")
            elif key == ord('c'):
                # Capture and save current image
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"capture_{timestamp}.jpg"
                save_dir = os.path.join(PROJECT_ROOT, "results", "images")
                os.makedirs(save_dir, exist_ok=True)
                filepath = os.path.join(save_dir, filename)
                if cv2.imwrite(filepath, frame):
                    print(f"\nImage saved: {filepath}")
                else:
                    print(f"\nERROR: Failed to save image to {filepath}")
            elif key == ord('r'):
                if FEATURE_PDF_REPORTS:
                    try:
                        from generate_report import generate_report
                        generate_report()
                    except ImportError:
                        print("\ngenerate_report.py not found")
                else:
                    print("\nPDF reports disabled. Set FEATURE_PDF_REPORTS = True in config.py")
            elif key == ord('l'):
                if FEATURE_LEARNING_MODULES:
                    print("\nLearning modules (run from the aquaguard/ folder):")
                    print("  1. python learning/learn_gram_staining.py")
                    print("  2. python learning/learn_bacteria_shapes.py")
                    print("  3. python learning/learn_how_ai_works.py")
                    print("  4. python learning/learn_water_quality.py")
                    print("  5. python learning/learn_risk_assessment.py")
                else:
                    print("\nLearning modules disabled. Set FEATURE_LEARNING_MODULES = True in config.py")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    finally:
        # Clean up
        if camera:
            camera.release()
        cv2.destroyAllWindows()
        if arduino:
            arduino.close()
        print("AquaGuard shut down. Goodbye!")


if __name__ == "__main__":
    main()
