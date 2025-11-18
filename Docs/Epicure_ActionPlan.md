# Epicure Robotics Task — Action Plan

## PHASE 1 — Understand Requirements (0.5 hour)
- Read the task PDF thoroughly.
- Identify 3 core components to build:
  1. Python MQTT Publisher  
  2. ESP32 MQTT Subscriber + UART Forwarder  
  3. STM32 UART Receiver + Motor & LED Controller

## PHASE 2 — Define Message Protocol (0.5 hour)
- Use a consistent command structure:
  ```
  motor:<steps>:<direction>
  led:<on/off>
  ```

## PHASE 3 — Python Program Development (2–3 hours)
- Implement MQTT publisher using `paho-mqtt`.
- Take continuous user input (CLI loop).
- Publish to topic `epicure/commands`.
- Add:
  - Auto reconnect  
  - Error handling  
  - Clean shutdown  
- Test using Mosquitto MQTT broker.

## PHASE 4 — ESP32 Firmware (3 hours)
- Use Arduino or ESP-IDF.
- Connect to WiFi → MQTT broker.
- Subscribe to `epicure/commands`.
- Forward received messages via UART to STM32.
- UART settings: `115200 baud`, `8N1`, newline-terminated.
- Add debug prints and reconnection logic.

## PHASE 5 — STM32 Firmware (4–5 hours)
- Use STM32CubeIDE.
- Initialize UART receive handler.
- Parse commands:
  - `motor:<steps>:<dir>` → drive stepper motor  
  - `led:on/off` → control LED  
- Implement stepper control via GPIO or timer pulses.
- Add error handling for invalid commands.

## PHASE 6 — Integration Testing (2 hours)
- Test each link:
  1. Python → MQTT  
  2. ESP32 → MQTT  
  3. ESP32 → UART  
  4. STM32 → Motor/LED  
- Then test full workflow:
  ```
  Python → MQTT → ESP32 → UART → STM32 → Motor/LED
  ```

## PHASE 7 — Documentation (1 hour)
- Write README with:
  - Setup steps  
  - Dependencies  
  - How to run each component  
  - Command format  
  - Example commands  

## PHASE 8 — Final Submission Package
Deliver:
- Python script  
- ESP32 code  
- STM32 code  
- README.md  

Optional:
- Architecture diagram  
- Flow diagram  
- Command table  

## TOTAL ESTIMATED TIME: ~12 hours
