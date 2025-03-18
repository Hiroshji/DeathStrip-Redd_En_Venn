import pygame
import sys

pygame.init()

# Screen settings
SCREEN_WIDTH, SCREEN_HEIGHT = 1088, 612
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Settings")

# Colors and font
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (150, 150, 150)
BLACK = (0, 0, 0)
font = pygame.font.Font(None, 36)

# Load the button click sound from the "sound" folder using try/except
try:
    button_click_sound = pygame.mixer.Sound("sound/button.click")  # Adjust name/extension if necessary.
    button_click_sound.set_volume(0.5)  # Default volume
except Exception as e:
    print("Error loading sound:", e)
    button_click_sound = None

# Animated button that moves down/up on click and plays sound
class AnimatedButton:
    def __init__(self, text, x, y, width, height, action):
        self.text = text
        self.base_rect = pygame.Rect(x, y, width, height)
        self.rect = self.base_rect.copy()
        self.action = action
        self.hovered = False
        self.pressed = False
        self.press_offset = 5  # How many pixels to move down when pressed

    def draw(self, surface):
        pygame.draw.rect(surface, DARK_GRAY, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def update(self):
        if self.pressed:
            self.rect.y = self.base_rect.y + self.press_offset
        else:
            self.rect.y = self.base_rect.y

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                if button_click_sound:
                    button_click_sound.play()
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed:
                self.pressed = False
                if self.rect.collidepoint(event.pos):
                    self.action()

# Simple horizontal slider to control the button click sound volume
class Slider:
    def __init__(self, x, y, width, height, min_val=0.0, max_val=1.0, initial=0.5):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial
        self.handle_radius = height // 2
        self.handle_x = x + int((self.value - self.min_val) / (self.max_val - self.min_val) * width)
        self.dragging = False

    def draw(self, surface):
        # Draw slider track
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        # Draw the handle
        handle_center = (self.handle_x, self.rect.centery)
        pygame.draw.circle(surface, DARK_GRAY, handle_center, self.handle_radius)

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            handle_rect = pygame.Rect(
                self.handle_x - self.handle_radius,
                self.rect.centery - self.handle_radius,
                self.handle_radius * 2,
                self.handle_radius * 2,
            )
            if handle_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.handle_x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width))
            ratio = (self.handle_x - self.rect.x) / self.rect.width
            self.value = self.min_val + ratio * (self.max_val - self.min_val)
            if button_click_sound:
                button_click_sound.set_volume(self.value)

def settings_screen():
    clock = pygame.time.Clock()
    running = True

    # Create an animated sample button
    sample_button = AnimatedButton("Test Button", 100, 100, 200, 50,
                                   lambda: print("Button action executed"))
    # Create a volume slider for controlling button sound volume
    slider = Slider(100, 200, 300, 20, initial=0.5)

    while running:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            sample_button.handle_event(event)
            slider.update(event)

        sample_button.update()

        screen.fill(BLACK)
        sample_button.draw(screen)
        slider.draw(screen)

        # Display current volume value
        volume_text = font.render(f"Volume: {slider.value:.2f}", True, WHITE)
        screen.blit(volume_text, (100, 240))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    settings_screen()