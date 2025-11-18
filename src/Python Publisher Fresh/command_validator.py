"""
Simple command validator for motor and LED commands
"""

import logging

logger = logging.getLogger(__name__)


class CommandValidator:
    """Validates and returns formatted commands"""

    @staticmethod
    def validate_motor_command(steps, direction):
        """Validate motor command
        
        Args:
            steps (int): Number of steps (0-10000)
            direction (int): Direction 0 or 1
            
        Returns:
            str: Formatted command if valid, None otherwise
        """
        try:
            steps = int(steps)
            direction = int(direction)

            if not (0 <= steps <= 10000):
                logger.error(f"Invalid steps: {steps}. Must be 0-10000")
                return None

            if direction not in [0, 1]:
                logger.error(f"Invalid direction: {direction}. Must be 0 or 1")
                return None

            command = f"motor:{steps}:{direction}"
            logger.debug(f"Valid motor command: {command}")
            return command

        except ValueError as e:
            logger.error(f"Invalid motor command format: {e}")
            return None

    @staticmethod
    def validate_led_command(state):
        """Validate LED command
        
        Args:
            state (str): 'on' or 'off'
            
        Returns:
            str: Formatted command if valid, None otherwise
        """
        state = state.lower().strip()

        if state not in ["on", "off"]:
            logger.error(f"Invalid LED state: {state}. Must be 'on' or 'off'")
            return None

        command = f"led:{state}"
        logger.debug(f"Valid LED command: {command}")
        return command

    @staticmethod
    def parse_user_input(user_input):
        """Parse user input and return formatted command
        
        Args:
            user_input (str): Raw user input
            
        Returns:
            str: Formatted command or None
        """
        user_input = user_input.strip()

        if not user_input:
            logger.error("Empty command")
            return None

        parts = user_input.split(":")

        if len(parts) == 3 and parts[0].lower() == "motor":
            return CommandValidator.validate_motor_command(parts[1], parts[2])

        elif len(parts) == 2 and parts[0].lower() == "led":
            return CommandValidator.validate_led_command(parts[1])

        else:
            logger.error(f"Unknown command format: {user_input}")
            return None
