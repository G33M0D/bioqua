# BIOQUA: Development of an AI-Assisted Arduino-Based Water Monitoring System for Gram Stain, pH level, and Mineral Detection for Water Chemical Analysis

**Authors:** Agreda, G.M., Joven, C.L., Mendez, A.V., Tangao, W., Zamora, G.D. | 2026

BIOQUA is an automated water quality monitoring system that detects and classifies bacteria in water samples using Arduino sensors, automated Gram staining, digital microscopy, and AI image classification.

The authoritative methodology lives in [docs/Phase.pdf](docs/Phase.pdf). A plain-language summary follows.

## How It Works — The Four Phases

**Phase I — Water Sample and Water Quality Assessment.** An Arduino-controlled pump draws water through a pre-filter into a flow-through sensor manifold where the EC probe sits fully immersed. EC is measured **first** on bulk water — before any staining — because accurate TDS estimation needs volume, and that chance is gone once the sample is spread thin. The EC signal is digitised by the Arduino ADC and used as a proxy for TDS; pH is measured concurrently and cross-referenced against EC trends to detect pollution events.

**Phase II — Gram Stain Analysis.** *Part I (sample injection):* a 3/2-way solenoid valve opens the path to a 1 mL sample syringe. Once the syringe is full, the Arduino flips the valve, closes the intake, and opens the path to the microfluidic chamber. *Part II (on-chip staining):* the sample sits stationary while the Arduino runs Crystal Violet → Iodine → Decolorizer → Safranin through serpentine microchannels. A USB digital microscope (read on the laptop with OpenCV `VideoCapture`) captures images of the stained bacteria; classification is paused on `STAINING_START` and resumed on `STAINING_DONE`.

**Phase III — Gram-Staining Evaluation.** The captured image is fed to the AI classifier. The paper's target architecture is two Random Forest models — one for Gram colour (purple vs pink), one for morphology (rods, cocci, chains, clusters) — yielding the six final classes in Table 2.1. The current prototype ships a MobileNetV2 CNN fine-tuned via transfer learning as a single-model stand-in until the two-RF pipeline is trained.

**Phase IV — Gated Fusion Risk Assessment.** The 15-row decision table cross-examines Phase I (chemical condition) × Phase III (bacteria class) to produce one of five risk levels: Low-Risk Contamination, Moderate Biological Risk, Moderate Risk, Moderate-High Risk, or High-Risk Contamination. The LCD and the laptop display a short code (`LOW` / `MOD-BIO` / `MOD` / `MOD-HIGH` / `HIGH` / `SAFE`).

## Where the code lives

- **GitHub**: https://github.com/G33M0D/bioqua
- **Local**: `~/bioqua/` (the source of truth on the dev machine)

## Quick Start

```bash
# 1. Install Python packages
pip install -r python/requirements.txt

# 2. Upload Arduino sketch
#    Open arduino/bioqua_controller/bioqua_controller.ino in Arduino IDE
#    Select Board: Arduino Mega 2560, select Port, click Upload

# 3. Test hardware
python python/test_camera.py      # Test microscope camera
python python/test_serial.py      # Test Arduino connection

# 4. Collect training images
python python/capture_images.py   # Press 1-5 to save images per class

# 5. Train AI model
python python/train_model.py      # OR use Google Teachable Machine

# 6. Run BIOQUA
python python/controller.py       # Main system
```

## Features

| Feature | Toggle in config.py | Description |
|---------|-------------------|-------------|
| Core System | Always on | Sensors + staining + AI + LCD |
| Data Logging | `FEATURE_DATA_LOGGING` | Save tests to CSV |
| PDF Reports | `FEATURE_PDF_REPORTS` | Generate printable reports |
| Modular Sensors | `FEATURE_MODULAR_SENSORS` | Extensibility hook for future sensor plug-ins |
| Learning Modules | `FEATURE_LEARNING_MODULES` | Interactive science guides |
| Bluetooth Mobile | `FEATURE_BLUETOOTH_MOBILE` | Phone app via ESP32 |

All features are OFF by default. Enable them one at a time in `python/config.py`.

## Project Structure

```
bioqua/
├── arduino/          # Arduino Mega sketch
├── python/           # Python scripts (controller, training, config)
├── sensors/          # Modular sensor plugins
├── learning/         # Interactive educational modules
├── mobile/           # ESP32 Bluetooth + phone app
├── models/           # Trained AI models
├── training_data/    # Microscope images for training
├── results/          # Test logs, images, PDF reports
├── wiring/           # Wiring diagram
└── docs/             # Full manual
```

## Documentation

See [docs/MANUAL.md](docs/MANUAL.md) for the complete setup guide, configuration reference, troubleshooting FAQ, and science report helper.

## License

MIT License - see [LICENSE](LICENSE)
