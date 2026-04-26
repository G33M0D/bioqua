# BIOQUA Project Manual

**AI-Assisted Water Quality Monitoring System**

Authors: Agreda, G.M., Joven, C.L., Mendez, A.V., Tangao, W., Zamora, G.D. | Year: 2026

---

This manual is your complete guide to setting up, running, customizing, and troubleshooting BIOQUA. It also includes a section to help you write your science research report.

The authoritative methodology — tables, references, acceptance criteria — is [docs/Phase.pdf](Phase.pdf). This manual is the practical companion that explains how to build and run the system.

**How to use this manual:**

- **First time?** Start at Part 1 and follow every step in order.
- **Already set up?** Jump to Part 2 to customize settings.
- **Something broken?** Go straight to Part 3.
- **Writing your report?** Part 4 has explanations, analogies, and sample sentences you can adapt.

## Where the code lives

- **GitHub (source of truth):** https://github.com/G33M0D/bioqua
- **Local clone on the dev machine:** `~/bioqua/`

---

# Architecture: The Four Phases

BIOQUA's methodology runs in four sequential phases. Each phase produces data that downstream phases consume. The numbering is **chronological** — phases are listed in the order they happen during a test cycle.

### Phase I — Water Sample and Water Quality Assessment

The Arduino turns on the peristaltic pump, which draws water through a pre-filter into a flow-through sensor manifold. An Electrical Conductivity (EC) probe sits fully immersed in the manifold. EC is measured **first**, on bulk water, because accurate TDS estimation needs volume — once the sample is diverted onto a slide or into a microchannel, that chance is gone. The Arduino's ADC digitises the EC reading and uses it as a proxy for TDS. pH is measured concurrently and statistically correlated against EC trends to flag pollution events (Tautabuzzumaro 2025; Kumar 2026).

**Hardware:** pump, pre-filter, flow-through sensor manifold, EC probe, pH probe
**Arduino does:** pump control, ADC read, transmits pH and EC over serial
**Output:** Table 2.2 chemical condition → Phase IV input

### Phase II — Gram Stain Analysis

This phase has two parts.

**Part I — Sample Injection.** A 3/2-way solenoid valve opens the path from the manifold to a 1 mL sample syringe. The syringe draws exactly 1 mL. The Arduino then flips the 3/2-way valve — closing the intake and opening the path to the microfluidic chamber — and pushes the sample in. This avoids cross-contamination, overpressure, and air bubbles.

**Part II — On-chip Gram Staining.** With the sample held stationary, the Arduino runs the automated Gram staining sequence. Each reagent is delivered through serpentine microchannels so mixing happens on-chip. The stain order is fixed:

1. **Crystal Violet** (60 s) — primary stain (purple)
2. **Iodine** (60 s) — mordant (fixes the purple in Gram-positive cell walls)
3. **Decolorizer** (10 s) — strips the stain from Gram-negative cells (critical — too long and Gram-positives false-negative)
4. **Safranin** (60 s) — counterstain (pink for Gram-negatives)

A 15 s DI-water rinse runs between each step.

**Image acquisition.** The microscope is a USB digital microscope opened on the laptop with OpenCV's `cv2.VideoCapture(CAMERA_INDEX)`. Frames are read continuously at ~10 Hz. The Arduino emits `STAINING_START` at the beginning of `runGramStain()` to pause the laptop classifier while reagents flow, and `STAINING_DONE` after the final wash so the next captured frame is fed into Phase III. Frames whose model confidence falls below `AI_CONFIDENCE_THRESHOLD = 0.6` are reported as `Uncertain` and produce no Phase IV verdict.

**Hardware:** 1 mL syringe (servo or stepper), 3/2-way valve, microfluidic chamber, 4 × reagent solenoid valves, DI water valve, USB digital microscope
**Arduino does:** aspirate, switch valve, inject, time each reagent, run wash cycles, emit `STAINING_START` / `STAINING_DONE`
**Output:** stained-bacteria images → Phase III input

### Phase III — Gram-Staining Evaluation

The captured image is passed to the AI classifier. The paper's target architecture (Sizar, Leslie, & Unakal 2023; Tankeshwar 2013) is a two-model machine-learning pipeline:

- **Model 1 — Gram Colour Identification.** A Random Forest analyses the slide's tint to determine whether the specimen is Gram-positive (purple) or Gram-negative (pink).
- **Model 2 — Morphological Categorization.** A second Random Forest analyses geometric descriptors extracted by SAT-AC (Selective Adaptive Thresholding–Active Contours): diameter and area; symmetry from centre to boundary; ratios indicating elongation or clustering. It assigns the specimen to one of the six final classes in Table 2.1 (Gram-positive rods, Gram-positive cocci (chains), Gram-positive cocci (clusters), Gram-positive cocci, Gram-negative rods, Gram-negative cocci).

The current prototype ships with a simpler **MobileNetV2** convolutional neural network (fine-tuned from Google Teachable Machine) covering five collapsed classes. This is a drop-in stand-in until the two-Random-Forest pipeline is trained and validated. The Phase IV gated fusion logic is identical either way — only the upstream classifier changes.

**Hardware:** host laptop running Python, OpenCV, and TensorFlow
**Output:** Table 2.1 bacteria classification → Phase IV input

### Phase IV — Gated Fusion Risk Assessment

The AI cross-examines Phase I (chemical condition) × Phase III (bacteria classification) using the 15-row gated fusion table (Table 2.3). The result is one of five risk levels: Low-Risk Contamination, Moderate Biological Risk, Moderate Risk, Moderate-High Risk, or High-Risk Contamination.

The Phase IV table follows decision-table modelling methods commonly used in automated environmental monitoring systems and incorporates microbial contamination guidelines from WHO (2017) and chemical contamination thresholds from USGS (2023).

**Arduino does:** receive the verdict over serial, display short code on the 20×4 LCD
**Output:** risk level on LCD, on the laptop overlay, and (if data logging is on) in the CSV and PDF report

### Risk Levels

The fusion table is keyed on **Phase I (chemical condition) × Phase III (bacteria class)**.

| Short code | Full label (Table 2.3)         | When it fires                                                                 |
|------------|--------------------------------|-------------------------------------------------------------------------------|
| `SAFE`     | Safe                           | No bacteria detected AND Phase I = Chemically Stable Water                    |
| `LOW`      | Low-Risk Contamination         | Gram-positive (rods / cocci chains / cocci clusters) AND Phase I stable       |
| `MOD-BIO`  | Moderate Biological Risk       | Gram-negative bacteria detected AND Phase I stable *(see retention note)*     |
| `MOD`      | Moderate Risk                  | Gram-positive bacteria + Phase I = Moderate Chemical Contamination            |
| `MOD-HIGH` | Moderate-High Risk             | Gram-negative bacteria + Phase I = Moderate Chemical Contamination            |
| `HIGH`     | High-Risk Contamination        | Phase I = Severe Chemical Contamination (high TDS spike + pH drop), regardless of bacteria class |

> **Retention note.** The current implementation retains `Moderate Biological Risk` for stable-chemistry Gram-negative results. The revised methodology PDF moves these rows to `Moderate Risk` while still listing `Moderate Biological Risk` as a defined level — likely an editing inconsistency. The more-specific label is preserved here because pathogen-present-with-normal-chemistry is a meaningfully distinct failure mode worth naming.

---

# Table of Contents

