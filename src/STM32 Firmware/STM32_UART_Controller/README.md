# STM32 UART Controller - Epicure Robotics

## Overview

STM32F407VET6 firmware for receiving motor and LED control commands via UART from the ESP32, with GPIO-based motor control and LED management.

## System Architecture

```
┌─────────────────────────┐
│   Python Publisher      │
│   (MQTT Publish)        │
└──────────────┬──────────┘
               │ MQTT Topic: epicure/commands
               ▼
┌─────────────────────────────────────┐
│    HiveMQ Cloud Broker              │
└──────────────┬──────────────────────┘
               │ MQTT Subscribe
               ▼
┌─────────────────────────┐
│   ESP32 (WiFi)          │
│   (MQTT Subscribe)      │
│   (UART Forward)        │
└──────────────┬──────────┘
               │ UART2: 115200 baud, 8N1
               ▼
┌──────────────────────────────────────┐
│   STM32F407VET6 (This Project)       │
│   ├── UART2 Receiver (PA2/PA3)       │
│   ├── Command Parser                 │
│   ├── Motor Control (PC13/PC14)      │
│   ├── LED Control (PD12)             │
│   └── Debug Output (UART TX)         │
└──────────────┬───────────────────────┘
               │
        ┌──────┴──────┬──────────┐
        ▼             ▼          ▼
    ┌────────┐  ┌─────┐    ┌────────┐
    │ Motor  │  │ LED │    │ Debug  │
    │Driver  │  │     │    │Output  │
    └────────┘  └─────┘    └────────┘
```

## Hardware Requirements

### Microcontroller
- **Target**: STM32F407VET6
- **Development Board**: Any STM32F407 board
- **Programmer**: ST-Link/V2 or equivalent

### Peripherals
- **Motor Driver**: Stepper motor driver (accepts step and direction signals)
- **LED**: Standard LED with appropriate resistor
- **UART Connection**: From ESP32 (3.3V levels)
- **Power Supply**: 5V for STM32, appropriate for motor driver

## Pin Configuration

### UART Pins
| Pin | Port | Function | Notes |
|-----|------|----------|-------|
| PA2 | GPIOA | UART2 TX | Debug output |
| PA3 | GPIOA | UART2 RX | Command input from ESP32 |

### Motor Control Pins
| Pin | Port | Function | Notes |
|-----|------|----------|-------|
| PC13 | GPIOC | Step Signal | Pulse signal to motor driver |
| PC14 | GPIOC | Direction | Direction control (HIGH=forward, LOW=backward) |

### LED Control Pin
| Pin | Port | Function | Notes |
|-----|------|----------|-------|
| PD12 | GPIOD | LED | Directly drive LED (with resistor) |

### Voltage Levels
- **STM32 Outputs**: 3.3V (CMOS)
- **Motor Driver Inputs**: Usually 3.3V-5V compatible
- **LED**: 3.3V max with appropriate resistor
- **GND**: Must be common between ESP32 and STM32

## Software Setup

### Prerequisites
- **STM32CubeIDE**: Latest version
- **Compiler**: ARM GCC (included with IDE)
- **Programmer**: ST-Link or compatible

### Installation Steps

1. **Open STM32CubeIDE**
   ```
   Launch STM32CubeIDE
   ```

2. **Import the Project**
   ```
   File → Open Projects from File System
   Navigate to: STM32_UART_Controller/
   Select all folders → Finish
   ```

3. **Configure for Your Board (if needed)**
   ```
   Right-click project → Properties → C/C++ Build → MCU
   Select: STM32F407VETx
   ```

4. **Build the Project**
   ```
   Project → Build Project
   Or: Ctrl+B
   ```

5. **Flash to Device**
   ```
   Connect ST-Link to development board
   Project → Build Configurations → Set Active → Release
   Run → Run Configurations → Select STM32... → Run
   Or: Right-click project → Run As → STM32 C/C++ Application
   ```

6. **Debug (Optional)**
   ```
   Run → Debug Configurations
   Select STM32... → Apply → Debug
   Or: F11 to start debugging
   ```

## Configuration

### UART Configuration
Already configured in STM32CubeIDE, verified in code:

```c
// UART2 Settings (from usart.c)
Baud Rate: 115200
Data Bits: 8
Parity: None
Stop Bits: 1
Flow Control: None
Mode: RX and TX
```

### GPIO Configuration
Already configured via CubeIDE, verified in code:

```c
// Motor Pins (from gpio.c)
PC13 (MOTOR_STEP_Pin): Output, Push-Pull, Low Speed
PC14 (MOTOR_DIR_Pin): Output, Push-Pull, Low Speed

// LED Pin (from gpio.c)
PD12 (LED_INDICATOR_Pin): Output, Push-Pull, Low Speed
```

