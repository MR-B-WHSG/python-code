"""
12-Bit Floating Point Calculator using Pygame
------------------------------------------------
This application implements a floating point calculator designed for teaching purposes.
It uses a 12-bit representation with:
    • 8 bits for the mantissa (with an implicit binary point after the first bit)
      - For positive numbers, the mantissa starts with 0 (e.g. 0.1101100)
      - For negative numbers, the mantissa starts with 1. In that case, the mantissa is stored
        in two's complement. (e.g. 1.0010100 represents a negative number; its two's complement is 0.1101100)
    • 4 bits for the exponent stored in two's complement (e.g. 0100 for +4, 1110 for –2)

Calculation Process:
    1. Retrieve the 8 mantissa bits and 4 exponent bits from the UI.
    2. For the mantissa:
         - Insert a binary point after the first bit.
         - If the first (sign) bit is 1, compute its two’s complement to obtain the magnitude.
    3. Convert the fixed point mantissa (which is now in the form “0.xxxxxxx”) into a decimal value.
    4. Convert the 4-bit exponent (in two’s complement) into an integer.
    5. Compute the final value as:
             final_value = mantissa_value × (2 ** exponent_value)
         and, if the original mantissa sign bit was 1, the result is negative.
    6. A step-by-step explanation is built and displayed.

This code is designed to align with the presentation used to teach floating point arithmetic.
"""

import pygame
import sys
import math

# Initialize pygame
pygame.init()

# ---------------------------
# Global Constants and Settings
# ---------------------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 30

# Colors for UI elements
BG_COLOR = (30, 30, 30)  # Dark background
TEXT_COLOR = (240, 240, 240)  # Light text
BUTTON_COLOR = (70, 130, 180)  # Steel blue for buttons
BUTTON_HOVER_COLOR = (100, 160, 210)
BIT_COLOR = (200, 200, 200)  # Light grey for bit buttons (0)
BIT_ACTIVE_COLOR = (50, 205, 50)  # Lime green for active bit (1)

# Bit button dimensions
MANTISSA_BIT_SIZE = 40  # Square size for each mantissa bit
EXPONENT_BIT_SIZE = 40  # Square size for each exponent bit
BIT_MARGIN = 10  # Margin between bit buttons

# Define fonts
FONT = pygame.font.SysFont("arial", 20)
SMALL_FONT = pygame.font.SysFont("arial", 16)


# ---------------------------
# UI Helper Classes
# ---------------------------

class Button:
    """
    A clickable UI button.
    Attributes:
        rect: pygame.Rect defining the button's area.
        text: The text label on the button.
        callback: Function to call when the button is clicked.
    """

    def __init__(self, rect, text, callback):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.hovered = False

    def draw(self, surface):
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect)
        # Render text centered on the button
        text_surf = FONT.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback()


