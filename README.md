# BIOQUA: Development of an AI-Assisted Arduino-Based Water Monitoring System for Gram Stain, pH level, and Mineral Detection for Water Chemical Analysis

**Authors:** Agreda, G.M., Joven, C.L., Mendez, A.V., Tangao, W., Zamora, G.D. | 2026

BIOQUA is an automated water quality monitoring system that detects and classifies bacteria in water samples using Arduino sensors, automated Gram staining, digital microscopy, and AI image classification.

## How It Works

```
Water Sample → Pre-Filter → pH/EC Sensors → Automated Gram Staining → Microscope → AI Classification → Risk Level
```

1. **Sensors** measure pH and electrical conductivity (EC)
2. **Solenoid valves** automate the Gram staining process (Crystal Violet → Iodine → Decolorizer → Safranin)
3. **USB microscope** captures images of stained bacteria
4. **AI model** classifies bacteria by color (Gram+/Gram-) and shape (Cocci/Bacilli/Spirilla)
5. **Risk level** (LOW/MODERATE/HIGH) displayed on LCD and laptop

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
| Modular Sensors | `FEATURE_MODULAR_SENSORS` | Add temperature, turbidity |
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