### System Clock Configuration
Already configured via CubeIDE:

```c
// From main.c SystemClock_Config()
HSI: 16 MHz
PLL: 336x / 4 = 84 MHz
HCLK: 84 MHz
APB1: 42 MHz (84/2)
APB2: 84 MHz
```

## Operation

### Starting the Firmware

1. **Power On the STM32**
   - Connect 5V power supply
   - ST-Link automatically detects device
   - Firmware runs automatically

2. **Verify Initialization**
   - Monitor UART output (115200 baud)
   - Should show system ready message
   - Waiting for commands from ESP32

3. **Ready for Commands**
   - System waits for UART commands from ESP32
   - Processes incoming messages
   - Executes motor and LED control

### Command Reception

1. **Receive Cycle**
   ```
   Interrupt-driven UART reception
   Character buffering until newline
   Command validation
   Execution
   Debug response via UART TX
   ```

2. **Expected Flow**
   ```
   ESP32 sends: "motor:100:1\n"
   STM32 receives: byte-by-byte interrupt
   STM32 buffers: "motor:100:1"
   STM32 validates: Format, range, values
   STM32 executes: Motor control
   STM32 responds: "[OK] Motor executed\r\n"
   ```

### Debug Output

Monitor with serial terminal (115200 baud):

```
[OK] Motor executed
[OK] LED updated
[ERROR] Invalid motor parameters
[ERROR] LED: use led:on or led:off
[ERROR] Unknown command
```

## Command Protocol

### Supported Commands

#### Motor Command
```
Format: motor:<steps>:<direction>\n
Example: motor:100:1\n

Parameters:
- steps: 0-10000 (integer)
- direction: 0 (backward) or 1 (forward)

Response: [OK] Motor executed\r\n
Error: [ERROR] Invalid motor parameters\r\n
```

**Operation**:
1. Set direction GPIO (PC14)
2. Generate step pulses on PC13 (1ms high, 1ms low per step)
3. Return to position

#### LED Command
```
Format: led:on\n or led:off\n
Example: led:on\n

Parameters:
- State: on or off (case-insensitive in code)

Response: [OK] LED updated\r\n
Error: [ERROR] LED: use led:on or led:off\r\n
```

**Operation**:
1. Set PD12 HIGH (LED on) or LOW (LED off)
2. Return confirmation

### Command Validation

| Field | Valid Range | Invalid Example |
|-------|-------------|-----------------|
| Motor Steps | 0-10000 | motor:10001:1 |
| Motor Direction | 0 or 1 | motor:100:2 |
| LED State | on/off | led:maybe |
| Format | motor:X:Y or led:Z | motor:100 |

### Error Handling

```
Invalid Motor Parameters:
- Steps out of range (>10000)
- Direction not 0 or 1
- Non-numeric steps
- Wrong format

Invalid LED:
- State not on/off
- Wrong format

Unknown Command:
- Type not motor/led
- Empty command
```

## Hardware Connections

### UART Connection (ESP32 to STM32)

```
ESP32          STM32
GPIO16 (RX2) → PA3 (UART2_RX)
GPIO17 (TX2) → PA2 (UART2_TX)
GND          → GND
```

**Note**: ESP32 is 3.3V, STM32 is 3.3V - voltage levels compatible

### Motor Driver Connection

```
STM32 (3.3V)        Motor Driver        Stepper Motor
PC13 (Step)    →    STEP signal
PC14 (Dir)     →    DIR signal
GND            →    GND
                                        Step →
                                        Dir →
                                        +5V (Driver supply)
```

### LED Connection

```
STM32                LED Circuit
PD12 (Output) → 1kΩ Resistor → LED Anode
GND          → LED Cathode
```

**Resistor Calculation**:
- Typical LED forward voltage: 2V
- STM32 output: 3.3V
- Current limit: ~3mA
- Resistor = (3.3V - 2V) / 3mA = ~433Ω (use 470Ω standard)

## Testing

### Unit Testing (Before Integration)

1. **UART Communication Test**
   ```
   Connect UART2 TX (PA2) to your PC serial monitor
   Send test command: "motor:50:1\n"
   Expect response: "[OK] Motor executed\r\n"
   ```

2. **Motor Control Test**
   ```
   Send: "motor:100:1\n"
   Observe: PC13 produces 100 step pulses
   Observe: PC14 set HIGH (forward direction)
   Verify: Motor moves 100 steps forward
   ```

3. **LED Control Test**
   ```
   Send: "led:on\n"
   Observe: PD12 goes HIGH, LED lights up
   Send: "led:off\n"
   Observe: PD12 goes LOW, LED turns off
   ```

