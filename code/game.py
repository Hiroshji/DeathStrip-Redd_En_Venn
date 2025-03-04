import pygame
import sys
import time
from assets import load_image

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont("Arial", 24)

        # Game states
        self.state = "menu"  # "menu", "info", "game"
        self.current_scene = "start"

    def draw_text(self, text, x, y):
        text_surface = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(text_surface, (x, y))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if self.state == "menu":
                    if event.key == pygame.K_1:
                        self.state = "game"  # Start the game
                    elif event.key == pygame.K_2:
                        self.state = "info"  # Show info screen
                elif self.state == "info":
                    if event.key == pygame.K_RETURN:  # Press Enter to go back
                        self.state = "menu"
                elif self.state == "game":
                    if event.key == pygame.K_1:
                        self.current_scene = "decision_1"
                    elif event.key == pygame.K_2:
                        self.current_scene = "decision_2"

    def run(self):
        while self.running:
            self.handle_input()
            self.screen.fill((0, 0, 0))  # Clear screen
            
            if self.state == "menu":
                self.draw_text("Velkommen til Redd en venn", 50, 50)
                self.draw_text("1: Nytt spill", 50, 150)
                self.draw_text("2: Info", 50, 200)
            
            elif self.state == "info":
                self.draw_text("Om spillet:", 50, 50)
                self.draw_text("Du må stoppe vennene dine fra å ruskjøre.", 50, 100)
                self.draw_text("Trykk ENTER for å gå tilbake.", 50, 200)

            elif self.state == "game":
                if self.current_scene == "start":
                    self.draw_text("Velg om du vil drikke eller ikke:", 50, 50)
                    self.draw_text("1: Drikk", 50, 150)
                    self.draw_text("2: Ikke drikk", 50, 200)
                elif self.current_scene == "decision_1":
                    self.draw_text("Du drakk. Nå må du stoppe vennen din fra å kjøre.", 50, 50)
                    self.draw_text("1: Stoppe", 50, 150)
                    self.draw_text("2: La han kjøre", 50, 200)
                elif self.current_scene == "decision_2":
                    self.draw_text("Du valgte å ikke drikke. Nå må du stoppe vennen din.", 50, 50)
                    self.draw_text("1: Stoppe", 50, 150)
                    self.draw_text("2: La han kjøre", 50, 200)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()
