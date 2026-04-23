# ============================================================
# BIOQUA: AI-Assisted Water Quality Monitoring System
#
# Authors         : Agreda, G.M., Joven, C.L., Mendez, A.V., Tangao, W., Zamora, G.D.
# Year            : 2026
# License         : MIT License
#
# This project is the original work of the authors.
# Unauthorized removal of this notice is prohibited.
# ============================================================

"""
Train the BIOQUA AI Model
=============================
This script trains a bacteria classifier using transfer learning
with MobileNetV2. It learns from images you've collected.

BEFORE RUNNING:
  1. Collect training images using: python capture_images.py
  2. Put them in the training_data/ folders:
       training_data/gram_positive_cocci/     (30-50 images)
       training_data/gram_positive_bacilli/    (30-50 images)
       training_data/gram_negative_cocci/      (30-50 images)
       training_data/gram_negative_bacilli/     (30-50 images)
       training_data/no_bacteria/              (30-50 images)

HOW TO RUN:
  python train_model.py

WHAT IT DOES:
  - Loads a pre-trained MobileNetV2 model (trained on millions of images)
  - Fine-tunes it on YOUR bacteria images (transfer learning)
  - Saves the trained model to models/bioqua_model.h5

TIME: 5-15 minutes on a modern laptop (no GPU needed)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *


def check_training_data():
    """Check that training data exists and has enough images."""
    data_dir = os.path.join(PROJECT_ROOT, "training_data")

    if not os.path.exists(data_dir):
        print(f"ERROR: Training data folder not found at {data_dir}")
        return False

    print("Checking training data...")
    print("-" * 50)

    total_images = 0
    all_ok = True

    for class_name in sorted(os.listdir(data_dir)):
        class_dir = os.path.join(data_dir, class_name)
        if not os.path.isdir(class_dir):
            continue

        images = [f for f in os.listdir(class_dir)
                  if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        count = len(images)
        total_images += count

        status = "OK" if count >= 20 else "LOW" if count >= 5 else "EMPTY"
        icon = "+" if status == "OK" else "!" if status == "LOW" else "X"
        print(f"  [{icon}] {class_name}: {count} images ({status})")

        if count < 5:
            all_ok = False

    print("-" * 50)
    print(f"  Total: {total_images} images")
    print()

    if total_images == 0:
        print("ERROR: No training images found!")
        print("Collect images first using: python capture_images.py")
        print("OR download the DIBaS dataset from: http://misztal.edu.pl/software/databases/dibas/")
        return False

    if not all_ok:
        print("WARNING: Some classes have very few images (<5).")
        print("The model may not learn well. Try to collect at least 20 images per class.")
        print()
        response = input("Continue anyway? (y/n): ").strip().lower()
        if response != 'y':
            return False

    return True


def train():
    """Train the MobileNetV2 model on bacteria images."""
    try:
        import tensorflow as tf
        from tensorflow.keras.applications import MobileNetV2
        from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
        from tensorflow.keras.models import Model
        from tensorflow.keras.preprocessing.image import ImageDataGenerator
    except ImportError:
        print("ERROR: TensorFlow not installed.")
        print("Run: pip install tensorflow")
        sys.exit(1)

    data_dir = os.path.join(PROJECT_ROOT, "training_data")

    print("Setting up data augmentation...")
    # Training data gets augmented — rotate, flip, zoom for variety
    # IMPORTANT: Do NOT augment color/hue — it would corrupt Gram stain information!
    train_datagen = ImageDataGenerator(
        rotation_range=20,
        width_shift_range=0.1,
        height_shift_range=0.1,
        zoom_range=0.15,
        horizontal_flip=True,
        vertical_flip=True,
        validation_split=0.2,
        rescale=1.0 / 255.0
    )

    # Validation data gets NO augmentation — clean holdout for honest accuracy
    val_datagen = ImageDataGenerator(
        validation_split=0.2,
        rescale=1.0 / 255.0
    )

    print("Loading training images...")
    # Use same seed so both generators split the same way (no data leakage)
    SPLIT_SEED = 42

    train_data = train_datagen.flow_from_directory(
        data_dir,
        target_size=AI_IMAGE_SIZE,
        batch_size=16,
        class_mode='categorical',
        subset='training',
        shuffle=True,
        seed=SPLIT_SEED
    )

    val_data = val_datagen.flow_from_directory(
        data_dir,
        target_size=AI_IMAGE_SIZE,
        batch_size=16,
        class_mode='categorical',
        subset='validation',
        shuffle=False,
        seed=SPLIT_SEED
    )

    num_classes = train_data.num_classes
    print(f"\nClasses found: {train_data.class_indices}")
    print(f"Number of classes: {num_classes}")
    print(f"Training images: {train_data.samples}")
    print(f"Validation images: {val_data.samples}")

    print("\nBuilding model (MobileNetV2 + custom classifier)...")
    # Load MobileNetV2 pre-trained on ImageNet (1.4 million images)
    # We freeze it and add our own classifier on top
    base_model = MobileNetV2(
        weights='imagenet',
        include_top=False,
        input_shape=(AI_IMAGE_SIZE[0], AI_IMAGE_SIZE[1], 3)
    )
    base_model.trainable = False  # Freeze — don't change the pre-trained weights

    # Add our classifier layers
    x = base_model.output
    x = GlobalAveragePooling2D()(x)         # Compress features
    x = Dropout(0.3)(x)                     # Prevent overfitting
    x = Dense(64, activation='relu')(x)     # Learn bacteria-specific features
    output = Dense(num_classes, activation='softmax')(x)  # Classify

    model = Model(inputs=base_model.input, outputs=output)
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    print(f"Model parameters: {model.count_params():,} total, "
          f"{sum(p.numpy().size for p in model.trainable_weights):,} trainable")

    # Train
    print("\n" + "=" * 50)
    print("  TRAINING STARTED")
    print("  This will take 5-15 minutes...")
    print("=" * 50 + "\n")

    history = model.fit(
        train_data,
        validation_data=val_data,
        epochs=15,
        verbose=1
    )

    # Save model and class mapping
    os.makedirs(os.path.dirname(AI_MODEL_PATH), exist_ok=True)
    model.save(AI_MODEL_PATH)

    # Save class indices so inference uses the same label order
    import json
    class_map_path = AI_MODEL_PATH.replace('.h5', '_classes.json')
    # Invert {name: index} to {index: name} for easy lookup
    idx_to_class = {v: k for k, v in train_data.class_indices.items()}
    with open(class_map_path, 'w') as f:
        json.dump(idx_to_class, f, indent=2)
    print(f"  Class mapping saved to: {class_map_path}")

    # Print results
    final_acc = history.history['accuracy'][-1]
    final_val_acc = history.history['val_accuracy'][-1]

    print("\n" + "=" * 50)
    print("  TRAINING COMPLETE!")
    print(f"  Training accuracy:   {final_acc:.1%}")
    print(f"  Validation accuracy: {final_val_acc:.1%}")
    print(f"  Model saved to: {AI_MODEL_PATH}")
    print("=" * 50)

    if final_val_acc < 0.5:
        print("\nWARNING: Validation accuracy is below 50%.")
        print("This means the model is not learning well. Try:")
        print("  - Collecting more training images (at least 30 per class)")
        print("  - Making sure images are clear and well-focused")
        print("  - Checking that images are in the correct folders")

    print("\nNext step: Run the controller to test your model:")
    print("  python controller.py")


if __name__ == "__main__":
    print("=" * 60)
    print("  BIOQUA AI Model Trainer")
    print("  Authors: Agreda, G.M., Joven, C.L., Mendez, A.V., Tangao, W., Zamora, G.D.")
    print("=" * 60)
    print()

    if check_training_data():
        train()
