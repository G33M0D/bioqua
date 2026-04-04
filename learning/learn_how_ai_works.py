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
Learning Module 3: How AI Works in AquaGuard
Explains HSV color thresholding, contour analysis, transfer learning,
and neural networks in plain English with analogies.
"""

import os
import sys


def print_header(title):
    width = 60
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width + "\n")


def print_subheader(title):
    print(f"\n--- {title} ---\n")


def pause():
    input("  [Press Enter to continue...]\n")


def introduction():
    print_header("HOW AI DETECTS BACTERIA IN WATER")

    print("""  AquaGuard uses Artificial Intelligence (AI) to look at
  microscope images of water samples and detect bacteria.

  But how does a computer "see" bacteria? It can't squint at
  a microscope like a scientist can. Instead, it uses MATH
  and PATTERNS. Let's break it down into four key techniques:

      1. HSV Color Thresholding  -- finding the right colors
      2. Contour Analysis        -- finding shapes and edges
      3. Neural Networks         -- how AI "thinks"
      4. Transfer Learning       -- teaching AI new tricks fast

  Don't worry if these sound complicated. We'll use everyday
  analogies to make them crystal clear!
""")
    pause()


def hsv_section():
    print_header("TECHNIQUE 1: HSV Color Thresholding")

    print_subheader("The M&M Analogy")
    print("""  Imagine you have a big bowl of M&Ms and you want to pick
  out ONLY the red ones. How would you do it?

  You'd look at each M&M and ask: "Is this red?"
  - If YES -> keep it
  - If NO  -> toss it aside

  That's EXACTLY what HSV color thresholding does with pixels
  in an image!

  WHAT IS HSV?

  Computers usually see color as RGB (Red, Green, Blue).
  But HSV is often more useful:

      H = HUE         (What color is it? Red? Blue? Purple?)
      S = SATURATION   (How vivid is the color? Bright or pale?)
      V = VALUE        (How bright or dark is it?)

       H: 0----60---120---180---240---300---360
          RED  YELLOW GREEN CYAN  BLUE MAGENTA RED

  Think of it like a color wheel:

            Red (0)
           /        \\
      Magenta       Yellow (60)
      (300)  |       |
       Blue  |       | Green
      (240)  \\      / (120)
            Cyan (180)

  HOW AQUAGUARD USES IT:

  After Gram staining, bacteria appear as PURPLE or PINK
  blobs against a lighter background. AquaGuard converts the
  image to HSV and says:

      "Keep only pixels where H is between 120-170 (purple
       range) and S is above 50 (not too pale)."

  Everything else becomes black (ignored). Now only the
  bacteria remain visible!

      ORIGINAL IMAGE         AFTER THRESHOLDING
      +--------------+       +--------------+
      |  ..@@..##..  |       |  ..@@........|
      | ...@@@@..##. |  -->  | ...@@@@......|
      |  ..@@..##..  |       |  ..@@........|
      +--------------+       +--------------+
      @@ = bacteria (purple)  ## = noise (removed!)
""")
    pause()


def contour_section():
    print_header("TECHNIQUE 2: Contour Analysis")

    print_subheader("Drawing Outlines Around Shapes")
    print("""  After thresholding removes the background, we're left with
  white blobs on a black background. But how does the computer
  know where each bacterium starts and ends?

  It uses CONTOUR DETECTION -- basically drawing an outline
  around each white blob.

  Think of it like a coloring book:

      BEFORE (blobs)           AFTER (contours found)
      +--------------+         +--------------+
      |              |         |              |
      |   ***  **    |         |  +---+ +--+  |
      |   ***  **    |  --->   |  |   | |  |  |
      |              |         |  +---+ +--+  |
      |     ****     |         |    +----+    |
      |     ****     |         |    |    |    |
      +--------------+         |    +----+    |
                               +--------------+

  Each outlined shape is a CONTOUR. For each contour, the
  computer can measure:

      +------------------------------------------+
      | MEASUREMENT     | WHAT IT TELLS US       |
      +------------------------------------------+
      | Area            | How big is the blob?   |
      | Perimeter       | How long is the edge?  |
      | Circularity     | Is it round or long?   |
      | Aspect ratio    | Width vs height        |
      | Solidity        | Filled or irregular?   |
      +------------------------------------------+

  These measurements help classify bacteria:

      Round + small area  -> probably COCCI
      Long + narrow       -> probably BACILLI
      Curved + thin       -> probably SPIRILLA

  It's like the computer is playing a shape-matching game!
