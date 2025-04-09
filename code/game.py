import sys, os
import pygame

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

pygame.init()

# Set video mode
SCREEN_WIDTH, SCREEN_HEIGHT = 1088, 612
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
if __name__ == "__main__":
    pygame.display.set_caption("Settings")

# --- Config file functions ---
def read_config():
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

# Load the new image for decision buttons
decision_image = pygame.image.load(resource_path("images/button_icon.png")).convert_alpha()

def new_decision_draw(self, screen):
    scaled_img = pygame.transform.smoothscale(decision_image, (self.rect.width, self.rect.height))
    screen.blit(scaled_img, (self.rect.x, self.rect.y))
    text_surf = font.render(self.text, True, WHITE)
    text_rect = text_surf.get_rect(center=self.rect.center)
    screen.blit(text_surf, text_rect)

# Load assets
button_box_img = pygame.image.load(resource_path("images/button_box.png")).convert_alpha()
try:
    button_click_sound = pygame.mixer.Sound(resource_path(os.path.join("sound", "button_click.wav")))
    config_volume = read_config()
    button_click_sound.set_volume(min(config_volume/5.0, 1.0))
except Exception as e:
    print("Error loading sound:", e)
    button_click_sound = None

font = pygame.font.SysFont("Arial", 24)
WHITE = (255, 255, 255)
DARK_GRAY = (150, 150, 150)

