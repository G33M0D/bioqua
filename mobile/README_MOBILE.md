# BIOQUA Mobile Bluetooth Dashboard

This guide covers two ways to view BIOQUA sensor data on your phone:

1. **MIT App Inventor** -- build a custom dashboard app (recommended for the full project)
2. **Serial Bluetooth Terminal** -- quick testing with no coding required

---

## Prerequisites

- ESP32 board flashed with `esp32_bluetooth.ino`
- Android phone with Bluetooth (Classic/SPP, not just BLE)
- The ESP32 must be powered on and advertising as **BIOQUA-ESP32**

---

## Option 1: MIT App Inventor Dashboard

### Account Setup

1. Go to [appinventor.mit.edu](https://appinventor.mit.edu)
2. Sign in with a Google account
3. Click **Start new project** and name it `BIOQUA`
4. Install the **MIT AI2 Companion** app on your phone from the Play Store

### Designer View -- Building the UI

Add these components from the palette:

| Component | Name | Properties |
|-----------|------|------------|
| Label | `lblTitle` | Text: "BIOQUA Dashboard", FontSize: 24, FontBold: true |
| HorizontalArrangement | `rowPH` | Width: Fill parent |
| Label (inside rowPH) | `lblPHLabel` | Text: "pH:" |
| Label (inside rowPH) | `lblPHValue` | Text: "---", FontSize: 20 |
| Slider | `sliderPH` | MinValue: 0, MaxValue: 14, Width: Fill parent, Enabled: false |
| HorizontalArrangement | `rowEC` | Width: Fill parent |
| Label (inside rowEC) | `lblECLabel` | Text: "EC (uS/cm):" |
| Label (inside rowEC) | `lblECValue` | Text: "---", FontSize: 20 |
| Slider | `sliderEC` | MinValue: 0, MaxValue: 2000, Width: Fill parent, Enabled: false |
| Label | `lblRisk` | Text: "Risk: ---", FontSize: 22, FontBold: true |
| Label | `lblBacteria` | Text: "Bacteria: ---", FontSize: 18 |
| Label | `lblStatus` | Text: "Status: IDLE", FontSize: 16 |
| ListPicker | `btnConnect` | Text: "Connect to ESP32" |
| Button | `btnDisconnect` | Text: "Disconnect" |
| BluetoothClient | `btClient` | (non-visible, drag from Connectivity palette) |
| Clock | `clockReceive` | TimerInterval: 500, TimerEnabled: true |
| Button | `btnClassify` | Text: "Send Classification" (optional — for manual result sending) |

### Blocks View -- Programming the Logic

#### 1. Populate Bluetooth device list on tap

```
when btnConnect.BeforePicking
  set btnConnect.Elements to btClient.AddressesAndNames
```

#### 2. Connect to selected device

```
when btnConnect.AfterPicking
  call btClient.Connect (address: btnConnect.Selection)
```

#### 3. Disconnect

```
when btnDisconnect.Click
  call btClient.Disconnect
```

#### 4. Receive and parse data (runs every 500ms)

```
when clockReceive.Timer
  if btClient.IsConnected then
    if btClient.BytesAvailableToReceive > 0 then
      set local dataLine to call btClient.ReceiveText (numberOfBytes: -1)
      -- Parse "pH:7.20,EC:450.0,status:IDLE"
      set local pairs to split dataLine at ","
      for each pair in pairs
        set local kv to split pair at ":"
        if select list item kv index 1 = "pH" then
          set lblPHValue.Text to select list item kv index 2
          set sliderPH.ThumbPosition to select list item kv index 2
        else if select list item kv index 1 = "EC" then
          set lblECValue.Text to select list item kv index 2
          set sliderEC.ThumbPosition to select list item kv index 2
        else if select list item kv index 1 = "status" then
          set lblStatus.Text to join "Status: " select list item kv index 2
        else if select list item kv index 1 = "risk" then
          set lblRisk.Text to join "Risk: " select list item kv index 2
        else if select list item kv index 1 = "bacteria" then
          set lblBacteria.Text to join "Bacteria: " select list item kv index 2
        end if
      end for
    end if
  end if
```

#### 5. Send classification result back to ESP32

After running your ML model (or manual classification), send a result string:

```
when btnClassify.Click
  if btClient.IsConnected then
    call btClient.SendText (text: join "result:CONTAMINATED,bacteria:E.coli,risk:HIGH" "\n")
  end if
```

Replace the hardcoded values with your actual classification output.

#### 6. Color-code the risk label

```
when clockReceive.Timer (add to existing block)
  -- After parsing, update risk color
  if lblRisk.Text contains "HIGH" then
    set lblRisk.TextColor to red
  else if lblRisk.Text contains "MODERATE" then
    set lblRisk.TextColor to orange
  else if lblRisk.Text contains "LOW" then
    set lblRisk.TextColor to green
  end if
```

### Building and Installing

1. In App Inventor, go to **Connect > AI Companion**
2. Scan the QR code with the MIT AI2 Companion app to live-test
3. When ready, go to **Build > Android App (.apk)** to download the installable APK
4. Transfer the APK to your phone and install (enable "Install from unknown sources" in Settings)

---

## Option 2: Serial Bluetooth Terminal (Quick Testing)

This requires zero coding and works in under 2 minutes.

### Steps

1. Install **Serial Bluetooth Terminal** by Kai Morich from the Google Play Store
   (free, no account required)
2. Open your phone's **Bluetooth Settings**
3. Tap **Pair new device** and select **BIOQUA-ESP32**
   - PIN if prompted: `1234` (ESP32 default)
4. Open the Serial Bluetooth Terminal app
5. Tap the menu (three lines) > **Devices** > select **BIOQUA-ESP32**
6. Tap the **Connect** button (plug icon)
7. You should see incoming lines like:
   ```
   pH:7.20,EC:450.0,status:IDLE
   pH:7.18,EC:452.3,status:IDLE
   ```
8. To send a classification result back, type in the input field:
   ```
   result:SAFE,bacteria:None,risk:LOW
   ```
   and tap Send. The ESP32 LCD will update accordingly.

### Tips for Serial Bluetooth Terminal

- Set line ending to **Newline (LF)** under Settings > Send
- Enable **Timestamp** display to track reading intervals
- Use **Log** feature to save a session for later analysis

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| ESP32 not appearing in Bluetooth scan | Make sure the sketch is uploaded and running. Check the Serial Monitor at 115200 baud for "Bluetooth ready" message. |
| Connected but no data received | Verify the ESP32 is sending (check Serial Monitor for "BT TX:" lines). Ensure sensors are wired to GPIO 36 and 39. |
| pH reads 0.00 or 14.00 | The reading is being clamped. Check wiring and recalibrate PH_OFFSET and PH_SLOPE with buffer solutions. |
| EC reads 0.0 | Check EC probe wiring to GPIO 39. Verify EC_KVALUE matches your probe's cell constant. |
| App Inventor cannot find BluetoothClient | Make sure you dragged it from the **Connectivity** section in the palette, not the Sensors section. |
| "Error 507: Unable to connect" in App Inventor | The ESP32 may already be connected to another device. Bluetooth SPP only allows one connection at a time. Disconnect from the other device first. |

---

## Data Format Reference

### ESP32 sends (every 2 seconds):
```
pH:<float>,EC:<float>,status:<string>\n
```
Example: `pH:7.20,EC:450.0,status:IDLE\n`

### Phone/laptop sends back (after classification):
```
result:<string>,bacteria:<string>,risk:<string>\n
```
Example: `result:CONTAMINATED,bacteria:E.coli,risk:HIGH\n`

### Status values:
- `IDLE` -- waiting, no classification running
- `SCANNING` -- classification in progress
- `SAFE` -- water passed classification
- `CONTAMINATED` -- bacteria detected
