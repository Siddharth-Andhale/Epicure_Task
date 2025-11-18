"""
Configuration file for Epicure MQTT Publisher
Simple and straightforward settings
"""

# MQTT Broker Settings
BROKER_HOST = "af31a5fa47f74486be18c7a448f04ae4.s1.eu.hivemq.cloud"
BROKER_PORT = 8883
BROKER_USERNAME = "Epicure_Task_Broker"
BROKER_PASSWORD = "Epicure#2025"

# MQTT Settings
MQTT_TOPIC = "epicure/commands"
MQTT_CLIENT_ID = "epicure-publisher-fresh"
MQTT_KEEPALIVE = 60

# TLS Settings
USE_TLS = True
TLS_VERSION = "tlsv1_2"

# Retry Settings
MAX_RETRIES = 10
RETRY_DELAY = 2
MAX_RETRY_DELAY = 60

# Log Settings
LOG_LEVEL = "INFO"