# AnimatedButton class for decisions (with sound and animation)
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
    def __init__(self, start_scene="start"):
        self.screen = screen
        pygame.display.set_caption("Death Trip - Redd en venn")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont("Arial", 24)
        
        # Music settings
        self.config_volume = read_config()
        self.music_on = True
        self.current_music = None  # To track which music is loaded
        
        # Create a persistent Music toggle button (positioned at top-left)
        self.music_button = AnimatedButton("Musikk: på", 20, 20, 120, 40, self.toggle_music)
        
        # Load the original images for scene "start"
        original_you = pygame.image.load(resource_path("images/you.png")).convert_alpha()
        original_venn = pygame.image.load(resource_path("images/venn.png")).convert_alpha()
        target_width = 300  # Change this value for a different size
        you_width, you_height = original_you.get_size()
        venn_width, venn_height = original_venn.get_size()
        you_scale = target_width / you_width
        venn_scale = target_width / venn_width
        self.you_img = pygame.transform.scale(original_you, (target_width, int(you_height * you_scale)))
        self.venn_img = pygame.transform.scale(original_venn, (target_width, int(venn_height * venn_scale)))
        
        # Load alternate images for scenes after "start"
        alt_you1 = pygame.image.load(resource_path("images/concerned_you1.png")).convert_alpha()
        alt_you2 = pygame.image.load(resource_path("images/concerned_you2.png")).convert_alpha()
        concerned_you_scale = target_width / alt_you1.get_width()
        self.concerned_you_imgs = [
            pygame.transform.scale(alt_you1, (target_width, int(alt_you1.get_height() * concerned_you_scale))),
            pygame.transform.scale(alt_you2, (target_width, int(alt_you2.get_height() * concerned_you_scale)))
        ]
        
        alt_venn1 = pygame.image.load(resource_path("images/drunk_venn1.png")).convert_alpha()
        alt_venn2 = pygame.image.load(resource_path("images/drunk_venn2.png")).convert_alpha()
        alt_venn3 = pygame.image.load(resource_path("images/drunk_venn3.png")).convert_alpha()
        drunk_venn_scale = target_width / alt_venn1.get_width()
        self.drunk_venn_imgs = [
            pygame.transform.scale(alt_venn1, (target_width, int(alt_venn1.get_height() * drunk_venn_scale))),
            pygame.transform.scale(alt_venn2, (target_width, int(alt_venn2.get_height() * drunk_venn_scale))),
            pygame.transform.scale(alt_venn3, (target_width, int(alt_venn3.get_height() * drunk_venn_scale)))
        ]
        
        # Counters to cycle images when characters speak
        self.du_img_index = 0
        self.venn_img_index = 0
        
        # Set the starting scene based on the parameter.
        self.current_scene = start_scene
        
        # Preload chapter backgrounds (using resource_path for all images)
        self.backgrounds = {
            "start": pygame.transform.scale(pygame.image.load(resource_path("images/chapter1.jpg")).convert(), (1088, 612)),
            "decision_drink": pygame.transform.scale(pygame.image.load(resource_path("images/chapter2.jpg")).convert(), (1088, 612)),
            "decision_no_drink": pygame.transform.scale(pygame.image.load(resource_path("images/chapter2.jpg")).convert(), (1088, 612)),
            "scene_2": pygame.transform.scale(pygame.image.load(resource_path("images/chapter3_start.jpg")).convert(), (1088, 612)),
            "decision_exit": pygame.transform.scale(pygame.image.load(resource_path("images/chapter3_start.jpg")).convert(), (1088, 612)),
            "scene_3": pygame.transform.scale(pygame.image.load(resource_path("images/chapter4.jpg")).convert(), (1088, 612)),
            "decision_try_stop": pygame.transform.scale(pygame.image.load(resource_path("images/chapter4.jpg")).convert(), (1088, 612)),
            "scene_4": pygame.transform.scale(pygame.image.load(resource_path("images/chapter4.jpg")).convert(), (1088, 612)),
            "decision_seat": pygame.transform.scale(pygame.image.load(resource_path("images/chapter4.jpg")).convert(), (1088, 612)),
            "ending_stop": pygame.transform.scale(pygame.image.load(resource_path("images/chapter5.jpg")).convert(), (1088, 612)),
            "ending_drive": pygame.transform.scale(pygame.image.load(resource_path("images/chapter5.jpg")).convert(), (1088, 612))
        }
        self.scene2_end_bg = pygame.transform.scale(pygame.image.load(resource_path("images/chapter3_end.jpg")).convert(), (1088, 612))
        
        # Game state and dialogues (script based on your story)
        self.dialogues = {
            "start": [
                "Venn: Hei, kom og ta en shot med oss!",
                "Du: Jeg vet ikke, jeg skal tidlig opp i morgen.",
                "Venn: Slapp av, én drink skader ikke! Vi skal jo bare ha det gøy."
            ],
            "scene_2": [
                "Du: Hva gjør du?",
                "Venn: Jeg skal hjem. Det går fint, jeg har kontroll.",
                "Du: Er du sikker? Kanskje det er bedre å vente litt eller få noen til å kjøre deg?",
                "Venn: Slapp av, jeg føler meg helt fin. Det er ikke noe problem.",
                "Du: Det handler ikke bare om deg. Hva om noe skjer?",
                "Venn: Det skjer ikke noe, jeg har full kontroll. Slutt å bekymre deg."
            ],
            "scene_3": [
                "Du: Vent litt, kanskje vi heller kan bestille en taxi?",
                "Venn: Nei, nei, jeg har det helt fint. Dette går bra.",
                "Du: Men tenk om noe skjer? Det er ikke verdt risikoen.",
                "Venn: Jeg sier det går fint. Hvorfor lager du så mye drama?"
            ],
            "scene_4": [
                "Venn: Kom igjen, bare hopp inn, vi kommer oss kjapt hjem!",
                "Du: Jeg vet ikke... Jeg føler meg ikke trygg.",
                "Venn: Slutt å overtenke, det går bra! Vil du hjem eller ikke?"
            ],
            "ending_stop": [
                "Dette kan bli realiteten."
            ],
            "ending_drive": [
                "Vennen din kjørte under påvirkning ..."
            ],
            "info_drink": [
                "Ruspåvirket tilstand er en av hovedårsakene til at unge dør i trafikken."
            ],
            "info_exit_A": [
                "1 pils og du er på grensa. 0,2 promille kan endre alt."
            ],
            "info_try_stop_A": [
                "1 av 4 dødsulykker i trafikken skyldes rus."
            ],
            "info_sete_B": [
                "Det er ikke bare ditt liv du setter på spill. 1 av 3 som dør i trafikken er ikke sjåfør."
            ]
        }
        self.current_dialogue_full = self.dialogues[self.current_scene]
        self.dialogue_progress = ""
        self.dialogue_index = 0
        self.current_line_index = 0   # Track which dialogue line you're on.
        self.dialogue_timer = 0       # Timer for typewriter effect (ms)
        self.dialogue_finished = False
        self.post_dialogue_timer = 0  # (Not used for auto-advance)
        
        # Button layout (for decision buttons)
        self.button_width = 127
        self.button_height = 71
        dialogue_box_height = 100
        bottom_margin = 20
        dialogue_y = 612 - dialogue_box_height - bottom_margin
        self.button_y = dialogue_y - self.button_height - 10
        gap = 100  # increased gap between buttons
        total_buttons_width = self.button_width * 2 + gap  # two buttons with gap
        self.left_x = (1088 - total_buttons_width) // 2
        self.right_x = self.left_x + self.button_width + gap
        
        # Decision buttons (will be created when dialogue is finished)
        self.decision_buttons = {}
        self.info_mode = False
        self.info_text = ""
        # Set a flag for alternate (cycling) images once we leave the "start" scene.
        self.alternate = (self.current_scene != "start")
        
        # Initialize fade parameters for ending and load logo image.
        self.ending_fade = 0
        try:
            self.logo_img = pygame.image.load(resource_path("images/logo.png")).convert_alpha()
        except Exception as e:
            print("Error loading logo image:", e)
            self.logo_img = None

    def toggle_music(self):
        self.music_on = not self.music_on
        self.music_button.text = "Musikk: på" if self.music_on else "Musikk: av"
        if self.music_on:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()

    def reset_dialogue(self):
        self.current_dialogue_full = self.dialogues.get(self.current_scene, [])
        self.current_line_index = 0
        self.dialogue_progress = ""
        self.dialogue_index = 0
        self.dialogue_timer = 0
        self.dialogue_finished = False
        self.post_dialogue_timer = 0
        self.decision_buttons = {}
        self.alternate = (self.current_scene != "start")
        self.du_img_index = 0
        self.venn_img_index = 0

    def update_dialogue(self, dt):
        if self.current_line_index < len(self.current_dialogue_full):
            if not self.dialogue_finished:
                if self.dialogue_index < len(self.current_dialogue_full[self.current_line_index]):
                    self.dialogue_timer += dt
                    if self.dialogue_timer >= 30:
                        self.dialogue_progress += self.current_dialogue_full[self.current_line_index][self.dialogue_index]
                        self.dialogue_index += 1
                        self.dialogue_timer = 0
                else:
                    self.dialogue_finished = True
        else:
            self.dialogue_progress = ""

    def advance_dialogue(self):
        if self.dialogue_finished:
            if self.current_line_index < len(self.current_dialogue_full):
                if self.alternate:
                    current_line = self.current_dialogue_full[self.current_line_index]
                    if current_line.startswith("Du:"):
                        self.du_img_index = (self.du_img_index + 1) % len(self.concerned_you_imgs)
                    elif current_line.startswith("Venn:"):
                        self.venn_img_index = (self.venn_img_index + 1) % len(self.drunk_venn_imgs)
                self.current_line_index += 1
                self.dialogue_progress = ""
                self.dialogue_index = 0
                self.dialogue_timer = 0
                self.dialogue_finished = False

            if self.current_line_index >= len(self.current_dialogue_full) and \
            (self.current_scene.startswith("info_") or self.current_scene.startswith("ending_")):
                self.info_transition()

    def draw_text(self, text, x, y, color=(255, 255, 255)):
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))

    def draw_dialogue_box(self, dialogue):
        box_rect = pygame.Rect(20, 612 - 100 - 20, 1088 - 40, 100)
        pygame.draw.rect(self.screen, (50, 50, 50), box_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), box_rect, 2)
        
        if self.current_line_index < len(self.current_dialogue_full):
            current_line = self.current_dialogue_full[self.current_line_index]
            if self.alternate:
                if current_line.startswith("Du:"):
                    img = self.concerned_you_imgs[self.du_img_index]
                    y_pos = box_rect.top - img.get_height()
                    self.screen.blit(img, (150, y_pos))
                elif current_line.startswith("Venn:"):
                    img = self.drunk_venn_imgs[self.venn_img_index]
                    y_pos = box_rect.top - img.get_height()
                    self.screen.blit(img, (1088 - img.get_width() - 150, y_pos))
            else:
                if current_line.startswith("Du:"):
                    y_pos = box_rect.top - self.you_img.get_height()
                    self.screen.blit(self.you_img, (150, y_pos))
                elif current_line.startswith("Venn:"):
                    y_pos = box_rect.top - self.venn_img.get_height()
                    self.screen.blit(self.venn_img, (1088 - self.venn_img.get_width() - 150, y_pos))
        
        self.draw_text(dialogue, box_rect.x + 10, box_rect.y + 10)

    def create_decision_buttons(self):
        if self.current_scene == "start":
            self.decision_buttons = {
                "Drikke": AnimatedButton("Drikk", self.left_x, self.button_y, self.button_width, self.button_height,
                                          lambda: self.handle_decision("drink")),
                "Ikke Drikke": AnimatedButton("Ikke Drikk", self.right_x, self.button_y, self.button_width, self.button_height,
                                               lambda: self.handle_decision("no_drink"))
            }
        elif self.current_scene == "scene_2":
            self.decision_buttons = {
                "Ikke gå": AnimatedButton("Stopp han", self.left_x, self.button_y, self.button_width, self.button_height,
                                          lambda: self.handle_decision("exit_decision_A")),
                "Gå med": AnimatedButton("Følg etter", self.right_x, self.button_y, self.button_width, self.button_height,
                                          lambda: self.handle_decision("exit_decision_B"))
            }
        elif self.current_scene == "scene_3":
            self.decision_buttons = {
                "Stoppe": AnimatedButton("Stopp han", self.left_x, self.button_y, self.button_width, self.button_height,
                                         lambda: self.handle_decision("try_stop_A")),
                "Ikke Stoppe": AnimatedButton("Gå mot bil", self.right_x, self.button_y, self.button_width, self.button_height,
                                              lambda: self.handle_decision("try_stop_B"))
            }
        elif self.current_scene == "scene_4":
            self.decision_buttons = {
                "seat_A": AnimatedButton("Stå igjen", self.left_x, self.button_y, self.button_width, self.button_height,
                                        lambda: self.handle_decision("seat_B")),  # swapped: now takes the outcome of seat_B
                "seat_B": AnimatedButton("Sitt på", self.right_x, self.button_y, self.button_width, self.button_height,
                                        lambda: self.handle_decision("seat_A"))   # swapped: now takes the outcome of seat_A
            }
        for btn in self.decision_buttons.values():
            btn.draw = new_decision_draw.__get__(btn, AnimatedButton)