- [Part 1 -- Full Setup Guide (Start Here)](#part-1--full-setup-guide-start-here)
  - [Step 1: Install Python 3](#step-1-install-python-3)
  - [Step 2: Install Arduino IDE](#step-2-install-arduino-ide)
  - [Step 3: Install Arduino Libraries](#step-3-install-arduino-libraries)
  - [Step 4: Install Python Packages](#step-4-install-python-packages)
  - [Step 5: Wiring Your Hardware](#step-5-wiring-your-hardware)
  - [Step 6: Upload the Arduino Sketch](#step-6-upload-the-arduino-sketch)
  - [Step 7: Test the Camera](#step-7-test-the-camera)
  - [Step 8: Test the Serial Connection](#step-8-test-the-serial-connection)
  - [Step 9: Run the Full System](#step-9-run-the-full-system)
  - [Step 10: Your First Test](#step-10-your-first-test)
- [Part 2 -- Configuration Guide (Customize It)](#part-2--configuration-guide-customize-it)
  - [All Settings in config.py](#all-settings-in-configpy)
  - [How to Find Your Serial Port](#how-to-find-your-serial-port)
  - [Feature Toggles](#feature-toggles)
  - [How to Add New Bacteria Classes](#how-to-add-new-bacteria-classes)
  - [How to Retrain the AI](#how-to-retrain-the-ai)
  - [How to Switch Between AI Options](#how-to-switch-between-ai-options)
- [Part 3 -- Troubleshooting FAQ](#part-3--troubleshooting-faq)
- [Part 4 -- Science Report Helper](#part-4--science-report-helper)
  - [What Is AI?](#what-is-ai)
  - [How BIOQUA's AI Sees Bacteria](#how-bioquas-ai-sees-bacteria)
  - [What Is Transfer Learning?](#what-is-transfer-learning)
  - [What Is Gram Staining?](#what-is-gram-staining)
  - [How to Present Accuracy (Confusion Matrix)](#how-to-present-accuracy-confusion-matrix)
  - [Suggested Report Structure](#suggested-report-structure)
  - [Key Vocabulary List](#key-vocabulary-list)
  - [Sample Sentences You Can Adapt](#sample-sentences-you-can-adapt)

---

# Part 1 -- Full Setup Guide (Start Here)

Read each step carefully. Do them in order. Do not skip ahead.

---

## Step 1: Install Python 3

Python is the programming language that runs BIOQUA's brain on your laptop. The Arduino handles the hardware, but all the AI, camera work, and analysis happens in Python.

### On Windows

1. Open your web browser and go to **https://www.python.org/downloads/**
2. Click the big yellow button that says **"Download Python 3.x.x"** (the exact number doesn't matter as long as it starts with 3)
3. Open the downloaded file (it will be called something like `python-3.12.x-amd64.exe`)
4. **IMPORTANT: On the very first screen of the installer, check the box at the bottom that says "Add python.exe to PATH"** -- this is the most common mistake people make. If you miss this, nothing will work later.
5. Click **"Install Now"**
6. Wait for it to finish, then click **"Close"**

### On Mac

1. Open your web browser and go to **https://www.python.org/downloads/**
2. Click the big yellow button that says **"Download Python 3.x.x"**
3. Open the downloaded `.pkg` file
4. Click through the installer (Next, Next, Agree, Install)
5. Enter your Mac password when asked
6. Click **"Close"** when done

### What You Should See

Open a terminal to verify it worked:

- **Windows:** Press the Windows key, type `cmd`, press Enter
- **Mac:** Press Cmd+Space, type `Terminal`, press Enter

Then type:

```
python --version
```

You should see something like:

```
Python 3.12.4
```

The exact number doesn't matter as long as it starts with `3`.

> **If something went wrong:**
>
> - If you see `'python' is not recognized` (Windows) or `command not found` (Mac):
>   - You probably forgot to check "Add to PATH" during installation
>   - Uninstall Python (Windows: Settings > Apps > Python > Uninstall), then redo Step 1 and **make sure you check the PATH box**
> - On Mac, if `python --version` shows Python 2, try `python3 --version` instead. If that works, use `python3` instead of `python` for all commands in this manual
> - If you see `Python 3.x.x` -- you are good. Move on.

---

## Step 2: Install Arduino IDE

The Arduino IDE is the program you use to write code to the Arduino Mega board. You only need it to upload the BIOQUA sketch once.

1. Open your web browser and go to **https://www.arduino.cc/en/software**
2. Scroll down to **"Download Options"**
3. Click the download for your operating system:
   - **Windows:** "Windows Win 10 and newer, 64 bits" (the .exe installer, not the zip)
   - **Mac:** "macOS 12 (Monterey) or newer"
4. You may see a "Contribute & Download" page -- you can click **"Just Download"** (no payment required)
5. Run the installer:
   - **Windows:** Double-click the downloaded `.exe` file, click Yes/Next through everything
   - **Mac:** Drag the Arduino IDE icon into your Applications folder
6. Open Arduino IDE (search for "Arduino IDE" in your Start Menu or Applications)

### What You Should See

The Arduino IDE opens with a blank sketch that looks like this:

```
void setup() {
  // put your setup code here, to run once:
}

void loop() {
  // put your main code here, to run repeatedly:
}
```

> **If something went wrong:**
>
> - If Windows says "Windows protected your PC" -- click "More info", then "Run anyway"
> - If Mac says the app "can't be opened because it is from an unidentified developer" -- go to System Settings > Privacy & Security > scroll down and click "Open Anyway"
> - If you see a security warning about USB drivers, click "Allow" or "Install" -- the Arduino needs USB drivers to communicate

---

## Step 3: Install Arduino Libraries

Libraries are pre-written code that makes it easier to talk to specific hardware. BIOQUA needs two libraries.

### Library 1: LiquidCrystal I2C (Required)

This library lets the Arduino control the 20x4 LCD screen.

1. In Arduino IDE, go to **Sketch > Include Library > Manage Libraries** (or press Ctrl+Shift+I)
2. In the search box at the top, type: `LiquidCrystal I2C`
3. Find the one by **Frank de Brabander** (it should be near the top)
4. Click **Install**
5. Wait for the green "INSTALLED" label to appear

### Library 2: DFRobot_PH (Optional)

This library provides advanced pH calibration. You only need it if you are using a DFRobot pH sensor module.

1. In the same Library Manager, search for: `DFRobot_PH`
2. Find the one by **DFRobot**
3. Click **Install**

### What You Should See

After installing, if you go to **Sketch > Include Library**, you should see "LiquidCrystal I2C" listed near the bottom under "Contributed libraries."

> **If something went wrong:**
>
> - If the Library Manager won't open or hangs: close Arduino IDE completely, reopen it, and try again
> - If you can't find the library: make sure you spelled it exactly right. Try just searching "LiquidCrystal" and scrolling through results
> - If it says "Error installing library": check your internet connection, then try again

---

## Step 4: Install Python Packages

BIOQUA needs several Python packages (think of them as tools that Python downloads from the internet). Open a terminal (Command Prompt on Windows, Terminal on Mac) and run this command:

```
pip install opencv-python numpy tensorflow pyserial scikit-learn
```

This will download and install:

| Package | What It Does |
|---------|-------------|
| `opencv-python` | Captures and processes images from the USB microscope |
| `numpy` | Does fast math on images (needed by everything else) |
| `tensorflow` | Runs the AI model that classifies bacteria |
| `pyserial` | Talks to the Arduino through the USB cable |
| `scikit-learn` | Alternative AI method using feature extraction |

If you also want PDF reports and charts, run:

```
pip install fpdf2 matplotlib
```

### What You Should See

A lot of text will scroll by as each package downloads. At the end, you should see:

```
Successfully installed opencv-python-4.x.x numpy-1.x.x tensorflow-2.x.x pyserial-3.x scikit-learn-1.x.x
```

The exact version numbers don't matter. What matters is that there are no red `ERROR` lines.

> **If something went wrong:**
>
> - `'pip' is not recognized`: Python wasn't installed correctly or PATH wasn't set. Go back to Step 1.
> - On Mac, try `pip3` instead of `pip` (same reason as `python3` vs `python`)
> - `ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied`:
>   - On Windows: open Command Prompt as Administrator (right-click > Run as administrator)
>   - On Mac/Linux: add `--user` to the end: `pip install --user opencv-python numpy tensorflow pyserial scikit-learn`
> - If TensorFlow fails: it requires 64-bit Python. Check by running `python -c "import struct; print(struct.calcsize('P') * 8)"` -- it should say `64`. If it says `32`, uninstall Python and download the 64-bit version.
> - If TensorFlow takes forever: it is a large download (~500 MB). Be patient and make sure you have a good internet connection.

---

## Step 5: Wiring Your Hardware

Before you power anything on, connect all the hardware according to the wiring diagram.

**Refer to:** `wiring/wiring_diagram.txt` in the project folder.

Here is a summary of all connections:

### Arduino Mega Pin Connections

| Component | Arduino Pin | Notes |
|-----------|------------|-------|
| pH Sensor Signal | A0 | Analog input |
| TDS/EC Sensor Signal | A1 | Analog input |
| Relay 1 (Crystal Violet valve) | D2 | Digital output |
| Relay 2 (Iodine valve) | D3 | Digital output |
| Relay 3 (Decolorizer valve) | D4 | Digital output |
| Relay 4 (Safranin valve) | D5 | Digital output |
| Relay 5 (DI Water valve) | D6 | Digital output |
| Relay 6 (Peristaltic pump) | D7 | Digital output |
| Start Button | D8 | Optional, uses internal pull-up |
| 3/2-Way Directional Valve (Phase 2) | D9 | LOW = intake path, HIGH = injection path |
| Syringe Actuator (Phase 2) | D10 | HIGH = energise, LOW = idle |
| LCD SDA | SDA (pin 20) | I2C data |
| LCD SCL | SCL (pin 21) | I2C clock |

### Power

| Component | Power | Notes |
|-----------|-------|-------|
| pH Sensor | 5V from Arduino | Connect VCC to 5V, GND to GND |
| TDS Sensor | 5V from Arduino | Connect VCC to 5V, GND to GND |
| Relay Module | 5V from Arduino (signal), separate 12V supply (valves) | **Never power solenoid valves directly from Arduino -- they need their own power supply** |
| LCD (20x4 I2C) | 5V from Arduino | VCC to 5V, GND to GND |
| Peristaltic Pump | External 12V supply via relay | Same as solenoid valves |
| 3/2-Way Valve | External 12V supply via relay | Two-position solenoid valve (Phase 2) |
| Syringe Actuator | External 5V/12V per spec | Servo- or stepper-driven 1 mL syringe (Phase 2) |

### Important Safety Notes

- **Double-check every connection before plugging in the USB cable.** A wrong wire can permanently damage the Arduino.
- **Solenoid valves and the pump need an external 12V power supply.** The Arduino cannot power them -- it can only switch them on and off through the relay module.
- **Relay modules are usually active-LOW.** This means the Arduino sends LOW (0V) to turn the relay ON, and HIGH (5V) to turn it OFF. The code already handles this.
- **If the LCD doesn't show anything after uploading the sketch**, the I2C address might be wrong. The code uses `0x27`. The other common address is `0x3F`. See Troubleshooting, Part 3.

> **If something went wrong:**
>
> - Nothing works at all: Check that the Arduino is getting power (the ON LED should be lit when USB is plugged in)
> - Relays click but valves don't open: Check the 12V power supply. The relay switches the 12V to the valves -- if there's no 12V, the valves won't move.
> - Only some relays work: Check individual wire connections from the Arduino digital pins (D2-D7) to the relay module inputs

---

## Step 6: Upload the Arduino Sketch

The Arduino sketch is the code that runs on the Arduino itself. It reads sensors, controls valves, and shows results on the LCD.

1. Open Arduino IDE
2. Go to **File > Open**
3. Navigate to your BIOQUA project folder and open: `arduino/bioqua_controller/bioqua_controller.ino`
4. Plug in the Arduino Mega to your laptop with a USB cable
5. In Arduino IDE, go to **Tools > Board** and select **"Arduino Mega or Mega 2560"**
   - If you don't see it, go to **Tools > Board > Boards Manager**, search for "Arduino AVR Boards", and install it
6. Go to **Tools > Port** and select the port that appeared when you plugged in the Arduino:
   - **Windows:** It will be something like `COM3` or `COM4` (it will say "Arduino Mega 2560" next to it)
   - **Mac:** It will be something like `/dev/cu.usbmodem14201`
   - If you don't see any port, unplug and replug the USB cable
7. Click the **Upload** button (the right-pointing arrow icon in the top-left, or press Ctrl+U)
8. Wait for it to compile and upload

### What You Should See

At the bottom of Arduino IDE, in the black console area:

```
Compiling sketch...
Uploading...
avrdude done. Thank you.
```

And on the physical LCD screen attached to the Arduino:

```
=== BIOQUA ===
System Ready
Press START or
send 'S' via Serial
```

> **If something went wrong:**
>
> - `Board at COM3 is not available`: The wrong port is selected, or the Arduino is not plugged in. Unplug and replug, then check Tools > Port again.
> - `avrdude: stk500v2_ReceiveMessage(): timeout`: The wrong board is selected. Make sure Tools > Board says "Arduino Mega or Mega 2560" (not "Arduino Uno").
> - `compilation error` / `LiquidCrystal_I2C.h: No such file or directory`: The library wasn't installed. Go back to Step 3.
> - `Upload error` on Mac: Go to System Settings > Privacy & Security and allow the USB device.
> - The code compiles but LCD shows nothing: See Step 5 safety notes about the I2C address (`0x27` vs `0x3F`).

---

## Step 7: Test the Camera

Before running the full system, let's make sure your laptop can see the USB microscope.

1. Plug the USB microscope into your laptop
2. Open a terminal (Command Prompt on Windows, Terminal on Mac)
3. Navigate to the project's python folder:
   ```
   cd path/to/bioqua/python
   ```
   (Replace `path/to/bioqua` with wherever you saved the project -- for example, `cd C:\Users\YourName\Documents\bioqua\python` on Windows or `cd ~/Documents/bioqua/python` on Mac)
4. Run:
   ```
   python test_camera.py
   ```

### What You Should See

In the terminal:

```
==================================================
  BIOQUA Camera Test
==================================================

Testing camera indices 0, 1, 2...

  [+] Camera index 0: WORKS (640x480)
  [-] Camera index 1: Not available
  [-] Camera index 2: Not available

Found 1 working camera(s).

Showing camera index 0. Press [q] to quit.
```

A window will pop up showing a live video feed from the microscope. Press `q` to close it.

**Take note of which camera index showed the microscope image.** If your laptop also has a built-in webcam, the microscope might be at index 1 instead of 0. Remember this number for config.py.

> **If something went wrong:**
>
> - `No working cameras found!`:
>   - Is the USB microscope plugged in? Try unplugging and plugging it back in.
>   - On Windows: open Device Manager (right-click Start button > Device Manager) and look under "Cameras" or "Imaging devices". The microscope should appear there.
>   - On Mac: go to System Settings > Privacy & Security > Camera and make sure Terminal has camera access.
> - The wrong camera shows (your face instead of the microscope): The microscope is at a different index. Note the correct index number from the test output and update `CAMERA_INDEX` in `python/config.py` (see Part 2).
> - `ModuleNotFoundError: No module named 'cv2'`: OpenCV isn't installed. Go back to Step 4 and run `pip install opencv-python`.

---

## Step 8: Test the Serial Connection

This test checks whether your laptop can communicate with the Arduino.

**Before running this test:**
- The Arduino sketch must already be uploaded (Step 6)
- The Arduino must be plugged in via USB
- Arduino IDE's Serial Monitor must be **closed** (only one program can use the serial port at a time)

1. In the same terminal, run:
   ```
   python test_serial.py
   ```

### What You Should See

```
==================================================
  BIOQUA Serial Test
==================================================

Available serial ports:
  COM3 - Arduino Mega 2560

Connecting to COM3 at 9600 baud...
Connected!

Reading sensor data (press Ctrl+C to stop):
--------------------------------------------------
  Arduino: BIOQUA_READY
  pH: 7.02  |  EC: 485.3 uS/cm
  pH: 7.01  |  EC: 486.1 uS/cm
```

The pH and EC values will keep scrolling. Press `Ctrl+C` to stop.

If the serial port is wrong, the test will show you all available ports and tell you which one to put in config.py.

> **If something went wrong:**
>
> - `ERROR: could not open port 'COM3'`:
>   - **Most common cause:** Arduino IDE's Serial Monitor is still open. Close it, then try again.
>   - The port name is wrong. Look at the "Available serial ports" list in the output and update `SERIAL_PORT` in `python/config.py`.
> - `No serial ports found`:
>   - The Arduino isn't plugged in, or the USB cable is a charge-only cable (some cheap cables don't carry data). Try a different cable.
>   - On Windows, you may need to install the CH340 USB driver (search "CH340 driver download" and install it).
> - `ModuleNotFoundError: No module named 'serial'`: pyserial isn't installed. Run `pip install pyserial`.

---

## Step 9: Run the Full System

Everything is connected and tested. Time to run BIOQUA.

1. Make sure:
   - Arduino is plugged in and the sketch is uploaded
   - USB microscope is plugged in
   - Arduino IDE Serial Monitor is **closed**
2. In the terminal, run:
   ```
   python controller.py
   ```

### What You Should See

```
============================================================
  BIOQUA: AI-Assisted Water Quality Monitoring
  Authors: Agreda, G.M., Joven, C.L., Mendez, A.V., Tangao, W., Zamora, G.D.
============================================================

WARNING: No AI model found at .../models/bioqua_model.h5
The system will run without AI classification.
Arduino connected on COM3
Arduino is ready!
Camera connected (index 0)

Controls: [q]uit  [s]tart staining  [c]apture image  [r]eport
------------------------------------------------------------
```

A video window will appear showing the live microscope feed. At the top of the video, you will see a status bar showing the current bacteria classification and risk level.

**The "No AI model" warning is normal on first run.** The system will use color-based detection (HSV method) as a fallback until you train your own model.

### Keyboard Controls (while the video window is in focus)

| Key | What It Does |
|-----|-------------|
| `q` | Quit BIOQUA |
| `s` | Start the automated Gram staining sequence |
| `c` | Capture and save the current microscope image |
| `r` | Generate a PDF report (only if PDF reports are enabled) |
| `l` | Show learning module commands (only if learning modules are enabled) |

> **If something went wrong:**
>
> - `Cannot continue without a camera. Exiting.`: The camera isn't working. Go back to Step 7.
> - The video window opens but is black: The microscope might need a moment to initialize. Wait 5 seconds. If it stays black, unplug and replug the microscope.
> - Video is very laggy: This is normal on slower laptops, especially when TensorFlow is running. The system processes one frame per second by design.

---

## Step 10: Your First Test

Now that the system is running, let's do a test to make sure everything works together.

### If You Have a Prepared Gram-Stained Slide

1. Place the slide under the USB microscope
2. Adjust focus until you can see individual bacteria (you want to see small colored dots or rods)
3. Look at the status bar at the top of the video window -- it should show a classification like "Gram+ Cocci" or "Gram- Bacilli" along with a confidence percentage
4. The LCD on the Arduino should also update with the result

### If You Don't Have a Slide Yet

You can still verify the system works:

1. Point the microscope at something purple (like a purple marker on paper) -- the HSV detector should classify it as "Gram+"
2. Point it at something pink -- it should classify as "Gram-"
3. Point it at a plain white surface -- it should say "No Bacteria"

This confirms the color detection pipeline is working correctly.

### Running the Automated Staining Sequence

If your hardware is fully assembled (solenoid valves, pump, reagent containers):

1. Place a water sample in the collection chamber
2. Press `s` on your keyboard (with the video window in focus)
3. The Arduino will run through the full Gram stain protocol automatically:
   - Sample loading via peristaltic pump (5 seconds)
   - Settle time (2 minutes)
   - Crystal Violet stain (60 seconds + wash)
   - Iodine mordant (60 seconds + wash)
   - Decolorizer (10 seconds + wash)
   - Safranin counterstain (60 seconds + wash)
4. After staining completes, the system will capture an image and classify the bacteria
5. The result appears on both the laptop screen and the Arduino LCD

The entire staining sequence takes approximately 8 minutes.

---

# Part 2 -- Configuration Guide (Customize It)

All settings live in one file: **`python/config.py`**

Open it in any text editor (Notepad on Windows, TextEdit on Mac, or any code editor like VS Code). Every setting has a comment above it explaining what it does.

---

## All Settings in config.py

### Core Settings

| Setting | Default | What It Does |
|---------|---------|-------------|
| `SERIAL_PORT` | `"COM3"` | Which USB port the Arduino is connected to |
| `SERIAL_BAUD` | `9600` | Communication speed with Arduino (don't change this unless you also change it in the Arduino sketch) |
| `CAMERA_INDEX` | `0` | Which camera to use (0 = first camera, 1 = second, etc.) |
| `AI_MODEL_PATH` | `models/bioqua_model.h5` | Where the trained AI model file is saved |
| `CLASS_NAMES` | 5 bacteria classes | The names of bacteria types the AI can recognize |

### Sensor Thresholds

| Setting | Default | What It Does |
|---------|---------|-------------|
| `PH_NORMAL_MIN` | `6.5` | pH below this is considered abnormal |
| `PH_NORMAL_MAX` | `8.5` | pH above this is considered abnormal |
| `EC_NORMAL_MAX` | `1500` | EC above this (in microsiemens/cm) means high dissolved solids |

These values follow the WHO drinking water guidelines. Change them if your research uses different standards.

### Gram Stain Timings

| Setting | Default | What It Does |
|---------|---------|-------------|
| `STAIN_CRYSTAL_VIOLET` | `60` seconds | How long the primary purple stain is applied |
| `STAIN_IODINE` | `60` seconds | How long the iodine mordant is applied |
| `STAIN_DECOLORIZER` | `10` seconds | How long the decolorizer runs -- **this is the most sensitive timing**. Too long and everything turns pink (false Gram-negative). Too short and everything stays purple (false Gram-positive). |
| `STAIN_SAFRANIN` | `60` seconds | How long the pink counterstain is applied |
| `WASH_DURATION` | `15` seconds | How long the DI water rinse runs between each step |
| `SETTLE_DURATION` | `120` seconds | How long bacteria settle onto the slide before staining begins |

### AI Settings

| Setting | Default | What It Does |
|---------|---------|-------------|
| `AI_CONFIDENCE_THRESHOLD` | `0.6` (60%) | If the AI is less confident than this, it reports "Uncertain" instead of guessing. Increase to 0.8 for stricter results, decrease to 0.4 to get classifications more often (but less reliable). |
| `AI_IMAGE_SIZE` | `(224, 224)` | The image size the model expects. Don't change this unless you trained with a different size. Google Teachable Machine uses 224x224. |

### HSV Color Ranges

These define what counts as "purple" and "pink" in the microscope image. The values are in HSV (Hue, Saturation, Value) color space.

| Setting | Default | What It Detects |
|---------|---------|----------------|
| `HSV_GRAM_POSITIVE` | `((120, 50, 50), (160, 255, 255))` | Purple pixels (Gram-positive bacteria) |
| `HSV_GRAM_NEGATIVE_1` | `((0, 50, 100), (20, 255, 255))` | Pink pixels, low hue range |
| `HSV_GRAM_NEGATIVE_2` | `((160, 50, 100), (180, 255, 255))` | Pink pixels, high hue range |

If your microscope lighting makes purple look bluer or pinker than expected, you may need to adjust these. A good approach is to capture an image, open it in a tool that shows HSV values (like an online color picker), and check what hue range your stained bacteria actually fall into.

### Shape Classification

| Setting | Default | What It Does |
|---------|---------|-------------|
| `CIRCULARITY_COCCI` | `0.7` | Shapes rounder than this are classified as cocci (round bacteria) |
| `ASPECT_RATIO_BACILLI` | `2.0` | Shapes more elongated than this are classified as bacilli (rod-shaped bacteria) |
| `MIN_CONTOUR_AREA` | `50` | Shapes smaller than this (in pixels) are ignored as noise |

### Arduino Pin Assignments

| Setting | Default | What It Does |
|---------|---------|-------------|
| `RELAY_PINS` | `{"crystal_violet": 2, "iodine": 3, ...}` | Which digital pins control which relay channels |
| `LCD_ADDRESS` | `0x27` | I2C address of the LCD. Try `0x3F` if the LCD doesn't work |

---

## How to Find Your Serial Port

The serial port name is different on every computer. Here is how to find yours:

### Windows

1. Plug in the Arduino via USB
2. Right-click the Start button, click **Device Manager**
3. Expand **Ports (COM & LPT)**
4. You will see something like: `Arduino Mega 2560 (COM3)` or `USB-SERIAL CH340 (COM4)`
5. The `COMx` part is your serial port. Put it in config.py:
   ```python
   SERIAL_PORT = "COM3"  # Change the number to match yours
   ```

### Mac

1. Plug in the Arduino via USB
2. Open Terminal
3. Run: `ls /dev/tty.*`
4. Look for something like `/dev/tty.usbmodem14201` or `/dev/tty.usbserial-1420`
5. Copy the full path into config.py:
   ```python
   SERIAL_PORT = "/dev/tty.usbmodem14201"
   ```

### Linux

1. Plug in the Arduino via USB
2. Open a terminal
3. Run: `ls /dev/ttyUSB*` or `ls /dev/ttyACM*`
4. You will see something like `/dev/ttyUSB0` or `/dev/ttyACM0`
5. Put it in config.py:
   ```python
   SERIAL_PORT = "/dev/ttyUSB0"
   ```
6. You may also need to add yourself to the `dialout` group: `sudo usermod -a -G dialout $USER` (then log out and back in)

---

## Feature Toggles

BIOQUA has optional features that are all turned OFF by default. Turn them on one at a time when you're ready.

| Feature | Setting | What It Adds |
|---------|---------|-------------|
| Data Logging | `FEATURE_DATA_LOGGING = True` | Saves every test result to a CSV file (`results/test_log.csv`) and captures images. Open the CSV in Excel or Google Sheets to see trends. |
| PDF Reports | `FEATURE_PDF_REPORTS = True` | Press `r` during a test to generate a printable PDF report with charts and tables. Requires: `pip install fpdf2 matplotlib` |
| Modular Sensors | `FEATURE_MODULAR_SENSORS = True` | Extensibility hook for future sensor plug-ins. Not part of BIOQUA's core methodology and disabled in the prototype. Future researchers can add sensors by writing a class under `sensors/` and registering it in `sensors/__init__.py`. |
| Learning Modules | `FEATURE_LEARNING_MODULES = True` | Interactive terminal-based educational guides about Gram staining, bacteria shapes, AI, water quality, and risk assessment. |
| Bluetooth Mobile | `FEATURE_BLUETOOTH_MOBILE = True` | Sends results to your phone via Bluetooth using an ESP32 module. Requires ESP32 hardware and the companion app. |

To enable a feature, open `python/config.py` and change `False` to `True`:

```python
# Before
FEATURE_DATA_LOGGING = False

# After
FEATURE_DATA_LOGGING = True
```

---

## How to Add New Bacteria Classes

If you want BIOQUA to recognize additional types of bacteria:

1. **Create a new folder** in `training_data/` with a descriptive name (e.g., `spirillum` or `filamentous`)
2. **Collect images** of that bacteria type (at least 30 images, ideally 50+):
   - Use `python capture_images.py` and manually sort images, OR
   - Use the microscope software to save images directly into the folder
3. **Update config.py** -- add the new class name to the `CLASS_NAMES` list:
   ```python
   CLASS_NAMES = [
       "Gram+ Cocci",
       "Gram+ Bacilli",
       "Gram- Cocci",
       "Gram- Bacilli",
       "No Bacteria",
       "Spirillum",  # Your new class
   ]
   ```
4. **Retrain the model** (see next section)

---

## How to Retrain the AI

### Option A: Train with the built-in script (MobileNetV2 transfer learning)

1. Make sure you have images in `training_data/` folders (at least 20 per class, ideally 30-50)
2. Run:
   ```
   python train_model.py
   ```
3. Training takes 5-15 minutes. When it finishes, you will see the accuracy percentage.
4. The new model is saved to `models/bioqua_model.h5` and will be used automatically next time you run `controller.py`

### Option B: Train with Google Teachable Machine (easier, visual)

1. Go to **https://teachablemachine.withgoogle.com/**
2. Click **"Get Started"** then choose **"Image Project"** > **"Standard image model"**
3. Create a class for each bacteria type (Gram+ Cocci, Gram+ Bacilli, etc.)
4. Upload your training images into each class
5. Click **"Train Model"** (this happens in your browser, no install needed)
6. After training, click **"Export Model"** > **"TensorFlow"** > **"Keras"** > **"Download"**
7. Unzip the download and copy the `.h5` file to `models/bioqua_model.h5` (replacing the old one)

### Option C: Train the feature extraction classifier (most explainable)

This method is the best for your science report because you can explain exactly how it works.

1. Make sure you have images in `training_data/` folders
2. Run:
   ```
   python feature_extraction.py train
   ```
3. This trains a Random Forest classifier on 5 measurable features (purple ratio, pink ratio, circularity, aspect ratio, bacteria count)
4. The output will show you exactly how important each feature is
5. The model is saved to `models/bioqua_features_model.pkl`

---

## How to Switch Between AI Options

BIOQUA has three ways to classify bacteria, from simplest to most advanced:

| Method | When It's Used | Best For |
|--------|---------------|----------|
| **HSV Color Detection** | Automatically used when no AI model exists | Quick testing, understanding the basics |
| **Feature Extraction (Random Forest)** | When `bioqua_features_model.pkl` exists | Science reports (fully explainable) |
| **Deep Learning (MobileNetV2)** | When `bioqua_model.h5` exists | Best accuracy |

The controller automatically uses the deep learning model if it exists. To force it to use HSV-only detection, temporarily rename or move the model file:

```
# On Windows:
ren models\bioqua_model.h5 models\bioqua_model.h5.bak

# On Mac/Linux:
mv models/bioqua_model.h5 models/bioqua_model.h5.bak
```

To use the feature extraction classifier instead, you would modify `controller.py` to load the `.pkl` model -- but for most purposes, just use `feature_extraction.py` directly for analysis and reporting.

---

# Part 3 -- Troubleshooting FAQ

Find your problem below and follow the fix.

---

### "Camera not detected" / No working cameras found

**Try this:**

1. Unplug the USB microscope and plug it back in
2. Wait 5 seconds, then run `python test_camera.py` again
3. Try a different USB port on your laptop
4. On Windows: open Device Manager and check under "Cameras" -- is the microscope listed?
5. On Mac: go to System Settings > Privacy & Security > Camera -- is Terminal allowed?
6. Try a different USB cable (some cables are charge-only and don't carry data)
7. If your laptop has a built-in webcam, the microscope might be at index 1 or 2 instead of 0. Run the camera test and note which index shows the microscope.

---

### "Serial port not found" / Could not open port

**Try this:**

1. **Close Arduino IDE's Serial Monitor.** This is the most common cause. Only one program can use the serial port at a time.
2. Unplug the Arduino USB cable and plug it back in
3. Run `python test_serial.py` -- it will list all available ports. Copy the correct one into `SERIAL_PORT` in config.py.
4. On Windows: check Device Manager > Ports. If you don't see the Arduino, install the CH340 driver (search "CH340 driver" online).
5. On Mac: run `ls /dev/tty.*` and look for the Arduino.
6. On Linux: you may need permission. Run `sudo usermod -a -G dialout $USER` then log out and back in.

---

### "Arduino upload failed" / avrdude timeout

**Try this:**

1. Make sure **Tools > Board** is set to **"Arduino Mega or Mega 2560"** (not Uno, not Nano)
2. Make sure **Tools > Port** shows your Arduino (unplug/replug if it doesn't appear)
3. Make sure **Tools > Processor** is set to **"ATmega2560 (Mega 2560)"**
4. Try a different USB cable
5. Try a different USB port
6. If you get "permission denied" on Mac/Linux, you may need to allow the USB device in System Settings

---

### "AI says wrong classification" / results don't match what I see

**Try this:**

1. **Check your training data.** Are the images in the correct folders? Open a few and visually confirm they match the folder name.
2. **Collect more images.** The AI needs at least 30 images per class to learn well. More is better.
3. **Check image quality.** Blurry, dark, or overexposed images confuse the AI. Only use well-focused, well-lit images.
4. **Check the confidence percentage.** If it's below 60%, the AI is not sure. This means the image might be ambiguous.
5. **Retrain the model** after adding more images: `python train_model.py`
6. **Lower the confidence threshold** temporarily to see what the AI thinks: change `AI_CONFIDENCE_THRESHOLD = 0.4` in config.py. This will give you more classifications, but some may be wrong.
7. **Use the feature extraction method** (`python feature_extraction.py explain`) to understand what the AI is actually seeing in the image.

---

### "Solenoid valves not working" / relays click but nothing flows

**Try this:**

1. **Check the external 12V power supply.** Solenoid valves need 12V to open -- the Arduino cannot power them. Make sure your 12V supply is plugged in and turned on.
2. **Check the relay module LED indicators.** When a relay is activated, an LED on the relay board should light up.
3. **Test one relay at a time.** In Arduino IDE, open Serial Monitor, type `S` and press Enter. Watch which relay LEDs light up during the staining sequence.
4. **Check wiring.** Make sure the valve's positive wire goes through the relay's NO (Normally Open) terminal and the COM (Common) terminal is connected to the 12V supply.
5. **Check valve direction.** Some solenoid valves only flow in one direction. Look for an arrow on the valve body.

---

### "LCD shows weird characters" / LCD shows nothing / LCD backlight on but blank

**Try this:**

1. **Adjust the contrast potentiometer.** On the back of the I2C adapter board, there is a small blue screw (potentiometer). Turn it slowly with a small screwdriver until text appears.
2. **Check the I2C address.** Open `arduino/bioqua_controller/bioqua_controller.ino` and look for this line:
   ```
   LiquidCrystal_I2C lcd(0x27, 20, 4);
   ```
   Try changing `0x27` to `0x3F` and re-upload the sketch. These are the two most common I2C addresses.
3. **Check wiring.** SDA goes to pin 20 on the Mega, SCL goes to pin 21.
4. **Run an I2C scanner.** In Arduino IDE, go to File > Examples > Wire > i2c_scanner, upload it, open Serial Monitor, and it will tell you the exact address of your LCD.

---

### "Staining results wrong" / everything looks purple or everything looks pink

**Try this:**

1. **Decolorizer timing is the most critical.** If everything is purple: decolorizer didn't run long enough. Increase `STAIN_DECOLORIZER` from 10 to 15 seconds. If everything is pink: decolorizer ran too long. Decrease it to 5-8 seconds.
2. **Check reagent bottles.** Are they connected to the correct valves? Crystal Violet to Relay 1 (D2), Iodine to Relay 2 (D3), Decolorizer to Relay 3 (D4), Safranin to Relay 4 (D5), DI Water to Relay 5 (D6).
3. **Check reagent freshness.** Old reagents (especially Crystal Violet and Safranin) lose potency. If they look faded, replace them.
4. **Check flow rate.** If tubes are kinked or reservoirs are low, reagent may not reach the slide.
5. **Manual staining test.** Try staining a slide manually (with a dropper) to verify reagents work, then compare against the automated result.

---

### "Python ModuleNotFoundError" / No module named 'xxx'

**Try this:**

| Error Message | Fix |
|--------------|-----|
| `No module named 'cv2'` | `pip install opencv-python` |
| `No module named 'numpy'` | `pip install numpy` |
| `No module named 'tensorflow'` | `pip install tensorflow` |
| `No module named 'serial'` | `pip install pyserial` (note: it's pyserial, not serial) |
| `No module named 'sklearn'` | `pip install scikit-learn` |
| `No module named 'fpdf'` | `pip install fpdf2` |
| `No module named 'matplotlib'` | `pip install matplotlib` |

If `pip install` doesn't seem to work (you install it but the error persists):
- You might have multiple Python versions. Try `pip3 install` instead of `pip install`.
- On Windows, try `python -m pip install opencv-python` instead.

---

### "General errors I don't understand" / red text in the terminal

**Try this:**

1. **Read the last line of the error.** Python errors show a "traceback" (a chain of locations in the code). The most important part is always the **very last line** -- that's the actual error message.
2. **Common patterns:**
   - `FileNotFoundError`: A file or folder is missing. Check the path mentioned in the error.
   - `PermissionError`: You don't have access. On Windows, try running as Administrator. On Mac/Linux, check file permissions.
   - `ConnectionRefusedError` or `SerialException`: The Arduino isn't connected or the port is in use.
   - `ValueError`: A calculation got unexpected data. Usually means a sensor returned garbage.
3. **Copy the last line of the error and search for it online.** Paste it into Google with "Python" in front of it. Someone has almost certainly had the same problem.
4. **Check that you are in the right folder.** Make sure your terminal is in the `python/` folder within the BIOQUA project when running commands.

---

# Part 4 -- Science Report Helper

This section explains the science and technology behind BIOQUA in plain language. Use it to help write your research paper or presentation.

---

## What Is AI?

AI (Artificial Intelligence) is when a computer learns to do something that normally requires human judgment.

You already use AI every day, probably without realizing it:

- **Spam filter in email.** Your email app learned what spam looks like by seeing millions of examples of spam and not-spam emails. Now it can look at a new email and decide: spam or not spam?
- **Face unlock on your phone.** Your phone learned what your face looks like by studying the pictures you took during setup. Now it compares your live face to what it learned.
- **Autocomplete when you type.** Your keyboard predicts the next word based on patterns it learned from billions of sentences.

All of these work the same way: the computer is given many examples, it finds patterns, and then it uses those patterns to make decisions about new data it hasn't seen before.

BIOQUA's AI works the same way. Instead of emails or faces, it learned from microscope images. It studied hundreds of pictures of different bacteria types and learned: "purple and round = Gram-positive cocci," "pink and rod-shaped = Gram-negative bacilli," and so on. Now when it sees a new microscope image, it can classify the bacteria.

---

## How BIOQUA's AI Sees Bacteria

The AI does not "see" the way humans do. It sees numbers.

### Color Detection -- The M&Ms Analogy

Imagine you have a bowl of M&Ms and someone asks you to sort them by color. You would look at each M&M and put it in a pile: red, blue, green, yellow, etc.

BIOQUA does the same thing, but with pixels instead of M&Ms.

A microscope image is made up of thousands of tiny colored squares called pixels. Each pixel has a color described by three numbers (Hue, Saturation, Value). BIOQUA counts how many pixels fall into the "purple" range and how many fall into the "pink" range:

- **Lots of purple pixels?** That means Crystal Violet stain was retained -- Gram-positive bacteria.
- **Lots of pink pixels?** That means the Crystal Violet washed away and Safranin was picked up -- Gram-negative bacteria.
- **Very few colored pixels?** No bacteria detected.

This is exactly like sorting M&Ms: count the purple ones and count the pink ones. Whichever pile is bigger tells you the dominant bacteria type.

### Shape Detection -- Circles vs Rectangles

After determining the color (Gram type), BIOQUA looks at the shapes of the bacteria.

Think of it like this: if someone draws shapes on a whiteboard and asks you "is it a circle or a rectangle?", you would look at how round versus how stretched-out it is.

BIOQUA does the same thing with two measurements:

- **Circularity** (0 to 1): How close to a perfect circle is the shape? A perfect circle scores 1.0. A long thin rod scores closer to 0.3. Bacteria that score above 0.7 are classified as **cocci** (round bacteria like Staphylococcus).
- **Aspect Ratio**: Width divided by height. A square = 1.0. A shape that is 3 times wider than it is tall = 3.0. Bacteria with aspect ratio above 2.0 are classified as **bacilli** (rod-shaped bacteria like E. coli).

---

## What Is Transfer Learning?

Training an AI from scratch requires millions of images and powerful computers. High school students don't have that.

Transfer learning is the shortcut.

### The "Dog Learning New Tricks" Analogy

Imagine you have a dog that already knows how to sit, stay, and shake. If you want to teach it a new trick -- say, rolling over -- you don't start from zero. The dog already understands commands, rewards, and body movements. Teaching it one new thing is much faster than training a puppy that knows nothing.

Transfer learning works the same way. BIOQUA uses a model called **MobileNetV2** that was already trained on 1.4 million photographs. It already learned what edges, colors, textures, and shapes look like. It "knows" the basics of seeing.

All BIOQUA does is add a small new layer on top and teach it: "these particular colors and shapes mean Gram-positive cocci." Because the foundation is already solid, BIOQUA only needs 30-50 images per class instead of millions.

**In your report, you can say:**
> "The system uses transfer learning with a pre-trained MobileNetV2 convolutional neural network. The base model, trained on the ImageNet dataset (1.4 million images), provides general visual feature extraction. A custom classification head was added and fine-tuned on our bacteria image dataset."

---

## What Is Gram Staining?

Gram staining is a 150-year-old laboratory technique invented by Hans Christian Gram in 1884. It is still one of the most important tests in microbiology because it splits nearly all bacteria into two major groups based on their cell wall structure.

### The Procedure (4 Steps)

| Step | Reagent | Time | What Happens |
|------|---------|------|-------------|
| 1 | Crystal Violet (purple dye) | 60 sec | All bacteria turn purple |
| 2 | Iodine (mordant) | 60 sec | Locks the purple dye into the cell wall |
| 3 | Decolorizer (alcohol/acetone) | 10 sec | Strips the purple from thin-walled bacteria |
| 4 | Safranin (pink dye) | 60 sec | Pink dye fills in bacteria that lost the purple |

### The Result

- **Gram-positive bacteria** have a thick cell wall (peptidoglycan layer). The Crystal Violet gets trapped inside and can't be washed out by the decolorizer. They stay **purple**.
- **Gram-negative bacteria** have a thin cell wall with an outer membrane. The decolorizer dissolves the outer membrane and washes the Crystal Violet away. Then the Safranin counterstain fills in and they turn **pink**.

### Why It Matters for Water Safety

Many dangerous waterborne pathogens are Gram-negative, including E. coli, Salmonella, and Cholera (Vibrio cholerae). Detecting Gram-negative bacteria in a water sample is an important indicator of potential contamination.

---

## How to Present Accuracy (Confusion Matrix)

When you report how well your AI works, you need to show more than just "it got 85% right." A confusion matrix shows exactly what types of mistakes the AI makes.

### What Is a Confusion Matrix?

A confusion matrix is a table that compares what the AI predicted versus what the actual answer was.

Here is an example for a simple 3-class system:

```
                        AI Predicted:
                   Gram+    Gram-    None
Actual:
  Gram+             28       2        0       (93% correct)
  Gram-              1      27        2       (90% correct)
  None               0       1       29       (97% correct)
```

Reading this table:
- Row 1: Out of 30 actual Gram-positive samples, the AI correctly called 28 "Gram+", mistakenly called 2 "Gram-", and never said "None." So it was 93% accurate on Gram-positive samples.
- Row 2: Out of 30 actual Gram-negative samples, the AI correctly identified 27, confused 1 for Gram+, and missed 2 completely. That's 90% accuracy.
- Row 3: Out of 30 actual clean samples, the AI got 29 right and mistakenly detected bacteria once. 97% accuracy.

### How to Generate It

Run `python feature_extraction.py train` -- it automatically prints a classification report with precision, recall, and F1-score per class. You can include that output directly in your paper.

### What to Say in Your Report

Don't just report the overall accuracy number. Explain the trade-offs:

> "The classifier achieved an overall accuracy of 93.3% across 90 test images. Gram-negative bacteria were the most commonly misclassified category, with 2 out of 30 samples missed. This is significant because Gram-negative misses (false negatives) could lead to unsafe water being classified as safe. Future work should focus on increasing the Gram-negative detection sensitivity."

---

## Suggested Report Structure

Here is a recommended outline for your science research paper or investigatory project report.

### I. Title
> BIOQUA: AI-Assisted Water Quality Monitoring System

### II. Abstract (1 paragraph, ~150 words)
Summarize the problem, your approach, and your main results. Write this last.

### III. Introduction
- The problem: waterborne diseases, lack of affordable water testing in rural areas
- Existing solutions and their limitations (lab testing is expensive and slow)
- Your proposed solution: a low-cost, automated system using AI and Arduino

### IV. Review of Related Literature
- Gram staining history and procedure
- AI and image classification (cite Teachable Machine or MobileNetV2)
- Transfer learning
- Arduino-based water monitoring systems (search Google Scholar for similar projects)

### V. Methodology
- Hardware components (Arduino Mega, sensors, solenoid valves, LCD, microscope)
- Software components (Python, OpenCV, TensorFlow, serial communication)
- The automated Gram staining process
- AI training process (how many images, what model, what parameters)
- Testing protocol (how you collected water samples, how many tests)

### VI. Results and Discussion
- Confusion matrix (see above)
- Accuracy per class
- Sensor calibration results (pH and EC readings vs lab-verified values)
- Example classifications with images
- Limitations: what didn't work well, what would you improve?

### VII. Conclusion
- Summary of what you built and what it achieved
- Real-world applicability
- Recommendations for future work

### VIII. References
Cite everything. Include URLs for software (Python, Arduino IDE, TensorFlow), papers you read, and data sources.

---

## Key Vocabulary List

Use these terms correctly in your report.

| Term | Definition |
|------|-----------|
| **Artificial Intelligence (AI)** | A computer system that can perform tasks normally requiring human intelligence, such as visual recognition or decision-making |
| **Machine Learning** | A subset of AI where the computer learns patterns from data rather than being explicitly programmed |
| **Transfer Learning** | A technique where a model trained on a large general dataset is adapted for a specific task using a smaller dataset |
| **Convolutional Neural Network (CNN)** | A type of deep learning model designed for image recognition that detects features like edges, colors, and shapes |
| **MobileNetV2** | A lightweight CNN architecture designed by Google for mobile and embedded devices |
| **Classification** | The task of assigning a label (category) to an input. In BIOQUA, the input is a microscope image and the labels are bacteria types |
| **Confidence Score** | A number from 0% to 100% representing how certain the AI is about its classification |
| **HSV Color Space** | A way of representing colors using Hue (what color), Saturation (how vivid), and Value (how bright). Used in computer vision because it separates color from brightness |
| **Contour** | The outline of a shape detected in an image. Used to measure circularity and aspect ratio |
| **Circularity** | A measure of how round a shape is, calculated as 4 x pi x Area / Perimeter squared. A perfect circle = 1.0 |
| **Aspect Ratio** | Width divided by height of a shape's bounding rectangle. Circles have ~1.0, rods have >2.0 |
| **Gram Staining** | A differential staining technique that classifies bacteria as Gram-positive (purple, thick cell wall) or Gram-negative (pink, thin cell wall) |
| **Peptidoglycan** | A polymer that forms the main structural component of bacterial cell walls. Gram-positive bacteria have a thick peptidoglycan layer |
| **Mordant** | A substance (iodine in Gram staining) that fixes a dye to a material, making it harder to wash out |
| **Decolorizer** | A solvent (usually ethanol or acetone) that removes Crystal Violet from Gram-negative bacteria |
| **Counterstain** | A second dye (Safranin in Gram staining) that stains cells that lost the primary stain |
| **Cocci** | Spherical (round) bacteria. Singular: coccus |
| **Bacilli** | Rod-shaped bacteria. Singular: bacillus |
| **Spirilla** | Spiral-shaped bacteria. Singular: spirillum |
| **pH** | A measure of how acidic or alkaline a solution is, on a scale of 0 (very acidic) to 14 (very alkaline). Pure water is 7.0 (neutral) |
| **Electrical Conductivity (EC)** | A measure of water's ability to conduct electricity, measured in microsiemens per centimeter. Higher EC = more dissolved minerals |
| **Random Forest** | A machine learning algorithm that makes predictions by building many decision trees and averaging their votes |
| **Data Augmentation** | A technique where training images are slightly modified (rotated, flipped, zoomed) to create more training variety without collecting new images |
| **Overfitting** | When a model memorizes the training data instead of learning general patterns. It scores well on training data but poorly on new data |
| **Confusion Matrix** | A table comparing the AI's predictions against actual labels, showing exactly where it makes mistakes |
| **Precision** | Of all samples the AI labeled as class X, what percentage actually were class X |
| **Recall** | Of all actual class X samples, what percentage did the AI correctly identify |
| **Microcontroller** | A small computer on a single chip (the Arduino Mega uses an ATmega2560) that reads sensors and controls hardware |
| **Serial Communication** | A method of sending data one bit at a time over a wire. The Arduino and laptop communicate over USB serial at 9600 baud |
| **Relay Module** | An electrically operated switch that allows a low-power signal (Arduino 5V) to control a high-power device (12V solenoid valve) |
| **Solenoid Valve** | An electronically controlled valve that opens or closes when electrical current flows through it |
| **Peristaltic Pump** | A pump that moves fluid by squeezing a flexible tube. Used in BIOQUA to move water and reagents without contamination |

---

## Sample Sentences You Can Adapt

These are example sentences you can modify for your own report. Replace the bracketed parts with your actual data.

### For the Introduction

> "According to the World Health Organization, approximately 2 billion people worldwide use a drinking water source contaminated with feces (WHO, 2019). Traditional laboratory testing for bacterial contamination requires trained technicians and equipment costing thousands of dollars, making it inaccessible in many developing communities."

> "This study developed BIOQUA, a low-cost automated system that combines Arduino-controlled hardware with artificial intelligence to detect and classify bacteria in water samples."

### For the Methodology

> "The system uses an Arduino Mega 2560 microcontroller connected to a pH sensor (analog pin A0), a TDS/EC sensor (analog pin A1), a 6-channel relay module (digital pins D2-D7) controlling five solenoid valves and one peristaltic pump, and a 20x4 I2C LCD display."

> "Bacteria classification was performed using transfer learning with a MobileNetV2 convolutional neural network pre-trained on the ImageNet dataset. The final classification layer was replaced with a custom dense layer trained on [number] microscope images across [number] classes."

> "Training images were augmented using random rotation (up to 20 degrees), horizontal and vertical flipping, and zoom (up to 15%). Color augmentation was intentionally excluded to preserve Gram stain color information."

> "An alternative explainable classifier was also developed using a Random Forest algorithm trained on five extracted features: purple pixel ratio, pink pixel ratio, average circularity, average aspect ratio, and bacteria count."

### For the Results

> "The MobileNetV2 classifier achieved [X]% validation accuracy after 15 epochs of training on [X] images. The confusion matrix revealed that Gram-negative bacilli were the most reliably classified category at [X]% recall, while [category] had the lowest recall at [X]%."

> "Feature importance analysis from the Random Forest classifier showed that [feature name] was the most influential feature (importance score: [X]), followed by [feature name] ([X])."

> "The pH sensor readings were within [+/- X] of laboratory-verified values across [X] calibration samples. EC readings showed a linear correlation with laboratory measurements (R squared = [X])."

### For the Discussion

> "The decolorizer timing was found to be the most critical variable in the automated Gram staining process. A timing of 10 seconds produced results consistent with manual staining, while timings above 15 seconds caused false Gram-negative classifications due to over-decolorization."

> "The feature extraction classifier, while slightly less accurate than the deep learning model ([X]% vs [X]%), offers the advantage of full explainability. Each prediction can be traced to specific measurable features, which is important for scientific transparency."

### For the Conclusion

> "BIOQUA demonstrates that AI-powered bacteria detection is feasible using low-cost hardware. The total material cost of approximately [amount] is significantly less than traditional laboratory equipment, suggesting potential applicability in resource-limited settings."

> "Future improvements could include adding additional bacteria classes, implementing real-time model updates through continued learning, and developing a mobile application for field use."

---

**End of Manual**

For questions or issues not covered here, review the source code comments in the `python/` folder -- every script has detailed documentation at the top explaining what it does and how to use it.
