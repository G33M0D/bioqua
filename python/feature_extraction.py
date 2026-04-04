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
Feature Extraction Classifier (Option C)
==========================================
This is an alternative to the neural network model.
Instead of a "black box" AI, this script uses transparent,
explainable features to classify bacteria:

  - COLOR: Purple vs Pink pixel ratios (Gram stain detection)
  - SHAPE: Circularity and aspect ratio (morphology detection)

This is the BEST option for science reports because you can
explain exactly what the AI "sees" — no black box.

HOW TO RUN:
  python feature_extraction.py train     Train the classifier
  python feature_extraction.py test      Test on a single image
  python feature_extraction.py explain   Show how features work

WHAT YOU SHOULD SEE:
  - Feature values for each image
  - Classification accuracy
  - A clear explanation of how each feature contributes
"""

import os
import sys
import pickle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import cv2
    import numpy as np
except ImportError:
    print("ERROR: Missing packages. Run: pip install opencv-python numpy scikit-learn")
    sys.exit(1)

from config import *

MODEL_FILE = os.path.join(PROJECT_ROOT, "models", "aquaguard_features_model.pkl")


def extract_features(image):
    """
    Extract measurable features from a microscope image.

    Returns 5 features:
      1. purple_ratio  — How much purple (Gram+) is in the image
      2. pink_ratio    — How much pink (Gram-) is in the image
      3. avg_circularity — How round the bacteria shapes are (1.0 = perfect circle)
      4. avg_aspect_ratio — How elongated the shapes are (1.0 = square, 3.0 = rod)
      5. bacteria_count — How many individual bacteria are detected
    """
    if isinstance(image, str):
        image = cv2.imread(image)
        if image is None:
            return None

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # ── Feature 1 & 2: Color Ratios ──
    # Detect purple pixels (Gram-positive stain)
    purple_mask = cv2.inRange(hsv,
                              np.array(HSV_GRAM_POSITIVE[0]),
                              np.array(HSV_GRAM_POSITIVE[1]))

    # Detect pink pixels (Gram-negative stain)
    pink_mask1 = cv2.inRange(hsv,
                             np.array(HSV_GRAM_NEGATIVE_1[0]),
                             np.array(HSV_GRAM_NEGATIVE_1[1]))
    pink_mask2 = cv2.inRange(hsv,
                             np.array(HSV_GRAM_NEGATIVE_2[0]),
                             np.array(HSV_GRAM_NEGATIVE_2[1]))
    pink_mask = cv2.bitwise_or(pink_mask1, pink_mask2)

    total_pixels = image.shape[0] * image.shape[1]
    purple_ratio = cv2.countNonZero(purple_mask) / total_pixels
    pink_ratio = cv2.countNonZero(pink_mask) / total_pixels

    # ── Features 3, 4, 5: Shape Analysis ──
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
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

        if perimeter > 0 and h > 0:
            circularity = (4 * np.pi * area) / (perimeter ** 2 + 1e-6)
            aspect_ratio = w / h
            circularities.append(circularity)
            aspect_ratios.append(aspect_ratio)

    avg_circularity = np.mean(circularities) if circularities else 0
    avg_aspect_ratio = np.mean(aspect_ratios) if aspect_ratios else 0
    bacteria_count = len(circularities)

    return [purple_ratio, pink_ratio, avg_circularity, avg_aspect_ratio, bacteria_count]


def train_classifier():
    """Train a Random Forest classifier on extracted features."""
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import classification_report, confusion_matrix
    except ImportError:
        print("ERROR: scikit-learn not installed. Run: pip install scikit-learn")
        sys.exit(1)

    data_dir = os.path.join(PROJECT_ROOT, "training_data")
    features = []
    labels = []
    label_names = []

    print("Extracting features from training images...")
    print("-" * 50)

    # Filter to directories only BEFORE enumerating to keep indices aligned
    class_dirs = sorted([d for d in os.listdir(data_dir)
                         if os.path.isdir(os.path.join(data_dir, d))])

    for class_idx, class_name in enumerate(class_dirs):
        class_dir = os.path.join(data_dir, class_name)
        label_names.append(class_name)
        images = [f for f in os.listdir(class_dir)
                  if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]

        print(f"  {class_name}: {len(images)} images", end=" ")

        count = 0
        for img_name in images:
            img_path = os.path.join(class_dir, img_name)
            feat = extract_features(img_path)
            if feat is not None:
                features.append(feat)
                labels.append(class_idx)
                count += 1

        print(f"({count} processed)")

    if not features:
        print("\nERROR: No images found in training_data/")
        return

    X = np.array(features)
    y = np.array(labels)

    print(f"\nTotal samples: {len(X)}")
    print(f"Features per sample: {X.shape[1]}")

    # Split into training and testing
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Train Random Forest
    print("\nTraining Random Forest classifier...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    # Evaluate
    y_pred = clf.predict(X_test)
    accuracy = (y_pred == y_test).mean()

    print(f"\nAccuracy: {accuracy:.1%}")
    print("\nDetailed results:")
    print(classification_report(y_test, y_pred, target_names=label_names))

    # Feature importance
    feature_names = ["Purple Ratio", "Pink Ratio", "Circularity", "Aspect Ratio", "Count"]
    importances = clf.feature_importances_

    print("Feature Importance (how much each feature matters):")
    for name, imp in sorted(zip(feature_names, importances), key=lambda x: -x[1]):
        bar = "#" * int(imp * 50)
        print(f"  {name:16s}: {imp:.3f} {bar}")

    # Save model
    os.makedirs(os.path.dirname(MODEL_FILE), exist_ok=True)
    with open(MODEL_FILE, 'wb') as f:
        pickle.dump({'classifier': clf, 'label_names': label_names}, f)

    print(f"\nModel saved to: {MODEL_FILE}")


def test_image(image_path):
    """Test classification on a single image."""
    if not os.path.exists(MODEL_FILE):
        print("ERROR: No trained model found. Run: python feature_extraction.py train")
        return

    with open(MODEL_FILE, 'rb') as f:
        data = pickle.load(f)
    clf = data['classifier']
    label_names = data['label_names']

    features = extract_features(image_path)
    if features is None:
        print(f"ERROR: Could not read image: {image_path}")
        return

    feature_names = ["Purple Ratio", "Pink Ratio", "Circularity", "Aspect Ratio", "Count"]

    print(f"\nImage: {image_path}")
    print("\nExtracted Features:")
    for name, value in zip(feature_names, features):
        print(f"  {name:16s}: {value:.4f}")

    prediction = clf.predict([features])[0]
    probabilities = clf.predict_proba([features])[0]

    print(f"\nClassification: {label_names[prediction]}")
    print("\nConfidence per class:")
    for name, prob in zip(label_names, probabilities):
        bar = "#" * int(prob * 30)
        print(f"  {name:30s}: {prob:.1%} {bar}")


def explain():
    """Explain how each feature works — great for science reports."""
    print("""
    ============================================================
    HOW AQUAGUARD'S FEATURE EXTRACTION WORKS
    ============================================================

    AquaGuard uses 5 measurable features to classify bacteria.
    Here's what each one means:

    1. PURPLE RATIO (Gram Stain Color)
       ─────────────────────────────────
       What: The percentage of pixels in the image that are purple.
       Why:  Gram-positive bacteria keep the Crystal Violet stain
             and appear PURPLE under the microscope.
       How:  We convert the image to HSV color space and count
             pixels with Hue between 120-160 (purple range).
       High value → Gram-positive bacteria present

    2. PINK RATIO (Gram Stain Color)
       ──────────────────────────────
       What: The percentage of pixels that are pink/red.
       Why:  Gram-negative bacteria lose the Crystal Violet during
             decolorization and pick up Safranin → they appear PINK.
       How:  Count pixels with Hue 0-20 or 160-180 (pink range).
       High value → Gram-negative bacteria present

    3. CIRCULARITY (Shape)
       ─────────────────────
       What: How round the detected shapes are.
             1.0 = perfect circle, 0.0 = very irregular shape.
       Why:  Cocci bacteria are spherical (circularity ~0.7-1.0).
             Bacilli are rod-shaped (circularity ~0.3-0.6).
       How:  Formula: 4 * pi * Area / Perimeter^2
       High value → Cocci (round bacteria)
       Low value  → Bacilli (rod-shaped bacteria)

    4. ASPECT RATIO (Shape)
       ──────────────────────
       What: Width divided by height of the bounding rectangle.
             1.0 = square (equally wide and tall), 3.0 = 3x wider than tall.
       Why:  Cocci have aspect ratio ~1.0 (equally round).
             Bacilli have aspect ratio >2.0 (longer than wide).
       How:  Draw a rectangle around each shape, divide width by height.
       ~1.0  → Cocci (round)
       >2.0  → Bacilli (rod-shaped)

    5. BACTERIA COUNT
       ───────────────
       What: How many individual bacteria shapes are detected.
       Why:  More bacteria = higher contamination.
       How:  Count contours (outlines) larger than a minimum size.
       0     → Clean water (no bacteria visible)
       High  → Contaminated sample

    ============================================================
    PUTTING IT ALL TOGETHER
    ============================================================

    The Random Forest classifier looks at ALL 5 features together
    to make a decision. It's like a panel of 100 experts (trees)
    voting on what type of bacteria they see.

    Example:
      Purple: 0.15, Pink: 0.02, Circ: 0.85, AR: 1.1, Count: 23
      → High purple + high circularity = Gram-positive Cocci

      Purple: 0.01, Pink: 0.12, Circ: 0.35, AR: 2.8, Count: 15
      → High pink + low circularity + high AR = Gram-negative Bacilli

    ============================================================
    """)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python feature_extraction.py train          Train the classifier")
        print("  python feature_extraction.py test <image>   Test on an image")
        print("  python feature_extraction.py explain        Explain how it works")
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == "train":
        train_classifier()
    elif command == "test" and len(sys.argv) >= 3:
        test_image(sys.argv[2])
    elif command == "explain":
        explain()
    else:
        print(f"Unknown command: {command}")
        print("Use: train, test <image>, or explain")