# remove terminal

# make logo screen bigger

    def handle_decision(self, decision):
        if decision == "drink":
            self.current_scene = "scene_2"
        elif decision == "no_drink":
            self.current_scene = "info_drink"
        elif decision == "exit_decision_A":
            self.current_scene = "info_exit_A"
        elif decision == "exit_decision_B":
            self.current_scene = "scene_3"
        elif decision == "try_stop_A":
            self.current_scene = "info_try_stop_A"
        elif decision == "try_stop_B":
            self.current_scene = "scene_4"
        elif decision == "seat_A":
            self.current_scene = "bad_ending"       # Bad ending: the one when you sit in.
        elif decision == "seat_B":
            self.current_scene = "info_sete_B"
        self.reset_dialogue()

    def info_transition(self):
        self.current_scene = "start"
        self.reset_dialogue()

    def draw_info_logo(self):
        if self.logo_img:
            small_logo = pygame.transform.scale(self.logo_img, (400, 400))
            logo_rect = small_logo.get_rect(center=(1088 // 2, 612 // 2 - 80))
            self.screen.blit(small_logo, logo_rect)

    def draw_scene(self):
        if self.current_scene in {"ending_stop", "ending_drive", "bad_ending"}:
            chapter5_bg = self.backgrounds.get("ending_stop")
            if chapter5_bg:
                self.screen.blit(chapter5_bg, (0, 0))
                
            # Draw the final dialogue text if there's any.
            if self.dialogue_progress:
                self.draw_dialogue_box(self.dialogue_progress)
            
            # No fade effect—just display the logo if present.
            if self.logo_img:
                self.draw_info_logo()
        elif self.current_scene == "scene_2" and self.current_line_index >= 2:
            self.screen.blit(self.scene2_end_bg, (0, 0))
        else:
            bg = self.backgrounds.get(self.current_scene)
            if bg:
                self.screen.blit(bg, (0, 0))
            else:
                self.screen.fill((0, 0, 0))
        
        if self.current_scene.startswith("info_"):
            self.draw_info_logo()
        
        if self.current_scene not in {"ending_stop", "ending_drive", "bad_ending"}:
            if self.current_line_index < len(self.current_dialogue_full):
                self.draw_dialogue_box(self.dialogue_progress)
            else:
                if not self.decision_buttons:
                    self.create_decision_buttons()
                for btn in self.decision_buttons.values():
                    btn.update()
                    btn.draw(self.screen)
        
        # Update and draw the persistent Music button
        self.music_button.update()
        self.music_button.draw(self.screen)

    def run(self):
        from settings import read_music_config
        while self.running:
            dt = self.clock.tick(60)
            desired_track = os.path.join("sound", "scene1.wav") if self.current_scene == "start" else os.path.join("sound", "scene2+.wav")
            if self.current_music != desired_track:
                self.current_music = desired_track
                pygame.mixer.music.load(resource_path(self.current_music))
                pygame.mixer.music.play(-1)
            music_volume = read_music_config()
            pygame.mixer.music.set_volume(min(music_volume / 5.0, 1.0))
            if not self.music_on:
                pygame.mixer.music.pause()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.music_button.handle_event(event)
                if self.decision_buttons:
                    for btn in self.decision_buttons.values():
                        btn.handle_event(event)
                else:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.dialogue_finished:
                            self.advance_dialogue()
            self.update_dialogue(dt)
            self.draw_scene()
            pygame.display.flip()            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()  # Defaults to "start" scene.
    game.run()