""")
    pause()


def neural_network_section():
    print_header("TECHNIQUE 3: Neural Networks (How AI 'Thinks')")

    print_subheader("The Brain Analogy")
    print("""  Your brain has about 86 BILLION neurons connected together.
  When you see a cat, millions of neurons fire in a pattern
  that your brain has learned means "cat."

  A neural network is a simplified version of this, built in
  software. It has layers of artificial "neurons":

      INPUT        HIDDEN LAYERS        OUTPUT
      LAYER        (the thinking)       LAYER

      [pixel 1] --\\                  /-- [coccus: 85%]
      [pixel 2] ---[O]--[O]--[O]---+-- [bacillus: 10%]
      [pixel 3] ---[O]--[O]--[O]---+-- [spirillum: 3%]
      [pixel 4] --/  [O]--[O]--[O]  \\-- [no bacteria: 2%]
        ...         ...  ...  ...

  HOW IT LEARNS:

  1. SHOW it thousands of labeled images:
     "This is a coccus" "This is a bacillus" etc.

  2. It makes a GUESS for each image.

  3. If the guess is WRONG, it adjusts its connections
     slightly (like tuning a radio dial).

  4. After seeing thousands of examples, it gets VERY GOOD
     at guessing correctly!

  SIMPLE EXAMPLE -- Learning to detect "round":

      Training:                    After training:
      Show: OO  Label: "round"    New image: OO
      Show: || Label: "not round" AI says: "round" (95%)
      Show: OO  Label: "round"
      Show: ~~ Label: "not round"  New image: ~~
      (repeat 1000x)              AI says: "not round" (97%)

  The network doesn't follow rules WE wrote. It DISCOVERS
  its own rules from examples. That's what makes AI powerful!
""")
    pause()


def transfer_learning_section():
    print_header("TECHNIQUE 4: Transfer Learning")

    print_subheader("Teaching a Dog New Tricks (Faster)")
    print("""  Training a neural network from scratch takes:
      - Millions of images
      - Days or weeks of computing time
      - Expensive hardware (GPUs)

  That's a LOT of work for a school project! Luckily, there's
  a shortcut called TRANSFER LEARNING.

  THE ANALOGY:

  Imagine you have a dog that already knows how to:
      - Sit
      - Stay
      - Recognize hand signals

  Now you want to teach it to fetch a specific toy.
  Do you start from scratch? NO! The dog already understands
  basic commands and signals. You just build on top of what
  it already knows.

  Transfer learning works the same way:

      +----------------------------------------------+
      |  Step 1: Take a PRE-TRAINED model            |
      |  (like MobileNet, trained on millions of     |
      |   everyday images -- cars, dogs, flowers)    |
      |                                              |
      |  This model already knows:                   |
      |  - How to detect edges                       |
      |  - How to recognize shapes                   |
      |  - How to identify textures                  |
      |  - How to see color patterns                 |
      +----------------------------------------------+
              |
              v
      +----------------------------------------------+
      |  Step 2: FREEZE the early layers             |
      |  (keep the basic knowledge it already has)   |
      +----------------------------------------------+
              |
              v
      +----------------------------------------------+
      |  Step 3: RETRAIN only the last few layers    |
      |  with YOUR bacteria images                   |
      |                                              |
      |  "Instead of 'dog' or 'car', now learn       |
      |   'coccus', 'bacillus', 'spirillum'"         |
      +----------------------------------------------+
              |
              v
      +----------------------------------------------+
      |  Result: A bacteria detector that works with |
      |  only hundreds of images instead of millions! |
      +----------------------------------------------+

  This is how AquaGuard can be accurate with a relatively
  small training dataset. We stand on the shoulders of giants!