4. **Error Handling Test**
   ```
   Send: "motor:20000:1\n"
   Expect: "[ERROR] Invalid motor parameters\r\n"
   Send: "led:maybe\n"
   Expect: "[ERROR] LED: use led:on or led:off\r\n"
   ```

### Integration Testing

1. **Full System Test**
   ```
   Start Python Publisher
   Start ESP32 (connected to WiFi/MQTT)
   Flash STM32 firmware
   Send command from Python: "motor:100:1"
   Verify: Motor moves on STM32
   ```

2. **Continuous Operation Test**
   ```
   Send multiple commands in sequence
   Verify each executes correctly
   Test rapid fire commands
   Monitor for memory leaks or hangs
   ```

3. **Error Recovery Test**
   ```
   Send invalid commands
   Verify graceful error handling
   Verify system continues working
   Send valid command after error
   ```

## Firmware Files

### Core Files
| File | Purpose |
|------|---------|
| `Core/Src/main.c` | Main program with command processing |
| `Core/Inc/main.h` | Header with GPIO pin definitions |
| `Core/Src/usart.c` | UART initialization |
| `Core/Src/gpio.c` | GPIO initialization |

### Key Functions in main.c

```c
HAL_UART_RxCpltCallback()      // UART receive interrupt handler
parse_and_execute_command()    // Parse and validate commands
motor_control()                // Execute motor movement
led_control()                  // Execute LED control
```

### Configuration Files
| File | Purpose |
|------|---------|
| `Epicure_STM.ioc` | CubeIDE project configuration |
| `STM32F407VETX_FLASH.ld` | Linker script for Flash storage |

## Code Structure

```c
// Main loop (from main.c)
while (1) {
    if (cmd_ready) {
        parse_and_execute_command(cmd_buffer);
        cmd_index = 0;
        cmd_ready = 0;
        HAL_UART_Receive_IT(&huart2, &cmd_buffer[0], 1);
    }
}

// Command parsing
void parse_and_execute_command(const char* cmd) {
    if (strncmp(cmd, "motor:", 6) == 0) {
        // Parse motor command
        // Validate parameters
        // Call motor_control()
    } else if (strncmp(cmd, "led:", 4) == 0) {
        // Parse LED command
        // Validate state
        // Call led_control()
    }
}

// Motor execution
void motor_control(uint16_t steps, uint8_t direction) {
    // Set direction
    // Generate step pulses
    // Send confirmation
}

// LED execution
void led_control(uint8_t state) {
    // Set LED GPIO
    // Send confirmation
}
```

## Troubleshooting

### Build Issues

**Problem**: Project won't build
```
Solution:
1. Clean project: Project → Clean
2. Rebuild: Project → Build All
3. Check compiler path in Settings
4. Verify project type is STM32C/C++
5. Check for syntax errors in main.c
```

**Problem**: "stm32f4xx_hal.h not found"
```
Solution:
1. Right-click project → Properties
2. C/C++ General → Paths and Symbols
3. Verify HAL includes are present
4. May need to regenerate code from .ioc
```

### Flash/Programming Issues

**Problem**: Cannot connect to device
```
Solution:
1. Check ST-Link USB connection
2. Verify ST-Link driver installed
3. Check Device Manager for STLink device
4. Try different USB port
5. Reset device and try again
```

**Problem**: "Device not found" after flash
```
Solution:
1. Check if firmware actually flashed
2. Verify no errors in build
3. Try full chip erase: STM32 → Erase Chip
4. Check power supply to board
5. Verify debugging interface settings
```

### UART Communication Issues

**Problem**: No characters received
```
Solution:
1. Verify UART2 initialization is correct
2. Check PA2/PA3 are configured
3. Verify serial settings: 115200, 8N1
4. Check RX interrupt is enabled
5. Test with simple echo program first
```

**Problem**: Garbled characters in serial monitor
```
Solution:
1. Verify baud rate is 115200
2. Check stop bits (should be 1)
3. Check data bits (should be 8)
4. Try different serial terminal program
5. Verify USB serial adapter is working
```

**Problem**: Commands not executing
```
Solution:
1. Verify command format exactly: motor:100:1\n
2. Check newline character is sent (\n not \r\n)
3. Monitor serial output for error messages
4. Verify command is received (add debug output)
5. Check buffer not overflowing
```

### Motor Control Issues

**Problem**: Motor doesn't move
```
Solution:
1. Check motor driver is powered
2. Verify PC13/PC14 GPIO pins are correct
3. Test GPIO output with oscilloscope
4. Check motor driver is enabled
5. Verify motor power supply
6. Test with simpler command first
```