class BitButton:
    """
    A clickable square representing a single bit (0 or 1).
    Attributes:
        rect: pygame.Rect defining the area of the bit.
        value: The current bit value (0 or 1).
    """

    def __init__(self, rect, value=0):
        self.rect = pygame.Rect(rect)
        self.value = value

    def draw(self, surface, font):
        # Use BIT_ACTIVE_COLOR if bit is 1, otherwise BIT_COLOR
        color = BIT_ACTIVE_COLOR if self.value == 1 else BIT_COLOR
        pygame.draw.rect(surface, color, self.rect)
        # Draw the bit value (0 or 1) centered in the square
        text_surf = font.render(str(self.value), True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        # Draw a border
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.value = 1 - self.value  # Toggle bit


# ---------------------------
# Helper Functions for Conversions
# ---------------------------
def twos_complement_8bit(bit_list):
    """
    Compute the two's complement of an 8-bit number represented as a list of bits.
    Args:
        bit_list: List of 8 integers (0 or 1) representing the binary number.
    Returns:
        A string of 8 bits representing the two's complement.
    """
    # Convert list of bits to integer
    original = int(''.join(str(b) for b in bit_list), 2)
    # Invert bits (one's complement)
    inverted = (~original) & 0xFF  # Mask to 8 bits
    # Add 1 to get two's complement
    twos_comp = (inverted + 1) & 0xFF
    # Format as an 8-bit binary string
    return format(twos_comp, '08b')


def convert_fixed_point(fp_str):
    """
    Convert an 8-bit fixed-point binary string (with an implicit binary point after the first bit)
    to its decimal value.
    For example, "0.1101100" is computed as:
         0*1 + 1/2 + 1/4 + 0/8 + 1/16 + 1/32 + 0/64 + 0/128.
    Args:
        fp_str: String in the format "X.YYYYYYY" (where X is one digit and YYYYYYY are 7 digits).
    Returns:
        The decimal (float) value.
    """
    if len(fp_str) != 9 or fp_str[1] != '.':
        raise ValueError("Fixed point string must be in the format 'X.YYYYYYY'")
    # The digit before the binary point
    int_part = int(fp_str[0])
    fraction = 0.0
    # Process each fractional digit
    for i, ch in enumerate(fp_str[2:], start=1):
        fraction += int(ch) * (2 ** (-i))
    return int_part + fraction


def convert_exponent(exp_str):
    """
    Convert a 4-bit binary string in two's complement to an integer.
    Args:
        exp_str: 4-bit binary string.
    Returns:
        The integer value (can be negative).
    """
    value = int(exp_str, 2)
    if exp_str[0] == '1':  # Negative number in two's complement
        value -= (1 << len(exp_str))
    return value


# ---------------------------
# Main Application Class
# ---------------------------
class FloatingPointCalculator:
    """
    Main application class for the 12-bit floating point calculator.
    This calculator uses an 8-bit mantissa (with a binary point after the first bit)
    and a 4-bit exponent (in two's complement).
    """

    def __init__(self):
        # Set up the pygame screen and clock.
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("12-bit Floating Point Calculator")
        self.clock = pygame.time.Clock()

        # Create bit button groups.
        # Mantissa: 8 bits displayed in one row.
        self.mantissa_buttons = []
        self.create_mantissa_buttons()

        # Exponent: 4 bits displayed in one row.
        self.exponent_buttons = []
        self.create_exponent_buttons()

        # Create UI buttons.
        self.ui_buttons = []
        self.create_ui_buttons()

        # Store explanation lines for display.
        self.explanation_lines = []

    def create_mantissa_buttons(self):
        """
        Create 8 BitButton objects for the mantissa.
        The first bit is the sign bit (also used for the two's complement if negative).
        The binary point is displayed after the first bit.
        """
        self.mantissa_buttons = []
        start_x = 100
        y = 100
        for i in range(8):
            rect = (start_x + i * (MANTISSA_BIT_SIZE + BIT_MARGIN), y, MANTISSA_BIT_SIZE, MANTISSA_BIT_SIZE)
            btn = BitButton(rect, value=0)
            self.mantissa_buttons.append(btn)

    def create_exponent_buttons(self):
        """
        Create 4 BitButton objects for the exponent.
        """
        self.exponent_buttons = []
        start_x = 100
        y = 200
        for i in range(4):
            rect = (start_x + i * (EXPONENT_BIT_SIZE + BIT_MARGIN), y, EXPONENT_BIT_SIZE, EXPONENT_BIT_SIZE)
            btn = BitButton(rect, value=0)
            self.exponent_buttons.append(btn)

    def create_ui_buttons(self):
        """
        Create UI buttons. For this calculator, we only need a Calculate button.
        """
        btn_width = 140
        btn_height = 40
        calc_rect = (600, 100, btn_width, btn_height)
        calc_btn = Button(calc_rect, "Calculate", self.calculate_value)
        self.ui_buttons.append(calc_btn)

    def calculate_value(self):
        """
        Compute the floating point value based on the 8-bit mantissa and 4-bit exponent.
        Builds a detailed step-by-step explanation.
        """
        explanation = []

        # ---------------------------
        # Process the Mantissa
        # ---------------------------
        # Retrieve the mantissa bits as a list of integers.
        mantissa_bits = [btn.value for btn in self.mantissa_buttons]
        # Build a string from the bits.
        mantissa_str = ''.join(str(b) for b in mantissa_bits)
        # Insert the binary point after the first bit.
        displayed_mantissa = mantissa_str[0] + "." + mantissa_str[1:]
        explanation.append(f"Original Mantissa: {displayed_mantissa}")

        # Check the sign bit (first bit of the mantissa)
        sign_bit = mantissa_bits[0]
        if sign_bit == 1:
            explanation.append("Detected negative number (sign bit = 1).")
            # For negative numbers, compute the two's complement of the 8-bit mantissa to obtain the magnitude.
            tc_str = twos_complement_8bit(mantissa_bits)
            displayed_tc = tc_str[0] + "." + tc_str[1:]
            explanation.append(f"Two's complement of mantissa: {displayed_tc}")
            # Now, convert the two's complement fixed-point representation to decimal.
            try:
                mantissa_value = convert_fixed_point(displayed_tc)
            except ValueError as e:
                mantissa_value = 0.0
                explanation.append(f"Error in conversion: {e}")
        else:
            explanation.append("Positive number detected (sign bit = 0).")
            try:
                mantissa_value = convert_fixed_point(displayed_mantissa)
            except ValueError as e:
                mantissa_value = 0.0
                explanation.append(f"Error in conversion: {e}")
        explanation.append(f"Mantissa value (absolute magnitude): {mantissa_value}")

        # ---------------------------
        # Process the Exponent
        # ---------------------------
        exponent_bits = [btn.value for btn in self.exponent_buttons]
        exp_str = ''.join(str(b) for b in exponent_bits)
        # Convert the 4-bit two's complement exponent string to an integer.
        exponent_value = convert_exponent(exp_str)
        explanation.append(f"Exponent bits: {exp_str} => Exponent value: {exponent_value}")

        # ---------------------------
        # Final Computation
        # ---------------------------
        # Compute the final value: mantissa * 2^(exponent)
        result = mantissa_value * (2 ** exponent_value)
        # If the original sign bit was 1, the final result is negative.
        if sign_bit == 1:
            result = -result
        explanation.append(f"Final result: {mantissa_value} x 2^({exponent_value}) = {result}")

        self.explanation_lines = explanation

    def draw(self):
        """
        Draw all UI elements: the mantissa and exponent bit buttons, the Calculate button,
        labels (including a drawn decimal point for the mantissa), and the step-by-step explanation.
        """
        self.screen.fill(BG_COLOR)

        # Draw UI buttons (e.g. Calculate)
        for btn in self.ui_buttons:
            btn.draw(self.screen)

        # Draw labels for sections
        self.screen.blit(FONT.render("Mantissa (8 bits, with binary point after 1st bit):", True, TEXT_COLOR),
                         (100, 60))
        self.screen.blit(FONT.render("Exponent (4-bit two's complement):", True, TEXT_COLOR), (100, 160))

        # Draw mantissa bit buttons
        for i, btn in enumerate(self.mantissa_buttons):
            btn.draw(self.screen, FONT)
        # Draw the binary point between the first and second mantissa bits
        first_bit_rect = self.mantissa_buttons[0].rect
        # Position the point slightly to the right of the first bit
        point_x = first_bit_rect.right + 2
        point_y = first_bit_rect.centery - 8
        self.screen.blit(FONT.render(".", True, TEXT_COLOR), (point_x, point_y))

        # Draw exponent bit buttons
        for btn in self.exponent_buttons:
            btn.draw(self.screen, FONT)

        # Draw the explanation text area
        start_y = 300
        for i, line in enumerate(self.explanation_lines):
            text_surf = SMALL_FONT.render(line, True, TEXT_COLOR)
            self.screen.blit(text_surf, (50, start_y + i * 25))

        pygame.display.flip()

    def handle_events(self, event):
        """
        Dispatch incoming pygame events to UI and bit buttons.
        """
        for btn in self.ui_buttons:
            btn.handle_event(event)
        for btn in self.mantissa_buttons:
            btn.handle_event(event)
        for btn in self.exponent_buttons:
            btn.handle_event(event)

    def run(self):
        """
        Main loop for the application.
        """
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.handle_events(event)
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()


# ---------------------------
# Entry Point
# ---------------------------
def main():
    calculator = FloatingPointCalculator()
    calculator.run()


if __name__ == '__main__':
    main()