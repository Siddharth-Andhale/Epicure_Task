# Epicure Robotics - Complete System Integration

## System Architecture

```
┌─────────────────┐
│   Python        │
│   Publisher     │
│   (Computer)    │
└────────┬────────┘
         │ MQTT
         │ (over Internet)
         ▼
┌─────────────────────────────────────┐
│     HiveMQ Cloud Broker             │
│ af31a5fa47f74486be18c7a448f04ae4   │
│ epicure/commands topic              │
└─────────────────────────────────────┘
         ▲
         │ MQTT Subscribe
         │
         ▼
┌─────────────────┐
│   ESP32         │
│   (WiFi)        │
│   MQTT Client   │
└────────┬────────┘
         │ UART2
         │ (115200 baud)
         ▼
┌─────────────────┐
│   STM32         │
│   (Wired)       │
│   UART Rx       │
└────────┬────────┘
         │
    ┌────┴─────┬──────────┐
    │           │          │
    ▼           ▼          ▼
┌────────┐  ┌─────┐   ┌────────┐
│ Motor  │  │ LED │   │ Debug  │
│(GPIO)  │  │(GPIO) │ │UART TX │
└────────┘  └─────┘   └────────┘
```

## Component Overview

### 1. Python Publisher (`Python Publisher Fresh/`)
- **Language**: Python 3
- **MQTT Broker**: HiveMQ Cloud (TLS/SSL)
- **Credentials**: Epicure_Task_Broker / Epicure#2025
- **Topic**: epicure/commands
- **Features**:
  - CLI for user input
  - MQTT publish with auto-reconnection
  - Command validation
  - Exponential backoff retry logic
  - Comprehensive error handling

### 2. ESP32 Firmware (`ESP32 Firmware/ESP32_MQTT_Subscriber/`)
- **MCU**: ESP32 (ESP-WROOM-32D)
- **Framework**: Arduino/ESP-IDF
- **WiFi**: Configurable SSID/Password
- **MQTT**: Secure TLS connection
- **UART**: GPIO16 (RX2) / GPIO17 (TX2) at 115200 baud
- **Features**:
  - WiFi auto-reconnection
  - MQTT subscription with auto-reconnection
  - Message forwarding to STM32 via UART
  - Debug output on Serial

### 3. STM32 Firmware (`STM32 Firmware/STM32_UART_Controller/`)
- **MCU**: STM32F407VET6
- **UART2**: PA2 (TX) / PA3 (RX) at 115200 baud
- **Motor Control**: PC13 (Step) / PC14 (Direction)
- **LED Control**: PD12 (On/Off)
- **Features**:
  - UART interrupt-driven command reception
  - Motor step pulse generation
  - LED on/off control
  - Command validation and error handling
  - Debug output on UART

## Command Flow

### Motor Command
```
User: motor:100:1
  ↓
Python: Parse and validate (100 steps, direction 1)
  ↓
Python: Publish to MQTT topic "epicure/commands"
  ↓
HiveMQ: Route message to subscribers
  ↓
ESP32: Receive MQTT message
  ↓
ESP32: Validate and format message
  ↓
ESP32: Forward via UART2 to STM32: "motor:100:1\n"
  ↓
STM32: Receive via UART interrupt
  ↓
STM32: Parse command (100 steps, forward)
  ↓
STM32: Set PC14 (DIR) = HIGH (forward)
  ↓
STM32: Generate 100 step pulses on PC13
  ↓
Motor: Move 100 steps forward
```

### LED Command
```
User: led:on
  ↓
Python: Parse and validate (state = "on")
  ↓
Python: Publish to MQTT "led:on"
  ↓
ESP32: Receive and forward "led:on\n"
  ↓
STM32: Parse command
  ↓
STM32: Set PD12 = HIGH
  ↓
LED: Turns on
```

## Setup Instructions

### Prerequisites
- Python 3.7+ with pip
- PlatformIO IDE or Arduino IDE
- STM32CubeIDE
- USB cables for all devices
- HiveMQ Cloud account (created)

### Step 1: Set Up Python Publisher

```bash
cd "Python Publisher Fresh"
pip install -r requirements.txt
python main.py
```

**Output:**
```
============================================================
Epicure MQTT Publisher
============================================================
Connecting to MQTT broker...
Connected to MQTT broker
```

### Step 2: Configure and Flash ESP32

1. Open `ESP32 Firmware/ESP32_MQTT_Subscriber/src/main.cpp`
2. Update WiFi credentials (lines 19-20):
   ```cpp
   const char* WIFI_SSID = "YOUR_SSID";
   const char* WIFI_PASSWORD = "YOUR_PASSWORD";
   ```
