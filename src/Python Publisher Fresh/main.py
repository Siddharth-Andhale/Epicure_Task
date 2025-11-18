"""
Main application for Epicure MQTT Publisher
Simple CLI loop for sending commands
"""

import logging
import sys
import time

import config
from mqtt_client import SimpleMQTTClient
from command_validator import CommandValidator

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


class EpicurePublisher:
    """Main application class"""

    def __init__(self):
        """Initialize the publisher"""
        self.mqtt_client = SimpleMQTTClient()
        self.validator = CommandValidator()
        self.running = True

    def print_welcome(self):
        """Print welcome message"""
        print("\n" + "=" * 60)
        print("Epicure MQTT Publisher")
        print("=" * 60)
        print("\nCommand Examples:")
        print("  motor:100:1  - Move motor 100 steps forward")
        print("  motor:50:0   - Move motor 50 steps backward")
        print("  led:on       - Turn LED on")
        print("  led:off      - Turn LED off")
        print("\nType 'exit' or 'quit' to stop")
        print("=" * 60 + "\n")

    def get_user_command(self):
        """Get command from user"""
        try:
            command = input("> ").strip()
            return command
        except EOFError:
            return "exit"
        except KeyboardInterrupt:
            print("\nInterrupted by user")
            return "exit"

    def handle_command(self, user_input):
        """Handle user command"""
        if user_input.lower() in ["exit", "quit"]:
            self.running = False
            return

        # Validate command
        command = self.validator.parse_user_input(user_input)

        if command is None:
            print("[ERROR] Invalid command format")
            return

        # Check connection
        if not self.mqtt_client.connected:
            print("[ERROR] Not connected to MQTT broker yet. Please wait...")
            return

        # Publish command
        success = self.mqtt_client.publish_message(command)

        if success:
            if "motor" in command:
                print("[OK] Motor command sent")
            elif "led" in command:
                print("[OK] LED command sent")
        else:
            print("[ERROR] Failed to send command")

    def run(self):
        """Main application loop"""
        try:
            # Connect to MQTT broker
            logger.info("Starting publisher...")
            self.mqtt_client.connect()

            # Wait for connection
            print("Connecting to MQTT broker...")
            timeout = 10
            start_time = time.time()
            while not self.mqtt_client.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)

            if not self.mqtt_client.connected:
                print("[WARNING] Connection timeout, but you can still try sending commands")

            # Show welcome message
            self.print_welcome()

            # Main loop
            while self.running:
                try:
                    user_input = self.get_user_command()

                    if user_input:
                        self.handle_command(user_input)

                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    print(f"[ERROR] {e}")

        except Exception as e:
            logger.error(f"Fatal error: {e}")
            print(f"[ERROR] Fatal error: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        logger.info("Shutting down...")
        self.mqtt_client.disconnect()
        logger.info("Application stopped")


def main():
    """Entry point"""
    publisher = EpicurePublisher()
    publisher.run()


if __name__ == "__main__":
    main()
