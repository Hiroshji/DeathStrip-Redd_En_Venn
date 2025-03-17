import pygame
import sys
import os

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH, SCREEN_HEIGHT = 1088, 612
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Deathtrip - Menu")

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (150, 150, 150)
BLACK = (0, 0, 0)

# Fonts
font = pygame.font.Font(None, 36)

# Load images
button_box_img = pygame.image.load("images/button_box.png").convert_alpha()
background_menu_img = pygame.image.load("images/background_menu.png").convert()
background_menu_img = pygame.transform.scale(background_menu_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Button class
class Button:
    def __init__(self, text, x, y, width, height, action):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.action = action
        self.hovered = False

    def draw(self, screen):
        # Use the button image scaled to button size
        scaled_img = pygame.transform.scale(button_box_img, (self.rect.width, self.rect.height))
        screen.blit(scaled_img, (self.rect.x, self.rect.y))
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def check_click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.action()

# Button actions
def start_game():
    import game
    game.Game().run()

def show_info():
    info_screen()

# Info screen
def info_screen():
    # Use the same background image for a consistent look
    background_img = background_menu_img
    def go_back():
        nonlocal running_info
        running_info = False

    # Create a local "Back" button (position stays the same as before)
    back_button = Button("Back", 20, SCREEN_HEIGHT - 60, 150, 50, go_back)
    running_info = True
    while running_info:
        # Blit the background image
        screen.blit(background_img, (0, 0))
        
        # Draw a plain rectangle as the background for the info text
        box_rect = pygame.Rect(20, SCREEN_HEIGHT // 2 - 50, SCREEN_WIDTH - 40, 100)
        pygame.draw.rect(screen, DARK_GRAY, box_rect)
        pygame.draw.rect(screen, WHITE, box_rect, 2)
        
        # Render the info text in white
        text_surf = font.render("Deathtrip: Stop friends from driving under influence", True, WHITE)
        text_rect = text_surf.get_rect(center=box_rect.center)
        screen.blit(text_surf, text_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        back_button.check_hover(mouse_pos)
        back_button.draw(screen)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running_info = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                back_button.check_click(event.pos)
        
        pygame.display.flip()

# Create buttons for main menu
buttons = [
    Button("New Game", 20, SCREEN_HEIGHT - 120, 150, 50, start_game),
    Button("Info", 20, SCREEN_HEIGHT - 60, 150, 50, show_info)
]

def run_menu():
    running = True
    while running:
        # Use the background image for the main menu
        screen.blit(background_menu_img, (0, 0))
        mouse_pos = pygame.mouse.get_pos()
        
        for button in buttons:
            button.check_hover(mouse_pos)
            button.draw(screen)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    button.check_click(event.pos)
                    
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    run_menu()