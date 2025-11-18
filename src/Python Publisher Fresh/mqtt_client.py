"""
Simple MQTT Client for Epicure Publisher
Handles connection and message publishing with automatic reconnection
"""

import paho.mqtt.client as mqtt
import ssl
import logging
import time
import threading

import config

logger = logging.getLogger(__name__)


class SimpleMQTTClient:
    """Basic MQTT client with connection and publishing"""

    def __init__(self):
        """Initialize the MQTT client"""
        self.client = mqtt.Client(client_id=config.MQTT_CLIENT_ID)
        self.connected = False
        self.reconnecting = False
        self.reconnect_attempts = 0
        self.backoff_time = config.RETRY_DELAY
        self.should_reconnect = True
        self.lock = threading.RLock()

        # Set up callbacks
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish

        # Set username and password
        self.client.username_pw_set(config.BROKER_USERNAME, config.BROKER_PASSWORD)

        # Configure TLS
        if config.USE_TLS:
            self.client.tls_set(
                ca_certs=None,
                certfile=None,
                keyfile=None,
                cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLSv1_2,
                ciphers=None,
            )
            self.client.tls_insecure_set(False)

    def on_connect(self, client, userdata, flags, rc):
        """Called when client connects to broker"""
        if rc == 0:
            self.connected = True
            logger.info("Connected to MQTT broker")
        else:
            logger.error(f"Connection failed with code {rc}")

    def on_disconnect(self, client, userdata, rc):
        """Called when client disconnects from broker"""
        with self.lock:
            self.connected = False

        if rc != 0:
            logger.warning(f"Unexpected disconnection: {rc}")
            if self.should_reconnect and not self.reconnecting:
                logger.info("Triggering automatic reconnection...")
                self._start_reconnection()
        else:
            logger.info("Disconnected from MQTT broker")

    def on_publish(self, client, userdata, mid):
        """Called when message is published"""
        logger.debug(f"Message {mid} published successfully")

    def _start_reconnection(self):
        """Start reconnection thread"""
        with self.lock:
            if self.reconnecting:
                return
            self.reconnecting = True

        thread = threading.Thread(target=self._reconnect_loop, daemon=True)
        thread.start()

    def _reconnect_loop(self):
        """Reconnection loop with exponential backoff"""
        while self.should_reconnect and not self.connected:
            try:
                self.reconnect_attempts += 1
                logger.info(
                    f"Reconnection attempt {self.reconnect_attempts}/{config.MAX_RETRIES} "
                    f"(waiting {self.backoff_time}s)"
                )

                time.sleep(self.backoff_time)

                if not self.connected:
                    logger.info(
                        f"Attempting to reconnect to {config.BROKER_HOST}:{config.BROKER_PORT}"
                    )
                    try:
                        self.client.reconnect()
                    except Exception as e:
                        logger.warning(f"Reconnection attempt failed: {e}")

                        if self.reconnect_attempts >= config.MAX_RETRIES:
                            logger.error(
                                f"Max reconnection attempts ({config.MAX_RETRIES}) exceeded"
                            )
                            with self.lock:
                                self.reconnecting = False
                            return

                        self.backoff_time = min(
                            self.backoff_time * 2, config.MAX_RETRY_DELAY
                        )
                        continue

                with self.lock:
                    self.reconnecting = False
                break

            except Exception as e:
                logger.error(f"Error in reconnection loop: {e}")
                with self.lock:
                    self.reconnecting = False
                break

    def connect(self):
        """Connect to MQTT broker"""
        try:
            logger.info(
                f"Connecting to {config.BROKER_HOST}:{config.BROKER_PORT}"
            )
            self.reconnect_attempts = 0
            self.backoff_time = config.RETRY_DELAY
            self.client.connect(
                config.BROKER_HOST, config.BROKER_PORT, config.MQTT_KEEPALIVE
            )
            self.client.loop_start()
            logger.info("Connection initiated")
        except Exception as e:
            logger.error(f"Connection error: {e}")
            raise

    def publish_message(self, message):
        """Publish a message to the topic"""
        with self.lock:
            if not self.connected:
                logger.error("Not connected to broker")
                return False

        try:
            result = self.client.publish(config.MQTT_TOPIC, message, qos=1)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Published: {message}")
                return True
            else:
                logger.error(f"Publish failed: {result.rc}")
                return False
        except Exception as e:
            logger.error(f"Error publishing message: {e}")
            return False

    def disconnect(self):
        """Disconnect from broker"""
        with self.lock:
            self.should_reconnect = False
            was_connected = self.connected

        try:
            if was_connected:
                self.client.disconnect()
        except Exception as e:
            logger.warning(f"Error during disconnect: {e}")

        # Always stop the network loop, even if connection failed
        self.client.loop_stop()

        with self.lock:
            self.connected = False
            self.reconnecting = False

        logger.info("Disconnected from broker")
