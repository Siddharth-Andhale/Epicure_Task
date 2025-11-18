# ESP32 MQTT Subscriber - Epicure Robotics

## Overview
This ESP32 firmware subscribes to MQTT messages from the Python publisher and forwards them to the STM32 microcontroller via UART.

## System Architecture
```
Python Publisher (MQTT) 
    → HiveMQ Cloud Broker 
        → ESP32 (MQTT Subscriber) 
            → UART (115200 baud, 8N1) 
                → STM32 (UART Receiver)
                    → Motor & LED Control
```

## Hardware Requirements
- **ESP32 Development Board** (ESP-WROOM-32 or similar)
- **USB-to-Serial Adapter** for programming
- **Jumper Wires** for UART connection to STM32

## Pin Configuration
```
ESP32 UART2 (RX2/TX2):
- GPIO16 (RX2) → STM32 TX
- GPIO17 (TX2) → STM32 RX
- GND → STM32 GND
```

## Software Setup

### Prerequisites
- PlatformIO IDE or VS Code with PlatformIO extension
- PubSubClient library (automatically installed)

### Installation Steps

1. **Clone/Copy the project**
   ```bash
   cd ESP32_MQTT_Subscriber
   ```

2. **Configure WiFi and MQTT credentials**
   Edit `include/config.h`:
   ```cpp
   #define WIFI_SSID "YOUR_WIFI_SSID"
   #define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"
   ```

3. **Build the project**
   ```bash
   platformio run -e esp32dev
   ```

4. **Upload to ESP32**
   ```bash
   platformio run -e esp32dev -t upload
   ```

5. **Monitor Serial Output**
   ```bash
   platformio device monitor -b 115200
   ```

## Configuration

### MQTT Settings
- **Broker**: `af31a5fa47f74486be18c7a448f04ae4.s1.eu.hivemq.cloud`
- **Port**: `8883` (TLS)
- **Username**: `Epicure_Task_Broker`
- **Password**: `Epicure#2025`
- **Topic**: `epicure/commands`
- **Client ID**: `esp32-subscriber`

### UART Settings
- **Baud Rate**: 115200
- **Data Bits**: 8
- **Parity**: None
- **Stop Bits**: 1
- **Line Ending**: Newline (`\n`)

## Operation

### Starting the ESP32
1. Connect ESP32 to power
2. Device automatically connects to WiFi
3. Device automatically subscribes to MQTT topic
4. Ready to receive commands

### Message Flow
1. Python Publisher sends command: `motor:100:1` to MQTT
2. ESP32 receives message via MQTT
3. ESP32 forwards to STM32 via UART: `motor:100:1\n`
4. STM32 parses and executes command

### Debug Output
Serial monitor shows:
```
[5s] DEBUG: WiFi connection successful
[6s] DEBUG: Connected to MQTT broker
[10s] DEBUG: Message forwarded to STM32
```

## Troubleshooting

### WiFi Connection Issues
- Verify SSID and password in `config.h`
- Check WiFi signal strength
- Monitor shows "WiFi connection failed"

### MQTT Connection Issues
- Verify broker credentials
- Check internet connection
- Verify firewall settings for port 8883
- Check HiveMQ console for connection logs

### UART Communication Issues
- Verify GPIO pins are correct (16, 17)
- Check baud rate matches STM32 (115200)
- Verify GND connection between ESP32 and STM32
- Check for proper voltage levels (3.3V)

### Message Not Received
- Check Python Publisher is publishing to correct topic
- Verify ESP32 is subscribed to `epicure/commands`
- Monitor serial output for "Message received" logs
- Check STM32 UART receiver is active

## Command Format

### Valid Commands
- `motor:100:1` - Move motor 100 steps forward (direction 1)
- `motor:50:0` - Move motor 50 steps backward (direction 0)
- `led:on` - Turn LED on
- `led:off` - Turn LED off

### Command Validation
- Motor steps: 0-10000
- Direction: 0 (backward) or 1 (forward)
- LED state: on or off

## Performance
- **Connection Time**: ~2-5 seconds
- **Message Latency**: <100ms (WiFi + MQTT)
- **UART Transmission**: Immediate
- **Memory Usage**: ~160KB Flash, ~45KB RAM

## Power Consumption
- **Active**: ~80-100mA
- **WiFi Active**: ~120-150mA
- **Sleep (not implemented): ~10mA

## Safety Features
- Automatic WiFi reconnection every 10 seconds
- Automatic MQTT reconnection every 5 seconds
- Command validation before UART transmission
- Debug output for troubleshooting
- Buffer overflow protection (256 bytes)

## Known Limitations
- Single MQTT message size: 256 bytes
- No command queue (processes one at a time)
- WiFi credentials stored in code (use environment variables for production)

## Future Improvements
- Add Over-The-Air (OTA) firmware updates
- Implement command queue for high-frequency commands
- Add EEPROM for credential storage
- Add LED indicator for connection status
- Implement watchdog timer for reliability

## Support
For issues or questions, check:
1. Serial monitor debug output
2. MQTT broker logs
3. STM32 UART receiver logs
4. Verify all connections and credentials

## License
Epicure Robotics - Intern Task