3. Build: `platformio run -e esp32dev`
4. Upload: `platformio run -e esp32dev -t upload`
5. Monitor: `platformio device monitor -b 115200`

**Expected Output:**
```
[0s] DEBUG: ESP32 Starting up...
[1s] DEBUG: WiFi connection successful
[2s] DEBUG: Connected to MQTT broker
[3s] DEBUG: MQTT subscribed to epicure/commands
```

### Step 3: Configure and Flash STM32

1. Open STM32CubeIDE
2. Import project: `STM32 Firmware/STM32_UART_Controller`
3. Generate code from `.ioc` file
4. Build project
5. Flash to STM32F407VET6
6. Open serial monitor at 115200 baud

**Expected Output:**
```
[DEBUG] STM32 Startup Complete
[DEBUG] Waiting for commands from ESP32...
```

### Step 4: Test Integration

1. Ensure all three components are running
2. In Python Publisher console, enter: `motor:50:1`
3. Expected sequence:
   - Python publishes to MQTT
   - ESP32 receives and forwards via UART
   - STM32 receives and moves motor 50 steps forward
   - Motor executes command

### Test Commands

```
motor:100:1     → Motor moves 100 steps forward (direction 1)
motor:50:0      → Motor moves 50 steps backward (direction 0)
motor:10000:1   → Motor moves maximum steps (10000) forward
motor:0:1       → Motor doesn't move (0 steps is valid)
led:on          → LED turns on
led:off         → LED turns off
exit            → Stop Python publisher gracefully
```

## Electrical Connections

### ESP32 to STM32 (UART)
```
ESP32 GPIO17 (TX2) → STM32 PA3 (RX)
ESP32 GPIO16 (RX2) → STM32 PA2 (TX)
ESP32 GND --------→ STM32 GND
```

### STM32 to Motor Driver
```
STM32 PC13 (STEP) → Motor Driver STEP Input
STM32 PC14 (DIR)  → Motor Driver DIR Input
STM32 GND --------→ Motor Driver GND
```

### STM32 to LED
```
STM32 PD12 ── 1kΩ Resistor ── LED Cathode (-)
LED Anode (+) ─────────────── +5V (with current limiting resistor)
```

### WiFi Network
- ESP32 connects to your local WiFi network
- Internet access required for HiveMQ Cloud connection
- Consider using 2.4GHz band if ESP32 has issues with 5GHz

## Troubleshooting Guide

### Python Publisher Issues

**Cannot connect to MQTT broker:**
- Verify HiveMQ credentials in `config.py`
- Check internet connection
- Verify firewall allows port 8883
- Check HiveMQ console for account status

**Commands not sent:**
- Verify MQTT broker connection shows "Connected"
- Check command format: `motor:steps:direction` or `led:on/off`
- Monitor HiveMQ for message publishing

### ESP32 Issues

**WiFi connection fails:**
- Verify SSID and password are correct
- Check WiFi signal strength
- Ensure 2.4GHz band (if applicable)
- Check if network has MAC filtering

**MQTT connection fails:**
- Verify internet connection
- Check credentials match HiveMQ settings
- Verify firewall port 8883 is accessible
- Check ESP32 system time is correct (NTP)

**UART transmission fails:**
- Verify ESP32 GPIO16/17 are not used elsewhere
- Check connections to STM32
- Verify baud rate is 115200
- Use logic analyzer to verify signal

### STM32 Issues

**UART not receiving:**
- Check PA2/PA3 connections from ESP32
- Verify UART2 is configured at 115200 baud
- Check for loose connections
- Use oscilloscope to verify signal presence

**Motor not moving:**
- Verify PC13/PC14 pins output HIGH/LOW signals
- Check motor driver power supply
- Test motor driver with external pulse generator
- Verify motor is powered

**LED not turning on:**
- Check PD12 pin voltage with multimeter
- Verify LED polarity
- Check current-limiting resistor value
- Test LED separately with power supply

**Command parsing errors:**
- Check UART data on scope/analyzer
- Verify newline character is sent (`\n`)
- Check command format exactly matches specification
- Monitor debug output for parsing details

## Support & Documentation

### Files Included
- `Python Publisher Fresh/main.py` - Python application
- `ESP32 Firmware/...` - ESP32 firmware
- `STM32 Firmware/...` - STM32 firmware
- `README.md` - This file

### Additional Resources
- MQTT Protocol: https://mqtt.org/
- HiveMQ Documentation: https://www.hivemq.com/documentation/
- ESP32 Arduino: https://github.com/espressif/arduino-esp32
- STM32CubeF4: https://www.st.com/en/embedded-software/stm32cubef4.html

