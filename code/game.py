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
            "start": [
                "Venn: Hei, kom og ta en shot med oss!",
                "Du: Jeg vet ikke, jeg skal tidlig opp i morgen.",
                "Venn: Slapp av, én drink skader ikke! Vi skal jo bare ha det gøy."
            ],
            # These keys represent what happens right after the "start" scene.
            "decision_drink": [
                "Du drakk."
            ],
            "decision_no_drink": [
                "Du valgte å ikke drikke.",
            ],
            "scene_2": [
                "Du: Hva gjør du?",
                "Vennen: Jeg skal hjem. Det går fint, jeg har kontroll.",
                "Du: Er du sikker på at du burde kjøre? Kanskje det er bedre å vente litt eller få noen til å kjøre deg?",
                "Vennen: Slapp av, jeg føler meg helt fin. Det er ingen problem.",
                "Du: Det handler ikke bare om deg. Hva om noe skjer?",
                "Vennen: Det skjer ikke noe, jeg har full kontroll. Slutt å bekymre deg."
            ],
            "decision_exit": [
                "Stoppe de fra å gå ut?",
                "A: Ja", # (Kutter til info)
                "B: Nei" # (Gå videre til mer dialog, scenebytte)
            ],
            "scene_3": [
                "Du: Vent litt, kanskje vi heller kan bestille en taxi?",
                "Vennen: Nei, nei, jeg er helt fin. Dette går bra.",
                "Du: Men tenk om noe skjer? Det er ikke verdt risikoen.",
                "Vennen: Jeg sier det går fint. Hvorfor lager du så mye drama?"
            ],
            "decision_try_stop": [
                "Prøve igjen å stoppe de fra å kjøre?",
                "A: Ja", # (Kutter til info)
                "B: Nei" # (Vennen starter bilen, dør lukkes, gå til neste scene.)
            ],
            "scene_4": [
                "Vennen: Kom igjen, bare hopp inn, vi kommer oss kjapt hjem!",
                "Du: Jeg vet ikke... Jeg føler meg ikke trygg.",
                "Vennen: Slutt å overtenke, det går bra! Vil du hjem eller ikke?"
            ],
            "decision_seat": [
                "Sitte på eller ikke?",
                "A: Nei",
                "B: Ja"
            ],
            "ending_stop": [
                "Du stoppet vennen din"
            ],
            "ending_drive": [
                "Vennen din kjørte under påvirkning..."
            ]
        }
        self.current_dialogue_full = self.dialogues[self.current_scene]
        self.dialogue_progress = ""
        self.dialogue_index = 0
        self.current_line_index = 0   # <-- Add this line to track which dialogue line you're on.
        self.dialogue_timer = 0       # Time accumulator for typewriter effect (ms)
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
    # Now current_dialogue_full will be the list of lines for the current scene.
        self.current_dialogue_full = self.dialogues.get(self.current_scene, [])
        self.current_line_index = 0         # Which dialogue line we're on.
        self.dialogue_progress = ""         # The current text being typewritten.
        self.dialogue_timer = 0             # Timer for typewriter effect.
        self.dialogue_finished = False      # True when the current line is fully displayed.
        self.post_dialogue_timer = 0        # Delay after finished before advancing.
        self.decision_buttons = {}          # Clear decision buttons.

    def update_dialogue(self, dt):
        # If there are still lines to show.
        if self.current_line_index < len(self.current_dialogue_full):
            # If the current line is not finished, do the typewriter effect.
            if not self.dialogue_finished:
                if self.dialogue_index < len(self.current_dialogue_full[self.current_line_index]):
                    self.dialogue_timer += dt
                    if self.dialogue_timer >= 30:  # adjust to your preferred speed
                        self.dialogue_progress += self.current_dialogue_full[self.current_line_index][self.dialogue_index]
                        self.dialogue_index += 1
                        self.dialogue_timer = 0
                else:
                    self.dialogue_finished = True
                    self.post_dialogue_timer = 0
            else:
                # Optionally wait a moment after finishing the line before advancing.
                self.post_dialogue_timer += dt
                # Advance to the next line when space is pressed or after a set delay (e.g., 1000 ms):
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE] or self.post_dialogue_timer >= 1000:
                    self.current_line_index += 1
                    self.dialogue_progress = ""
                    self.dialogue_index = 0
                    self.dialogue_timer = 0
                    self.dialogue_finished = False
        else:
            # All dialogue lines are done.
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
         # Transition to the dialogue that follows if the player drank.
         self.current_scene = "decision_drink"
        elif decision == "no_drink":
            self.current_scene = "decision_no_drink"
        elif decision == "exit_decision":
            self.current_scene = "scene_2"
        elif decision == "try_stop":
            self.current_scene = "decision_try_stop"
        elif decision == "seat":
            self.current_scene = "decision_seat"
        # etc, mapping your decision choices to the next key in the dialogue chain.

        self.reset_dialogue()

    def draw_scene(self):
        self.screen.fill((0, 0, 0))
        # If there are still dialogue lines left, show the dialogue box.
        if self.current_line_index < len(self.current_dialogue_full):
            self.draw_dialogue_box(self.dialogue_progress)
        else:
            # When all dialogue lines have been shown, create decision buttons if they haven't been created.
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