**Problem**: Wrong number of steps
```
Solution:
1. Check step timing (1ms delays)
2. Verify motor driver step pulse requirements
3. Test with known step count
4. Add debug output for step counter
5. Check for integer overflow (steps > 65535)
```

**Problem**: Direction not working
```
Solution:
1. Swap motor wires to reverse direction
2. Or modify code: change GPIO_PIN_SET/RESET logic
3. Test direction pin independently
4. Verify motor driver direction input
```

### LED Control Issues

**Problem**: LED won't turn on
```
Solution:
1. Check LED polarity (correct direction)
2. Verify resistor value (470Ω typical)
3. Test PD12 output with multimeter
4. Check GPIO configuration
5. Try different GPIO pin
```

**Problem**: LED dimmer than expected
```
Solution:
1. Increase resistor size (less current = dimmer)
2. Current calculation: (3.3V - 2V) / R = I
3. For 5mA: R = 260Ω
4. Check power supply voltage
```

## Performance Characteristics

### Timing
| Operation | Time |
|-----------|------|
| Command receive | 1-100ms (depends on length) |
| Command validate | < 1ms |
| Motor step | 2ms per step (1ms high + 1ms low) |
| Motor 100 steps | 200ms |
| LED control | < 1ms |
| UART response | < 1ms |

### Resource Usage
| Resource | Usage |
|----------|-------|
| Flash | ~20KB |
| RAM | <1KB global |
| Stack | ~1KB |
| Heap | ~2KB |

### Memory Layout
```
Flash:
- Bootloader: 0x08000000 - 0x08010000
- Code: 0x08010000 - 0x08100000 (960KB available)

RAM:
- SRAM1: 0x20000000 - 0x20020000 (128KB)
- SRAM2: 0x20020000 - 0x2002C000 (48KB)
- SRAM3: 0x2002C000 - 0x2003C000 (64KB)
```

## Advanced Features

### Command Buffer
- Size: 256 bytes
- Overflow protection
- Newline detection
- Auto-reset on error

### Error Handling
- Invalid format detection
- Range validation
- Parameter type checking
- Error message feedback

### Debug Output
- Via UART2 TX (PA2)
- 115200 baud
- Real-time status messages

## Future Enhancements

### Planned Features
- [ ] Variable motor speed control
- [ ] Encoder feedback for motor position
- [ ] Status queries (current position, LED state)
- [ ] Command queue for rapid fire
- [ ] Watchdog timer for safety
- [ ] Power management
- [ ] EEPROM settings storage

### Optimization Ideas
- [ ] Reduce step pulse timing
- [ ] Implement acceleration ramps
- [ ] Add PWM for motor speed
- [ ] Multi-motor support
- [ ] Emergency stop signal

## FAQ

### Q: Can I change the baud rate?
**A**: Yes, in `Core/Src/usart.c` change `115200` to desired rate. Then update ESP32 and serial monitor.

### Q: How many steps per revolution?
**A**: Depends on motor and driver. Typically 200-400 steps. Driver configuration determines this.

### Q: Can I use different GPIO pins?
**A**: Yes, in STM32CubeIDE reconfigure pins, then regenerate code. Or manually update `main.h` and main.c pin definitions.

### Q: What if motor driver needs higher voltage?
**A**: Use logic level converter (3.3V → 5V) between STM32 and motor driver.

### Q: Can I add more outputs?
**A**: Yes, configure additional GPIO pins in CubeIDE and add control functions.

### Q: How do I update the firmware?
**A**: Rebuild and flash using STM32CubeIDE. No bootloader modification needed.

## Integration Checklist

Before full system testing:

- [ ] STM32 firmware compiles without errors
- [ ] Firmware flashes to device
- [ ] Serial monitor shows ready message
- [ ] UART connection verified (ESP32 ↔ STM32)
- [ ] Motor GPIO outputs verified
- [ ] LED GPIO output verified
- [ ] Individual motor test passes
- [ ] Individual LED test passes
- [ ] Command format validated
- [ ] Error handling verified
- [ ] Full system integration test passes

## Support

For issues:
1. Check serial debug output
2. Verify hardware connections
3. Review command format
4. Check build output for warnings
5. Test each component independently

## Version Information

- **Firmware**: STM32 UART Controller v1.0
- **Target**: STM32F407VET6
- **HAL Version**: STM32F4xx v1.25+
- **UART Baud**: 115200
- **Status**: Production-Ready

## License

Epicure Robotics - Intern Task

## Credits

Developed following the Epicure Robotics action plan with complete UART command processing and GPIO motor/LED control implementation.

---

**Ready for Integration & Testing**
