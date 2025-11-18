#ifndef CONFIG_H
#define CONFIG_H

// WiFi Configuration
#define WIFI_SSID "YOUR_WIFI_SSID"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"

// MQTT Configuration
#define MQTT_BROKER "af31a5fa47f74486be18c7a448f04ae4.s1.eu.hivemq.cloud"
#define MQTT_PORT 8883
#define MQTT_USERNAME "Epicure_Task_Broker"
#define MQTT_PASSWORD "Epicure#2025"
#define MQTT_CLIENT_ID "esp32-subscriber"
#define MQTT_TOPIC "epicure/commands"

// UART Configuration for STM32
#define UART_RX_PIN 16  // ESP32 GPIO16 (RX2)
#define UART_TX_PIN 17  // ESP32 GPIO17 (TX2)
#define UART_BAUD 115200

// Connection Intervals
#define WIFI_CHECK_INTERVAL 10000   // 10 seconds
#define MQTT_CHECK_INTERVAL 5000    // 5 seconds
#define MQTT_RECONNECT_DELAY 5000   // 5 seconds

#endif
