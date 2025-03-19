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
        color = BIT_ACTIVE_COLOR if self.value == 1 else BIT_COLOR
        pygame.draw.rect(surface, color, self.rect)
        text_surf = font.render(str(self.value), True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
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
    original = int(''.join(str(b) for b in bit_list), 2)
    inverted = (~original) & 0xFF
    twos_comp = (inverted + 1) & 0xFF
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
    int_part = int(fp_str[0])
    fraction = 0.0
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
    if exp_str[0] == '1':
        value -= (1 << len(exp_str))
    return value

def int_to_twos_complement(value, bits):
    """
    Convert an integer to a two's complement binary string of a given bit width.
    Args:
        value: Integer value to convert.
        bits: Total number of bits for the representation.
    Returns:
        A string representing the two's complement binary.
    """
    if value < 0:
        value = (1 << bits) + value
    return format(value, f'0{bits}b')

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
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("12-bit Floating Point Calculator")
        self.clock = pygame.time.Clock()
        self.mantissa_buttons = []
        self.create_mantissa_buttons()
        self.exponent_buttons = []
        self.create_exponent_buttons()
        self.ui_buttons = []
        self.create_ui_buttons()
        self.explanation_lines = []
        self.denary_input = ""
        self.denary_input_rect = pygame.Rect(600, 220, 140, 40)

    def create_mantissa_buttons(self):
        self.mantissa_buttons = []
        start_x = 100
        y = 100
        for i in range(8):
            rect = (start_x + i * (MANTISSA_BIT_SIZE + BIT_MARGIN), y, MANTISSA_BIT_SIZE, MANTISSA_BIT_SIZE)
            btn = BitButton(rect, value=0)
            self.mantissa_buttons.append(btn)

    def create_exponent_buttons(self):
        self.exponent_buttons = []
        start_x = 100
        y = 200
        for i in range(4):
            rect = (start_x + i * (EXPONENT_BIT_SIZE + BIT_MARGIN), y, EXPONENT_BIT_SIZE, EXPONENT_BIT_SIZE)
            btn = BitButton(rect, value=0)
            self.exponent_buttons.append(btn)

    def create_ui_buttons(self):
        btn_width = 140
        btn_height = 40
        calc_rect = (600, 100, btn_width, btn_height)
        calc_btn = Button(calc_rect, "Calculate", self.calculate_value)
        self.ui_buttons.append(calc_btn)
        denary_btn_rect = (600, 160, btn_width, btn_height)
        denary_btn = Button(denary_btn_rect, "From Denary", self.convert_from_denary)
        self.ui_buttons.append(denary_btn)

    def convert_from_denary(self):
        """
        Convert the denary input into the floating-point bit representation.
        """
        explanation = []
        try:
            denary_value = float(self.denary_input)
            if denary_value == 0:
                explanation.append("Input is zero. Setting all bits to zero.")
                for btn in self.mantissa_buttons:
                    btn.value = 0
                for btn in self.exponent_buttons:
                    btn.value = 0
            else:
                sign_bit = 0 if denary_value > 0 else 1
                abs_value = abs(denary_value)
                exponent_value = math.floor(math.log2(abs_value)) + 1
                mantissa_value = abs_value / (2 ** exponent_value)

                # Compute the 7 fractional bits for the mantissa
                frac_bits = []
                for i in range(7):
                    mantissa_value *= 2
                    if mantissa_value >= 1:
                        frac_bits.append(1)
                        mantissa_value -= 1
                    else:
                        frac_bits.append(0)

                # Build the positive mantissa string: a leading '0' plus the 7 fractional bits
                pos_mantissa_str = '0' + ''.join(str(b) for b in frac_bits)
                if sign_bit == 1:
                    # For negative numbers, convert the positive mantissa to its two's complement
                    final_mantissa_str = twos_complement_8bit(list(map(int, list(pos_mantissa_str))))
                else:
                    final_mantissa_str = pos_mantissa_str

                # Update mantissa buttons
                for i, btn in enumerate(self.mantissa_buttons):
                    btn.value = int(final_mantissa_str[i])

                # Convert exponent to 4-bit two's complement
                exponent_bits = int_to_twos_complement(exponent_value, 4)
                for i, btn in enumerate(self.exponent_buttons):
                    btn.value = int(exponent_bits[i])

                explanation.append(f"Converted denary {denary_value} to mantissa {final_mantissa_str} and exponent {exponent_bits}.")
            self.explanation_lines = explanation
        except ValueError:
            self.explanation_lines = ["Invalid input for denary conversion."]

    def calculate_value(self):
        """
        Compute the floating point value based on the 8-bit mantissa and 4-bit exponent.
        Builds a detailed step-by-step explanation.
        """
        explanation = []
        # Process the Mantissa
        mantissa_bits = [btn.value for btn in self.mantissa_buttons]
        mantissa_str = ''.join(str(b) for b in mantissa_bits)
        displayed_mantissa = mantissa_str[0] + "." + mantissa_str[1:]
        explanation.append(f"Original Mantissa: {displayed_mantissa}")
        sign_bit = mantissa_bits[0]
        if sign_bit == 1:
            explanation.append("Detected negative number (sign bit = 1).")
            tc_str = twos_complement_8bit(mantissa_bits)
            displayed_tc = tc_str[0] + "." + tc_str[1:]
            explanation.append(f"Two's complement of mantissa: {displayed_tc}")
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

        # Process the Exponent
        exponent_bits = [btn.value for btn in self.exponent_buttons]
        exp_str = ''.join(str(b) for b in exponent_bits)
        exponent_value = convert_exponent(exp_str)
        explanation.append(f"Exponent bits: {exp_str} => Exponent value: {exponent_value}")

        # Final Computation
        result = mantissa_value * (2 ** exponent_value)
        if sign_bit == 1:
            result = -result
        explanation.append(f"Final result: {mantissa_value} x 2^({exponent_value}) = {result}")
        self.denary_input = str(result)
        self.explanation_lines = explanation

    def draw(self):
        self.screen.fill(BG_COLOR)
        for btn in self.ui_buttons:
            btn.draw(self.screen)
        pygame.draw.rect(self.screen, TEXT_COLOR, self.denary_input_rect, 2)
        input_surf = FONT.render(self.denary_input, True, TEXT_COLOR)
        self.screen.blit(input_surf, (self.denary_input_rect.x + 5, self.denary_input_rect.y + 5))
        self.screen.blit(FONT.render("Mantissa (8 bits, with binary point after 1st bit):", True, TEXT_COLOR), (100, 60))
        self.screen.blit(FONT.render("Exponent (4-bit two's complement):", True, TEXT_COLOR), (100, 160))
        for i, btn in enumerate(self.mantissa_buttons):
            btn.draw(self.screen, FONT)
        first_bit_rect = self.mantissa_buttons[0].rect
        point_x = first_bit_rect.right + 2
        point_y = first_bit_rect.centery - 8
        self.screen.blit(FONT.render(".", True, TEXT_COLOR), (point_x, point_y))
        for btn in self.exponent_buttons:
            btn.draw(self.screen, FONT)
        start_y = 300
        for i, line in enumerate(self.explanation_lines):
            text_surf = SMALL_FONT.render(line, True, TEXT_COLOR)
            self.screen.blit(text_surf, (50, start_y + i * 25))
        pygame.display.flip()

    def handle_events(self, event):
        for btn in self.ui_buttons:
            btn.handle_event(event)
        for btn in self.mantissa_buttons:
            btn.handle_event(event)
        for btn in self.exponent_buttons:
            btn.handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.denary_input = self.denary_input[:-1]
            else:
                self.denary_input += event.unicode

    def run(self):
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

def main():
    calculator = FloatingPointCalculator()
    calculator.run()

if __name__ == '__main__':
    main()