""")
    pause()


def putting_it_together():
    print_header("PUTTING IT ALL TOGETHER: The AquaGuard Pipeline")

    print("""  When AquaGuard analyzes a water sample image, here's what
  happens step by step:

      [MICROSCOPE IMAGE]
             |
             v
      [1] Convert to HSV color space
             |
             v
      [2] Apply color thresholding
          (keep only purple/pink bacteria pixels)
             |
             v
      [3] Find contours (outlines of each bacterium)
             |
             v
      [4] Measure each contour
          (area, circularity, aspect ratio)
             |
             v
      [5] Feed measurements + image to neural network
          (pre-trained with transfer learning)
             |
             v
      [6] Neural network classifies:
          "This is a [coccus/bacillus/spirillum]"
          "Confidence: [X]%"
             |
             v
      [7] Count bacteria, assess contamination level
             |
             v
      [RISK ASSESSMENT REPORT]

  Each technique builds on the one before it. Together, they
  turn a raw microscope photo into an actionable water safety
  report!
""")
    pause()


def demo_mode():
    print_header("DEMO MODE: Try It Yourself!")

    # Look for sample images in training_data/
    training_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "training_data")
    training_dir = os.path.normpath(training_dir)

    if not os.path.isdir(training_dir):
        print(f"  Training data directory not found at:")
        print(f"  {training_dir}\n")
        print("  To try the demo, add sample images to the training_data/")
        print("  folder in the AquaGuard project root.\n")
        pause()
        return

    # Look for image files in subfolders (training_data/class_name/*.jpg)
    image_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif")
    images = []
    for root, dirs, files in os.walk(training_dir):
        for f in files:
            if f.lower().endswith(image_extensions):
                images.append(os.path.join(root, f))

    if not images:
        print("  No sample images found in training_data/ subfolders.")
        print("  Add .jpg or .png microscope images to try the demo.\n")
        pause()
        return

    print(f"  Found {len(images)} image(s) in training_data/:\n")
    for i, img in enumerate(images[:5], 1):
        print(f"    {i}. {os.path.basename(img)}")

    print()

    try:
        import cv2
        import numpy as np
    except ImportError:
        print("  OpenCV (cv2) is not installed. To run the demo:")
        print("    pip install opencv-python numpy\n")
        print("  For now, here's what the demo WOULD do:\n")
        print("    1. Load the image")
        print("    2. Convert RGB -> HSV color space")
        print("    3. Apply purple/pink thresholding")
        print("    4. Find contours (bacteria outlines)")
        print("    5. Count and measure each contour")
        print("    6. Display results\n")
        pause()
        return

    # Process first image as demo
    img_path = os.path.join(training_dir, images[0])
    print(f"\n  Processing: {images[0]}")
    print("  " + "-" * 40)

    img = cv2.imread(img_path)
    if img is None:
        print(f"  Could not read image: {images[0]}")
        pause()
        return

    h, w = img.shape[:2]
    print(f"  Image size: {w} x {h} pixels")

    # Convert to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    print("  Converted to HSV color space.")

    # Apply thresholding for purple/pink (Gram stain colors)
    # Purple range
    lower_purple = np.array([120, 40, 40])
    upper_purple = np.array([170, 255, 255])
    mask_purple = cv2.inRange(hsv, lower_purple, upper_purple)

    # Pink range
    lower_pink = np.array([140, 30, 100])
    upper_pink = np.array([180, 255, 255])
    mask_pink = cv2.inRange(hsv, lower_pink, upper_pink)

    # Combine masks
    mask = cv2.bitwise_or(mask_purple, mask_pink)

    # Clean up with morphological operations
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)

    # Filter by minimum area
    min_area = 50
    valid_contours = [c for c in contours if cv2.contourArea(c) >= min_area]

    print(f"  Applied color thresholding (purple/pink range).")
    print(f"  Found {len(contours)} raw contours.")
    print(f"  After filtering (min area {min_area}px): "
          f"{len(valid_contours)} bacteria candidates.\n")

    # Analyze shapes
    if valid_contours:
        print("  Shape Analysis of Detected Bacteria:")
        print("  " + "-" * 40)
        cocci_count = 0
        bacilli_count = 0
        other_count = 0

        for i, c in enumerate(valid_contours[:10]):
            area = cv2.contourArea(c)
            perimeter = cv2.arcLength(c, True)
            if perimeter == 0:
                continue
            circularity = 4 * 3.14159 * area / (perimeter * perimeter)
            x, y, bw, bh = cv2.boundingRect(c)
            aspect_ratio = max(bw, bh) / max(min(bw, bh), 1)

            if circularity > 0.7:
                shape = "Coccus (round)"
                cocci_count += 1
            elif aspect_ratio > 2.5:
                shape = "Bacillus (rod)"
                bacilli_count += 1
            else:
                shape = "Unknown"
                other_count += 1

            print(f"    #{i+1}: Area={area:.0f}px  "
                  f"Circ={circularity:.2f}  "
                  f"AR={aspect_ratio:.1f}  -> {shape}")

        print(f"\n  Summary: {cocci_count} cocci, {bacilli_count} bacilli, "
              f"{other_count} unclassified")
    print()
    pause()


def quiz():
    print_header("QUIZ TIME! (5 Questions)")
    print("  Test your understanding of AI in bacteria detection.\n")

    score = 0

    # Q1
    print("  Question 1:")
    print("  In the M&M analogy, HSV color thresholding is like:")
    print("    A) Counting all the M&Ms")
    print("    B) Sorting M&Ms by color and keeping only one color")
    print("    C) Eating all the M&Ms")
    print("    D) Melting the M&Ms together")
    answer = input("\n  Your answer (A/B/C/D): ").strip().upper()
    if answer == "B":
        print("  Correct! We filter pixels by color, just like sorting M&Ms.\n")
        score += 1
    else:
        print("  Incorrect. The answer is B -- sorting by color.\n")

    # Q2
    print("  Question 2:")
    print("  What does the 'H' in HSV stand for?")
    print("    A) Height")
    print("    B) Hue")
    print("    C) Histogram")
    print("    D) Horizontal")
    answer = input("\n  Your answer (A/B/C/D): ").strip().upper()
    if answer == "B":
        print("  Correct! Hue describes WHAT color something is.\n")
        score += 1
    else:
        print("  Incorrect. The answer is B -- Hue.\n")

    # Q3
    print("  Question 3:")
    print("  Contour analysis measures shapes. If a contour has HIGH")
    print("  circularity, it's probably a:")
    print("    A) Bacillus (rod)")
    print("    B) Spirillum (spiral)")
    print("    C) Coccus (round)")
    answer = input("\n  Your answer (A/B/C): ").strip().upper()
    if answer == "C":
        print("  Correct! High circularity = round shape = coccus.\n")
        score += 1
    else:
        print("  Incorrect. The answer is C -- Coccus (round).\n")

    # Q4
    print("  Question 4:")
    print("  Transfer learning is like:")
    print("    A) Training a brand new dog from a puppy")
    print("    B) Teaching an already-trained dog a new trick")
    print("    C) Buying a robot dog")
    print("    D) Reading a book about dogs")
    answer = input("\n  Your answer (A/B/C/D): ").strip().upper()
    if answer == "B":
        print("  Correct! We build on existing knowledge instead of\n"
              "  starting from scratch.\n")
        score += 1
    else:
        print("  Incorrect. The answer is B -- building on existing training.\n")

    # Q5
    print("  Question 5:")
    print("  Why does AquaGuard convert images to HSV instead of using")
    print("  regular RGB?")
    print("    A) HSV images are smaller in file size")
    print("    B) HSV separates color information from brightness,")
    print("       making it easier to filter by color")
    print("    C) RGB doesn't work on microscope images")
    print("    D) HSV makes images look prettier")
    answer = input("\n  Your answer (A/B/C/D): ").strip().upper()
    if answer == "B":
        print("  Correct! HSV separates hue from brightness, which makes\n"
              "  color-based filtering much more reliable.\n")
        score += 1
    else:
        print("  Incorrect. The answer is B -- HSV separates color from\n"
              "  brightness for easier filtering.\n")

    return score


def main():
    print("\n" + "*" * 60)
    print("  AQUAGUARD LEARNING MODULE 3")
    print("  How AI Detects Bacteria in Water")
    print("*" * 60)
    pause()

    introduction()
    hsv_section()
    contour_section()
    neural_network_section()
    transfer_learning_section()
    putting_it_together()
    demo_mode()

    score = quiz()

    print_header("MODULE COMPLETE!")
    print(f"  Module complete! You scored {score}/5")
    print()
    if score == 5:
        print("  PERFECT SCORE! You understand how AI sees bacteria!")
    elif score >= 3:
        print("  Well done! You've got a solid grasp of AI techniques.")
    else:
        print("  Keep at it! The concepts take a while to sink in.")
    print()


if __name__ == "__main__":
    main()
