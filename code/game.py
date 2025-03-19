import pygame
import sys
import os

pygame.init()

# Set video mode first
screen = pygame.display.set_mode((1088, 612))
pygame.display.set_caption("Deathtrip - Game")

# --- Config file functions ---
def read_config():
    # Check if config.txt exists; if not create one with default volume=1.0.
    config_path = "config.txt"
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            line = f.readline().strip()
            try:
                vol = float(line.split("=")[1])
            except Exception as e:
                vol = 1.0
            return vol
    else:
        with open(config_path, "w") as f:
            f.write("volume=1.0")
        return 1.0

# Now load assets
button_box_img = pygame.image.load("images/button_box.png").convert_alpha()
try:
    button_click_sound = pygame.mixer.Sound(os.path.join("sound", "button_click.wav"))
    # Read the volume from the config (slider range 0.0–5.0 scaled to 0.0–1.0)
    config_volume = read_config()
    button_click_sound.set_volume(min(config_volume / 5.0, 1.0))
except Exception as e:
    print("Error loading sound:", e)
    button_click_sound = None

font = pygame.font.SysFont("Arial", 24)
WHITE = (255, 255, 255)
DARK_GRAY = (150, 150, 150)

# AnimatedButton class for decisions with button animation and sound
class AnimatedButton:
    def __init__(self, text, x, y, width, height, action):
        self.text = text
        self.base_rect = pygame.Rect(x, y, width, height)
        self.rect = self.base_rect.copy()
        self.action = action
        self.pressed = False
        self.press_offset = 5

    def draw(self, screen):
        scaled_img = pygame.transform.scale(button_box_img, (self.rect.width, self.rect.height))
        screen.blit(scaled_img, (self.rect.x, self.rect.y))
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

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

class Game:
    def __init__(self):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont("Arial", 24)

        # Game state and dialogues
        self.current_scene = "start"
        self.dialogues = {
            "start": "Velg om du vil drikke eller ikke:",
            "decision_1": "Du drakk. Nå må du stoppe vennen din fra å kjøre.",
            "decision_2": "Du valgte å ikke drikke. Nå må du stoppe vennen din.",
            "ending_stop": "Du stoppet vennen din og reddet dagen!",
            "ending_drive": "Vennen din kjørte under påvirkning... en farlig avgjørelse!",
        }
        self.current_dialogue_full = self.dialogues[self.current_scene]
        self.dialogue_progress = ""
        self.dialogue_index = 0
        self.dialogue_timer = 0  # Time accumulator for typewriter effect (ms)
        self.dialogue_finished = False
        self.post_dialogue_timer = 0  # Delay after full dialogue is shown

        # Button layout (for decision buttons)
        self.button_width = 200
        self.button_height = 50
        dialogue_box_height = 100
        bottom_margin = 20
        dialogue_y = 612 - dialogue_box_height - bottom_margin
        self.button_y = dialogue_y - self.button_height - 10
        total_buttons_width = self.button_width * 2 + 20  # two buttons with 20px gap
        self.left_x = (1088 - total_buttons_width) // 2
        self.right_x = self.left_x + self.button_width + 20

        # Decision buttons (will be created when dialogue is cleared)
        self.decision_buttons = {}

    def reset_dialogue(self):
        self.current_dialogue_full = self.dialogues.get(self.current_scene, "")
        self.dialogue_progress = ""
        self.dialogue_index = 0
        self.dialogue_timer = 0
        self.dialogue_finished = False
        self.post_dialogue_timer = 0
        self.decision_buttons = {}

    def update_dialogue(self, dt):
        if not self.dialogue_finished:
            if self.dialogue_index < len(self.current_dialogue_full):
                self.dialogue_timer += dt
                if self.dialogue_timer >= 30:
                    self.dialogue_progress += self.current_dialogue_full[self.dialogue_index]
                    self.dialogue_index += 1
                    self.dialogue_timer = 0
            else:
                self.dialogue_finished = True
                self.post_dialogue_timer = 0
        else:
            self.post_dialogue_timer += dt
            if self.post_dialogue_timer >= 1000:
                self.dialogue_progress = ""

    def draw_text(self, text, x, y, color=(255, 255, 255)):
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))

    def draw_dialogue_box(self, dialogue):
        box_rect = pygame.Rect(20, 612 - 100 - 20, 1088 - 40, 100)
        pygame.draw.rect(self.screen, (50, 50, 50), box_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), box_rect, 2)
        self.draw_text(dialogue, box_rect.x + 10, box_rect.y + 10)

    def create_decision_buttons(self):
        if self.current_scene == "start":
            self.decision_buttons = {
                "drink": AnimatedButton("Drikk", self.left_x, self.button_y, self.button_width, self.button_height,
                                          lambda: self.handle_decision("drink")),
                "no_drink": AnimatedButton("Ikke drikk", self.right_x, self.button_y, self.button_width, self.button_height,
                                           lambda: self.handle_decision("no_drink")),
            }
        elif self.current_scene in ["decision_1", "decision_2"]:
            self.decision_buttons = {
                "stop_friend": AnimatedButton("Stoppe", self.left_x, self.button_y, self.button_width, self.button_height,
                                              lambda: self.handle_decision("stop_friend")),
                "let_drive": AnimatedButton("La han kjøre", self.right_x, self.button_y, self.button_width, self.button_height,
                                            lambda: self.handle_decision("let_drive")),
            }

    def handle_decision(self, decision):
        if decision == "drink":
            self.current_scene = "decision_1"
        elif decision == "no_drink":
            self.current_scene = "decision_2"
        elif decision == "stop_friend":
            print("You stopped your friend!")
            self.current_scene = "ending_stop"
        elif decision == "let_drive":
            print("Your friend drives under influence...")
            self.current_scene = "ending_drive"
        self.reset_dialogue()

    def draw_scene(self):
        self.screen.fill((0, 0, 0))
        if self.dialogue_progress != "":
            self.draw_dialogue_box(self.dialogue_progress)
        else:
            if not self.decision_buttons:
                self.create_decision_buttons()
            for btn in self.decision_buttons.values():
                btn.update()
                btn.draw(self.screen)

    def run(self):
        while self.running:
            dt = self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if self.dialogue_progress == "" and self.decision_buttons:
                    for btn in self.decision_buttons.values():
                        btn.handle_event(event)
            self.update_dialogue(dt)
            self.draw_scene()
            pygame.display.flip()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()