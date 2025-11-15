import pygame
import cv2
import mediapipe as mp
import random
import sys
import os
import threading
import time
import math

# ------------------ Pygame Setup ------------------
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("⚡ Hogwarts: The Forbidden Run ⚡")
clock = pygame.time.Clock()

# Magical Color Palette
MIDNIGHT_BLUE = (15, 23, 42)
DEEP_PURPLE = (88, 28, 135)
MYSTIC_PURPLE = (147, 51, 234)
ENCHANTED_GOLD = (251, 191, 36)
PHOENIX_ORANGE = (249, 115, 22)
EMERALD = (16, 185, 129)
CRIMSON = (220, 38, 38)
SILVERY_WHITE = (248, 250, 252)
SHADOW_BLACK = (17, 24, 39)
CURSE_GREEN = (34, 197, 94)
SPELL_BLUE = (59, 130, 246)
MIST_GRAY = (156, 163, 175)
DARK_FOREST = (22, 101, 52)
POTION_PINK = (236, 72, 153)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Fonts
try:
    font_title = pygame.font.Font(None, 72)
    font_large = pygame.font.Font(None, 56)
    font_medium = pygame.font.Font(None, 40)
    font_small = pygame.font.Font(None, 28)
    font_tiny = pygame.font.Font(None, 20)
except:
    font_title = pygame.font.Font(None, 60)
    font_large = pygame.font.Font(None, 48)
    font_medium = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 24)
    font_tiny = pygame.font.Font(None, 18)

# Particle system for magical effects
class MagicParticle:
    def __init__(self, x, y, color, vel_x=None, vel_y=None):
        self.x = x
        self.y = y
        self.color = color
        self.vel_x = vel_x if vel_x else random.uniform(-2, 2)
        self.vel_y = vel_y if vel_y else random.uniform(-3, -1)
        self.life = 30
        self.size = random.randint(2, 5)
        
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += 0.2  # gravity
        self.life -= 1
        self.size = max(1, self.size - 0.1)
        
    def draw(self, screen):
        if self.life > 0:
            alpha = int((self.life / 30) * 255)
            s = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (int(self.size), int(self.size)), int(self.size))
            screen.blit(s, (int(self.x - self.size), int(self.y - self.size)))

# ------------------ MediaPipe Hand Setup ------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5,
    max_num_hands=1
)

# ------------------ Webcam Setup ------------------
try:
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    cap.set(cv2.CAP_PROP_FPS, 30)
    webcam_available = True
except:
    webcam_available = False
    print("🔮 Webcam not available - using wand movements (keyboard) only")

# ------------------ Thread-Safe Jump Control ------------------
jump_lock = threading.Lock()
jump_triggered = False
hand_control_enabled = True
running = True

# Particle list
particles = []

# ------------------ Load Obstacles ------------------
def load_obstacle_images():
    obstacles_imgs = []
    obstacle_folder = "obstacles"
    if os.path.exists(obstacle_folder):
        for filename in os.listdir(obstacle_folder):
            if filename.endswith('.png'):
                try:
                    img = pygame.image.load(os.path.join(obstacle_folder, filename))
                    img = pygame.transform.scale(img, (60, 60))
                    obstacles_imgs.append(img)
                except:
                    print(f"Failed to load {filename}")
    return obstacles_imgs

obstacle_images = load_obstacle_images()

# ------------------ Game Objects ------------------
class Player:
    def __init__(self):
        self.width = 50
        self.height = 70
        self.x = WIDTH // 2 - 25
        self.y = HEIGHT - 170
        self.velocity_y = 0
        self.is_jumping = False
        self.ground_y = HEIGHT - 170
        self.animation_offset = 0
        self.wand_sparkle_timer = 0
        self.trail_particles = []
        
    def draw(self, screen):
        # Animated floating effect
        self.animation_offset = math.sin(pygame.time.get_ticks() * 0.005) * 3
        draw_y = self.y + self.animation_offset
        
        # Magical aura glow
        glow_surface = pygame.Surface((self.width + 30, self.height + 30), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_surface, (*MYSTIC_PURPLE, 40), glow_surface.get_rect())
        screen.blit(glow_surface, (self.x - 15, draw_y - 15))
        
        # Cape/Cloak (flowing effect)
        cape_points = [
            (self.x + 25, draw_y + 40),
            (self.x + 10, draw_y + 50),
            (self.x + 5, draw_y + 65),
            (self.x + 45, draw_y + 65),
            (self.x + 40, draw_y + 50)
        ]
        pygame.draw.polygon(screen, SHADOW_BLACK, cape_points)
        pygame.draw.polygon(screen, DEEP_PURPLE, cape_points, 2)
        
        # Body (wizard robes)
        pygame.draw.ellipse(screen, MIDNIGHT_BLUE, (self.x + 8, draw_y + 38, 34, 32))
        pygame.draw.rect(screen, ENCHANTED_GOLD, (self.x + 20, draw_y + 40, 10, 3))  # Golden clasp
        
        # Head
        pygame.draw.circle(screen, (255, 220, 177), (int(self.x + 25), int(draw_y + 25)), 12)
        
        # Wizard Hat (more detailed)
        hat_points = [
            (self.x + 25, draw_y - 8),
            (self.x + 12, draw_y + 18),
            (self.x + 38, draw_y + 18)
        ]
        pygame.draw.polygon(screen, DEEP_PURPLE, hat_points)
        pygame.draw.ellipse(screen, DEEP_PURPLE, (self.x + 8, draw_y + 15, 34, 8))
        pygame.draw.line(screen, ENCHANTED_GOLD, (self.x + 10, draw_y + 17), (self.x + 40, draw_y + 17), 2)
        # Moon and stars on hat
        pygame.draw.circle(screen, ENCHANTED_GOLD, (int(self.x + 20), int(draw_y + 5)), 3)
        pygame.draw.circle(screen, SILVERY_WHITE, (int(self.x + 28), int(draw_y + 3)), 1)
        
        # Harry's iconic glasses
        pygame.draw.circle(screen, SHADOW_BLACK, (int(self.x + 20), int(draw_y + 24)), 4, 2)
        pygame.draw.circle(screen, SHADOW_BLACK, (int(self.x + 30), int(draw_y + 24)), 4, 2)
        pygame.draw.line(screen, SHADOW_BLACK, (self.x + 24, draw_y + 24), (self.x + 26, draw_y + 24), 2)
        
        # Lightning scar (glowing)
        scar_glow = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.line(scar_glow, (*CRIMSON, 180), (3, 2), (5, 5), 3)
        pygame.draw.line(scar_glow, (*CRIMSON, 180), (5, 5), (7, 4), 3)
        screen.blit(scar_glow, (self.x + 22, draw_y + 16))
        
        # Eyes with slight glow
        pygame.draw.circle(screen, SPELL_BLUE, (int(self.x + 20), int(draw_y + 24)), 2)
        pygame.draw.circle(screen, SPELL_BLUE, (int(self.x + 30), int(draw_y + 24)), 2)
        
        # Wand with magical effect
        wand_end_x = self.x + 52
        wand_end_y = draw_y + 42
        pygame.draw.line(screen, (101, 67, 33), (self.x + 42, draw_y + 45), (wand_end_x, wand_end_y), 3)
        
        # Wand sparkles
        self.wand_sparkle_timer += 1
        if self.wand_sparkle_timer % 5 == 0:
            particles.append(MagicParticle(wand_end_x, wand_end_y, ENCHANTED_GOLD, 
                                          random.uniform(-1, 1), random.uniform(-2, 0)))
        
        # Spell circle (rotating)
        angle = pygame.time.get_ticks() * 0.003
        for i in range(6):
            angle_offset = (math.pi * 2 / 6) * i + angle
            px = wand_end_x + math.cos(angle_offset) * 8
            py = wand_end_y + math.sin(angle_offset) * 8
            pygame.draw.circle(screen, ENCHANTED_GOLD, (int(px), int(py)), 2)
    
    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.velocity_y = -20
            # Spawn jump particles
            for _ in range(15):
                particles.append(MagicParticle(self.x + 25, self.y + 60, MYSTIC_PURPLE))
    
    def update(self):
        if self.is_jumping:
            self.velocity_y += 1.0
            self.y += self.velocity_y
            # Trail particles while jumping
            if random.random() > 0.7:
                particles.append(MagicParticle(self.x + 25, self.y + 35, SPELL_BLUE, 0, 1))
            if self.y >= self.ground_y:
                self.y = self.ground_y
                self.is_jumping = False
                self.velocity_y = 0
                # Landing particles
                for _ in range(10):
                    particles.append(MagicParticle(self.x + 25, self.y + 60, EMERALD))
        self.x = max(50, min(self.x, WIDTH - 100))

class Obstacle:
    def __init__(self, x, speed, has_image=False, image=None):
        self.width = 60
        self.height = 60
        self.x = x
        self.y = HEIGHT - 170
        self.speed = speed
        self.has_image = has_image
        self.image = image
        self.float_offset = random.uniform(0, math.pi * 2)
        self.rotation = 0
        
    def draw(self, screen):
        # Floating animation
        float_y = self.y + math.sin(pygame.time.get_ticks() * 0.003 + self.float_offset) * 5
        
        if self.has_image and self.image:
            # Rotate image slightly for effect
            rotated = pygame.transform.rotate(self.image, self.rotation)
            rect = rotated.get_rect(center=(self.x + self.width//2, float_y + self.height//2))
            screen.blit(rotated, rect)
        else:
            # Dark curse orb with pulsing effect
            pulse = math.sin(pygame.time.get_ticks() * 0.008) * 5 + 25
            
            # Outer glow
            glow_surface = pygame.Surface((self.width + 40, self.height + 40), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*DEEP_PURPLE, 60), 
                             (self.width//2 + 20, self.height//2 + 20), int(pulse + 10))
            screen.blit(glow_surface, (self.x - 20, float_y - 20))
            
            # Main orb
            pygame.draw.circle(screen, DEEP_PURPLE, (int(self.x + 30), int(float_y + 30)), int(pulse))
            pygame.draw.circle(screen, MYSTIC_PURPLE, (int(self.x + 30), int(float_y + 30)), int(pulse - 5))
            
            # Dark center with skull
            pygame.draw.circle(screen, SHADOW_BLACK, (int(self.x + 30), int(float_y + 30)), int(pulse - 15))
            
            # Skull eyes (menacing)
            eye_y = float_y + 25
            pygame.draw.ellipse(screen, CURSE_GREEN, (self.x + 22, eye_y, 6, 8))
            pygame.draw.ellipse(screen, CURSE_GREEN, (self.x + 32, eye_y, 6, 8))
            
            # Magical runes circling
            angle = pygame.time.get_ticks() * 0.005
            for i in range(4):
                a = angle + (math.pi * 2 / 4) * i
                rx = self.x + 30 + math.cos(a) * (pulse + 8)
                ry = float_y + 30 + math.sin(a) * (pulse + 8)
                pygame.draw.circle(screen, CRIMSON, (int(rx), int(ry)), 2)
        
        # Particle trail
        if random.random() > 0.8:
            particles.append(MagicParticle(self.x + 30, float_y + 30, DEEP_PURPLE, -2, 0))
        
        self.rotation += 1
    
    def update(self):
        self.x -= self.speed
    
    def off_screen(self):
        return self.x < -self.width

class Letter:
    def __init__(self, x, char, speed):
        self.width = 35
        self.height = 35
        self.x = x
        self.y = HEIGHT - 220 - random.randint(0, 100)
        self.char = char
        self.speed = speed
        self.collected = False
        self.float_offset = random.uniform(0, math.pi * 2)
        self.rotation = 0
        
    def draw(self, screen):
        if not self.collected:
            # Floating animation
            float_y = self.y + math.sin(pygame.time.get_ticks() * 0.004 + self.float_offset) * 8
            
            # Golden Snitch body with shimmer
            shimmer = math.sin(pygame.time.get_ticks() * 0.01) * 10 + 245
            gold_color = (int(shimmer), int(shimmer * 0.75), 20)
            
            # Glow effect
            glow_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*ENCHANTED_GOLD, 80), (25, 25), 25)
            screen.blit(glow_surface, (self.x - 7, float_y - 7))
            
            # Main golden sphere
            pygame.draw.circle(screen, gold_color, (int(self.x + 17), int(float_y + 17)), 18)
            pygame.draw.circle(screen, ENCHANTED_GOLD, (int(self.x + 17), int(float_y + 17)), 16)
            
            # Animated wings
            wing_angle = math.sin(pygame.time.get_ticks() * 0.01) * 0.3
            
            # Left wing
            left_wing = [
                (self.x + 5, float_y + 15),
                (self.x - 8, float_y + 8 + math.sin(wing_angle) * 5),
                (self.x - 5, float_y + 20),
                (self.x + 5, float_y + 22)
            ]
            pygame.draw.polygon(screen, SILVERY_WHITE, left_wing)
            pygame.draw.polygon(screen, MIST_GRAY, left_wing, 1)
            
            # Right wing
            right_wing = [
                (self.x + 29, float_y + 15),
                (self.x + 42, float_y + 8 + math.sin(wing_angle) * 5),
                (self.x + 39, float_y + 20),
                (self.x + 29, float_y + 22)
            ]
            pygame.draw.polygon(screen, SILVERY_WHITE, right_wing)
            pygame.draw.polygon(screen, MIST_GRAY, right_wing, 1)
            
            # Letter on snitch
            text = font_medium.render(self.char, True, MIDNIGHT_BLUE)
            text_rect = text.get_rect(center=(self.x + 17, float_y + 17))
            screen.blit(text, text_rect)
            
            # Sparkle particles
            if random.random() > 0.85:
                particles.append(MagicParticle(self.x + 17, float_y + 17, ENCHANTED_GOLD, 
                                              random.uniform(-1, 1), random.uniform(-1, 1)))
    
    def update(self):
        self.x -= self.speed
    
    def off_screen(self):
        return self.x < -self.width

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        
        # Glowing effect when hovered
        if self.is_hovered:
            glow_surface = pygame.Surface((self.rect.width + 20, self.rect.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*self.hover_color, 60), glow_surface.get_rect(), border_radius=15)
            screen.blit(glow_surface, (self.rect.x - 10, self.rect.y - 10))
        
        # Button background with gradient effect
        pygame.draw.rect(screen, color, self.rect, border_radius=12)
        pygame.draw.rect(screen, ENCHANTED_GOLD, self.rect, 3, border_radius=12)
        
        # Text with shadow
        text_shadow = font_small.render(self.text, True, SHADOW_BLACK)
        text_surf = font_small.render(self.text, True, SILVERY_WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_shadow, (text_rect.x + 2, text_rect.y + 2))
        screen.blit(text_surf, text_rect)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# ------------------ Levels ------------------
LEVELS = [
    {"name": "First Year", "phrase": "LUMOS", "description": "* Light in the Darkness", "speed": 5, "spawn_rate_obstacle": 100, "spawn_rate_letter": 110},
    {"name": "Second Year", "phrase": "EXPELLIARMUS", "description": "* The Disarming Charm", "speed": 6.5, "spawn_rate_obstacle": 80, "spawn_rate_letter": 95},
    {"name": "Third Year", "phrase": "EXPECTOPATRONUM", "description": "* Summon Your Guardian", "speed": 8, "spawn_rate_obstacle": 65, "spawn_rate_letter": 85}
]

# ------------------ Hand Detection Logic ------------------
def is_open_hand(hand_landmarks):
    tips = [8, 12, 16, 20]
    mcp  = [5, 9, 13, 17]
    open_count = 0
    for tip_idx, mcp_idx in zip(tips, mcp):
        if hand_landmarks[tip_idx].y < hand_landmarks[mcp_idx].y:
            open_count += 1
    return open_count >= 3

def hand_detection_thread():
    global jump_triggered, running
    last_state = False
    debounce_time = 0.3
    last_jump_time = 0
    while running and webcam_available:
        if hand_control_enabled:
            ret, frame = cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                small_frame = cv2.resize(frame, (160, 120))
                rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                rgb_frame.flags.writeable = False
                results = hands.process(rgb_frame)
                detected = False
                if results.multi_hand_landmarks:
                    hand_landmarks = results.multi_hand_landmarks[0]
                    if is_open_hand(hand_landmarks.landmark):
                        detected = True

                current_time = time.time()
                if detected and not last_state and (current_time - last_jump_time) > debounce_time:
                    with jump_lock:
                        jump_triggered = True
                    last_jump_time = current_time

                last_state = detected
        time.sleep(0.02)

if webcam_available:
    threading.Thread(target=hand_detection_thread, daemon=True).start()

# ------------------ Game Class ------------------
class Game:
    def __init__(self):
        self.state = "welcome"
        self.player = Player()
        self.obstacles = []
        self.letters = []
        self.current_level = 0
        self.target_phrase = LEVELS[0]["phrase"]
        self.collected_letters = ""
        self.score = 0
        self.spawn_timer = 0
        self.letter_index = 0
        self.control_mode = "hand"
        self.stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT - 200)) for _ in range(100)]
        
        self.story_button = Button(WIDTH//2 - 120, 480, 240, 55, "THE PROPHECY", DEEP_PURPLE, MYSTIC_PURPLE)
        self.home_button = Button(WIDTH - 180, 15, 165, 45, "GREAT HALL", DEEP_PURPLE, MYSTIC_PURPLE)
        
    def draw_magical_background(self, screen):
        # Animated starry night
        screen.fill(MIDNIGHT_BLUE)
        
        # Twinkling stars
        time_offset = pygame.time.get_ticks() * 0.001
        for i, (sx, sy) in enumerate(self.stars):
            brightness = (math.sin(time_offset + i * 0.5) + 1) * 0.5
            star_color = tuple(int(c * brightness) for c in SILVERY_WHITE)
            size = 1 if brightness < 0.5 else 2
            pygame.draw.circle(screen, star_color, (sx, sy), size)
        
        # Shooting stars occasionally
        if random.random() > 0.98:
            sx = random.randint(WIDTH//2, WIDTH)
            sy = random.randint(50, 200)
            for i in range(5):
                pygame.draw.circle(screen, SILVERY_WHITE, (sx - i * 10, sy + i * 5), 2 - i//2)
        
        # Mysterious fog at bottom
        fog_surface = pygame.Surface((WIDTH, 150), pygame.SRCALPHA)
        for y in range(150):
            alpha = int((y / 150) * 100)
            pygame.draw.line(fog_surface, (*DEEP_PURPLE, alpha), (0, y), (WIDTH, y))
        screen.blit(fog_surface, (0, HEIGHT - 150))
        
        # Castle ground
        pygame.draw.rect(screen, DARK_FOREST, (0, HEIGHT - 120, WIDTH, 120))
        
        # Grass texture
        for i in range(0, WIDTH, 20):
            grass_height = random.randint(3, 8)
            pygame.draw.line(screen, EMERALD, (i, HEIGHT - 120), (i, HEIGHT - 120 + grass_height), 2)
        
    def reset(self):
        self.state = "playing"
        self.player = Player()
        self.obstacles = []
        self.letters = []
        self.collected_letters = ""
        self.score = 0
        self.spawn_timer = 0
        self.letter_index = 0
        
    def next_level(self):
        self.current_level += 1
        if self.current_level >= len(LEVELS):
            self.state = "all_complete"
        else:
            self.state = "level_complete"
    
    def go_to_welcome(self):
        self.state = "welcome"
        self.current_level = 0
        self.target_phrase = LEVELS[0]["phrase"]
        self.player = Player()
        self.obstacles = []
        self.letters = []
        self.collected_letters = ""
        self.score = 0
        self.spawn_timer = 0
        self.letter_index = 0
        
    def spawn_obstacle(self):
        level_data = LEVELS[self.current_level]
        speed = level_data["speed"]
        
        if len(obstacle_images) > 0:
            img = random.choice(obstacle_images)
            img_rect = img.get_rect()
            scale_ratio = min(60 / img_rect.width, 60 / img_rect.height)
            img_scaled = pygame.transform.smoothscale(
                img, (int(img_rect.width * scale_ratio), int(img_rect.height * scale_ratio))
            )
            self.obstacles.append(Obstacle(WIDTH, speed, True, img_scaled))
        else:
            self.obstacles.append(Obstacle(WIDTH, speed, False, None))
        
    def spawn_letter(self):
        level_data = LEVELS[self.current_level]
        speed = level_data["speed"]
        
        for i, char in enumerate(self.target_phrase):
            if i >= len(self.collected_letters) or self.collected_letters[i] != char:
                self.letters.append(Letter(WIDTH, char, speed))
                break
    
    def check_collision(self, obj1_x, obj1_y, obj1_w, obj1_h, obj2_x, obj2_y, obj2_w, obj2_h):
        return (obj1_x < obj2_x + obj2_w and
                obj1_x + obj1_w > obj2_x and
                obj1_y < obj2_y + obj2_h and
                obj1_y + obj1_h > obj2_y)
    
    def update(self):
        if self.state != "playing":
            return
        
        self.player.update()
        level_data = LEVELS[self.current_level]
        
        self.spawn_timer += 1
        if self.spawn_timer % level_data["spawn_rate_obstacle"] == 0:
            self.spawn_obstacle()
        if self.spawn_timer % level_data["spawn_rate_letter"] == 0:
            self.spawn_letter()
        
        for obstacle in self.obstacles[:]:
            obstacle.update()
            if obstacle.off_screen():
                self.obstacles.remove(obstacle)
                self.score += 15
            elif self.check_collision(
                self.player.x, self.player.y, self.player.width, self.player.height,
                obstacle.x, obstacle.y, obstacle.width, obstacle.height
            ):
                self.state = "lost"
                # Explosion particles
                for _ in range(30):
                    particles.append(MagicParticle(self.player.x + 25, self.player.y + 35, CRIMSON))
        
        for letter in self.letters[:]:
            letter.update()
            if letter.off_screen():
                self.letters.remove(letter)
            elif not letter.collected and self.check_collision(
                self.player.x, self.player.y, self.player.width, self.player.height,
                letter.x, letter.y, letter.width, letter.height
            ):
                next_letter_index = len(self.collected_letters)
                if next_letter_index < len(self.target_phrase):
                    expected_letter = self.target_phrase[next_letter_index]
                    if letter.char == expected_letter:
                        letter.collected = True
                        self.collected_letters += letter.char
                        self.score += 75
                        self.letters.remove(letter)
                        # Collection particles
                        for _ in range(20):
                            particles.append(MagicParticle(letter.x, letter.y, ENCHANTED_GOLD))
                        
                        if self.collected_letters == self.target_phrase:
                            self.next_level()
    
    def draw(self, screen):
        self.draw_magical_background(screen)
        
        # Update and draw particles
        for particle in particles[:]:
            particle.update()
            particle.draw(screen)
            if particle.life <= 0:
                particles.remove(particle)
        
        if self.state == "welcome":
            # Animated title with glow
            title_y = 60 + math.sin(pygame.time.get_ticks() * 0.002) * 5
            
            # Title glow
            glow_surf = pygame.Surface((WIDTH, 100), pygame.SRCALPHA)
            title_glow = font_title.render("HOGWARTS", True, (*ENCHANTED_GOLD, 100))
            glow_rect = title_glow.get_rect(center=(WIDTH//2, title_y))
            for offset in [(2, 2), (-2, 2), (2, -2), (-2, -2)]:
                screen.blit(title_glow, (glow_rect.x + offset[0], glow_rect.y + offset[1]))
            
            title = font_title.render("HOGWARTS", True, ENCHANTED_GOLD)
            title_rect = title.get_rect(center=(WIDTH//2, title_y))
            screen.blit(title, title_rect)
            
            # Lightning bolts
            pygame.draw.line(screen, ENCHANTED_GOLD, (title_rect.left - 40, title_y), (title_rect.left - 50, title_y - 10), 3)
            pygame.draw.line(screen, ENCHANTED_GOLD, (title_rect.left - 50, title_y - 10), (title_rect.left - 45, title_y - 5), 3)
            pygame.draw.line(screen, ENCHANTED_GOLD, (title_rect.right + 40, title_y), (title_rect.right + 50, title_y - 10), 3)
            pygame.draw.line(screen, ENCHANTED_GOLD, (title_rect.right + 50, title_y - 10), (title_rect.right + 45, title_y - 5), 3)
            
            subtitle = font_large.render("The Forbidden Run", True, MYSTIC_PURPLE)
            subtitle_rect = subtitle.get_rect(center=(WIDTH//2, title_y + 60))
            screen.blit(subtitle, subtitle_rect)
            
            # Decorative line
            pygame.draw.line(screen, ENCHANTED_GOLD, (WIDTH//2 - 150, title_y + 95), (WIDTH//2 + 150, title_y + 95), 2)
            
            # Instructions with icons
            y_offset = 220
            if self.control_mode == "keyboard":
                inst_title = font_medium.render("WAND CONTROLS", True, PHOENIX_ORANGE)
                instruction1 = font_small.render("ARROW UP or SPACE - Cast Wingardium Leviosa", True, SILVERY_WHITE)
                instruction2 = font_small.render("Press H to switch to Hand Magic", True, MIST_GRAY)
            else:
                inst_title = font_medium.render("HAND MAGIC", True, PHOENIX_ORANGE)
                instruction1 = font_small.render("Open your hand (4+ fingers) - Levitate!", True, SILVERY_WHITE)
                instruction2 = font_small.render("Press K to switch to Keyboard", True, MIST_GRAY)
            
            inst_rect = inst_title.get_rect(center=(WIDTH//2, y_offset))
            screen.blit(inst_title, inst_rect)
            inst1_rect = instruction1.get_rect(center=(WIDTH//2, y_offset + 45))
            screen.blit(instruction1, inst1_rect)
            inst2_rect = instruction2.get_rect(center=(WIDTH//2, y_offset + 80))
            screen.blit(instruction2, inst2_rect)
            
            # Pulsing start text
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 0.3 + 0.7
            start_color = tuple(int(c * pulse) for c in EMERALD)
            start_text = font_large.render("Press SPACE to Begin", True, start_color)
            start_rect = start_text.get_rect(center=(WIDTH//2, 390))
            screen.blit(start_text, start_rect)
            
            self.story_button.draw(screen)
            
            # Floating magical symbols using shapes
            symbols_y = 550
            # Star
            star_x = WIDTH//2 - 200
            for i in range(5):
                angle = math.pi * 2 * i / 5 - math.pi / 2 + pygame.time.get_ticks() * 0.002
                x = star_x + math.cos(angle) * 8
                y = symbols_y + math.sin(angle) * 8 + math.sin(pygame.time.get_ticks() * 0.002) * 10
                pygame.draw.circle(screen, ENCHANTED_GOLD, (int(x), int(y)), 3)
            
            # Crystal ball
            ball_x = WIDTH//2 - 100
            ball_y = symbols_y + math.sin(pygame.time.get_ticks() * 0.002 + 1) * 10
            pygame.draw.circle(screen, MYSTIC_PURPLE, (ball_x, int(ball_y)), 10)
            pygame.draw.circle(screen, SILVERY_WHITE, (ball_x - 3, int(ball_y) - 3), 3)
            
            # Scroll
            scroll_x = WIDTH//2
            scroll_y = symbols_y + math.sin(pygame.time.get_ticks() * 0.002 + 2) * 10
            pygame.draw.rect(screen, (210, 180, 140), (scroll_x - 8, int(scroll_y) - 10, 16, 20), border_radius=2)
            pygame.draw.line(screen, SHADOW_BLACK, (scroll_x - 5, int(scroll_y) - 5), (scroll_x + 5, int(scroll_y) - 5), 1)
            pygame.draw.line(screen, SHADOW_BLACK, (scroll_x - 5, int(scroll_y)), (scroll_x + 5, int(scroll_y)), 1)
            pygame.draw.line(screen, SHADOW_BLACK, (scroll_x - 5, int(scroll_y) + 5), (scroll_x + 5, int(scroll_y) + 5), 1)
            
            # Owl
            owl_x = WIDTH//2 + 100
            owl_y = symbols_y + math.sin(pygame.time.get_ticks() * 0.002 + 3) * 10
            pygame.draw.circle(screen, (139, 69, 19), (owl_x, int(owl_y)), 10)
            pygame.draw.circle(screen, SILVERY_WHITE, (owl_x - 4, int(owl_y) - 2), 3)
            pygame.draw.circle(screen, SILVERY_WHITE, (owl_x + 4, int(owl_y) - 2), 3)
            pygame.draw.circle(screen, BLACK, (owl_x - 4, int(owl_y) - 2), 2)
            pygame.draw.circle(screen, BLACK, (owl_x + 4, int(owl_y) - 2), 2)
            
            # Wand
            wand_x = WIDTH//2 + 200
            wand_y = symbols_y + math.sin(pygame.time.get_ticks() * 0.002 + 4) * 10
            pygame.draw.line(screen, (101, 67, 33), (wand_x - 10, int(wand_y) - 10), (wand_x + 10, int(wand_y) + 10), 4)
            pygame.draw.circle(screen, ENCHANTED_GOLD, (wand_x + 10, int(wand_y) + 10), 3)
            
        elif self.state == "story":
            title = font_title.render("THE PROPHECY", True, ENCHANTED_GOLD)
            title_rect = title.get_rect(center=(WIDTH//2, 50))
            screen.blit(title, title_rect)
            
            # Decorative scrolls
            pygame.draw.rect(screen, (210, 180, 140), (WIDTH//2 - 200, 40, 30, 30), border_radius=5)
            pygame.draw.rect(screen, (210, 180, 140), (WIDTH//2 + 170, 40, 30, 30), border_radius=5)
            
            pygame.draw.line(screen, ENCHANTED_GOLD, (WIDTH//2 - 180, 90), (WIDTH//2 + 180, 90), 2)
            
            story_lines = [
                "In the depths of the Forbidden Forest,",
                "dark curses have been unleashed...",
                "",
                "As a young wizard at Hogwarts,",
                "you must master powerful spells",
                "to survive the enchanted trials.",
                "",
                "Collect magical letters to complete",
                "ancient incantations while dodging",
                "the cursed obstacles in your path.",
                "",
                "Only the bravest can master",
                "the art of spell-casting!",
                "",
                "Will you rise to the challenge?"
            ]
            
            y_pos = 140
            for i, line in enumerate(story_lines):
                alpha = min(255, (pygame.time.get_ticks() - i * 100) // 3)
                color = (*SILVERY_WHITE[:3], min(alpha, 255))
                text = font_small.render(line, True, SILVERY_WHITE if alpha >= 255 else MIST_GRAY)
                text_rect = text.get_rect(center=(WIDTH//2, y_pos))
                screen.blit(text, text_rect)
                y_pos += 30
            
            back_text = font_small.render("Press SPACE to return", True, ENCHANTED_GOLD)
            back_rect = back_text.get_rect(center=(WIDTH//2, 540))
            screen.blit(back_text, back_rect)
            
        elif self.state == "playing":
            self.player.draw(screen)
            
            for obstacle in self.obstacles:
                obstacle.draw(screen)
            
            for letter in self.letters:
                letter.draw(screen)
            
            # Modern HUD with glass effect
            hud_surface = pygame.Surface((300, 200), pygame.SRCALPHA)
            pygame.draw.rect(hud_surface, (*MIDNIGHT_BLUE, 180), hud_surface.get_rect(), border_radius=15)
            pygame.draw.rect(hud_surface, (*ENCHANTED_GOLD, 100), hud_surface.get_rect(), 2, border_radius=15)
            screen.blit(hud_surface, (10, 10))
            
            level_info = LEVELS[self.current_level]
            level_text = font_medium.render(f"{level_info['name']}", True, ENCHANTED_GOLD)
            screen.blit(level_text, (20, 20))
            
            desc_text = font_small.render(f"{level_info['description']}", True, MYSTIC_PURPLE)
            screen.blit(desc_text, (20, 55))
            
            score_text = font_small.render(f"House Points: {self.score}", True, SILVERY_WHITE)
            screen.blit(score_text, (20, 90))
            
            # Spell progress bar
            progress_bg = pygame.Surface((260, 30), pygame.SRCALPHA)
            pygame.draw.rect(progress_bg, (*SHADOW_BLACK, 150), progress_bg.get_rect(), border_radius=8)
            screen.blit(progress_bg, (20, 125))
            
            progress = len(self.collected_letters) / len(self.target_phrase)
            if progress > 0:
                progress_width = int(260 * progress)
                pygame.draw.rect(screen, EMERALD, (20, 125, progress_width, 30), border_radius=8)
            
            collected_text = font_small.render(f"Spell: {self.collected_letters}", True, ENCHANTED_GOLD)
            screen.blit(collected_text, (25, 130))
            
            target_text = font_tiny.render(f"Target: {self.target_phrase}", True, MIST_GRAY)
            screen.blit(target_text, (20, 165))
            
            # Mode indicator
            mode_bg = pygame.Surface((180, 30), pygame.SRCALPHA)
            pygame.draw.rect(mode_bg, (*DEEP_PURPLE, 180), mode_bg.get_rect(), border_radius=8)
            screen.blit(mode_bg, (WIDTH - 190, HEIGHT - 40))
            
            mode_icon = "HAND" if self.control_mode == "hand" else "KEYS"
            mode_text = font_tiny.render(f"{mode_icon}: {self.control_mode.upper()}", True, SILVERY_WHITE)
            screen.blit(mode_text, (WIDTH - 180, HEIGHT - 35))
            
            self.home_button.draw(screen)
            
        elif self.state == "level_complete":
            # Victory animation
            victory_y = 120 + math.sin(pygame.time.get_ticks() * 0.003) * 10
            
            congrats = font_title.render("SPELL MASTERED!", True, ENCHANTED_GOLD)
            congrats_rect = congrats.get_rect(center=(WIDTH//2, victory_y))
            
            # Glow effect
            for offset in [(3, 3), (-3, 3), (3, -3), (-3, -3)]:
                glow = font_title.render("SPELL MASTERED!", True, (*ENCHANTED_GOLD, 80))
                screen.blit(glow, (congrats_rect.x + offset[0], congrats_rect.y + offset[1]))
            
            screen.blit(congrats, congrats_rect)
            
            # Lightning bolts
            pygame.draw.line(screen, ENCHANTED_GOLD, (congrats_rect.left - 40, victory_y), (congrats_rect.left - 50, victory_y - 15), 4)
            pygame.draw.line(screen, ENCHANTED_GOLD, (congrats_rect.right + 40, victory_y), (congrats_rect.right + 50, victory_y - 15), 4)
            
            level_info = LEVELS[self.current_level - 1]
            phrase_text = font_large.render(f"{level_info['description']}", True, MYSTIC_PURPLE)
            phrase_rect = phrase_text.get_rect(center=(WIDTH//2, victory_y + 80))
            screen.blit(phrase_text, phrase_rect)
            
            spell_display = font_medium.render(f'"{level_info["phrase"]}"', True, EMERALD)
            spell_rect = spell_display.get_rect(center=(WIDTH//2, victory_y + 130))
            screen.blit(spell_display, spell_rect)
            
            score_text = font_large.render(f"* {self.score} House Points", True, SILVERY_WHITE)
            score_rect = score_text.get_rect(center=(WIDTH//2, victory_y + 190))
            screen.blit(score_text, score_rect)
            
            next_text = font_medium.render("Press SPACE for Next Challenge", True, ENCHANTED_GOLD)
            next_rect = next_text.get_rect(center=(WIDTH//2, victory_y + 270))
            screen.blit(next_text, next_rect)
            
            # Victory particles
            if random.random() > 0.7:
                particles.append(MagicParticle(random.randint(100, WIDTH-100), 
                                              random.randint(50, 400), 
                                              random.choice([ENCHANTED_GOLD, EMERALD, MYSTIC_PURPLE])))
            
        elif self.state == "all_complete":
            # Grand finale
            finale_y = 80 + math.sin(pygame.time.get_ticks() * 0.002) * 8
            
            win_text = font_title.render("GRAND WIZARD", True, ENCHANTED_GOLD)
            win_rect = win_text.get_rect(center=(WIDTH//2, finale_y))
            
            # Epic glow
            for i in range(3):
                offset = (i + 1) * 4
                glow = font_title.render("GRAND WIZARD", True, (*ENCHANTED_GOLD, 40))
                screen.blit(glow, (win_rect.x + offset, win_rect.y + offset))
            
            screen.blit(win_text, win_rect)
            
            # Trophy symbol
            trophy_x = WIDTH // 2
            trophy_y = finale_y - 30
            pygame.draw.rect(screen, ENCHANTED_GOLD, (trophy_x - 20, trophy_y, 40, 25), border_radius=5)
            pygame.draw.rect(screen, ENCHANTED_GOLD, (trophy_x - 5, trophy_y + 25, 10, 10))
            pygame.draw.ellipse(screen, ENCHANTED_GOLD, (trophy_x - 25, trophy_y + 35, 50, 10))
            
            congrats = font_large.render("You've Mastered All Spells!", True, MYSTIC_PURPLE)
            congrats_rect = congrats.get_rect(center=(WIDTH//2, finale_y + 80))
            screen.blit(congrats, congrats_rect)
            
            motto = font_medium.render("The wizarding world salutes you!", True, EMERALD)
            motto_rect = motto.get_rect(center=(WIDTH//2, finale_y + 130))
            screen.blit(motto, motto_rect)
            
            score_text = font_large.render(f"* Total: {self.score} House Points", True, ENCHANTED_GOLD)
            score_rect = score_text.get_rect(center=(WIDTH//2, finale_y + 200))
            screen.blit(score_text, score_rect)
            
            # Achievements
            achievements = [
                "* Lumos Master",
                "* Dueling Champion", 
                "* Patronus Summoner"
            ]
            y = finale_y + 260
            for achievement in achievements:
                ach_text = font_small.render(achievement, True, SILVERY_WHITE)
                ach_rect = ach_text.get_rect(center=(WIDTH//2, y))
                screen.blit(ach_text, ach_rect)
                y += 35
            
            replay_text = font_medium.render("Press SPACE to Train Again", True, PHOENIX_ORANGE)
            replay_rect = replay_text.get_rect(center=(WIDTH//2, finale_y + 410))
            screen.blit(replay_text, replay_rect)
            
            # Celebration particles
            if random.random() > 0.5:
                particles.append(MagicParticle(random.randint(0, WIDTH), 
                                              random.randint(0, 300),
                                              random.choice([ENCHANTED_GOLD, EMERALD, MYSTIC_PURPLE, PHOENIX_ORANGE])))
            
        elif self.state == "lost":
            defeat_y = 120 + math.sin(pygame.time.get_ticks() * 0.004) * 5
            
            lost_text = font_title.render("CURSE HIT!", True, CRIMSON)
            lost_rect = lost_text.get_rect(center=(WIDTH//2, defeat_y))
            
            # Dark glow
            for offset in [(3, 3), (-3, 3), (3, -3), (-3, -3)]:
                glow = font_title.render("CURSE HIT!", True, (*DEEP_PURPLE, 100))
                screen.blit(glow, (lost_rect.x + offset[0], lost_rect.y + offset[1]))
            
            screen.blit(lost_text, lost_rect)
            
            # Skull symbol
            skull_x = WIDTH // 2
            skull_y = defeat_y - 30
            pygame.draw.circle(screen, CRIMSON, (skull_x, skull_y), 15)
            pygame.draw.ellipse(screen, SHADOW_BLACK, (skull_x - 6, skull_y - 3, 5, 7))
            pygame.draw.ellipse(screen, SHADOW_BLACK, (skull_x + 1, skull_y - 3, 5, 7))
            
            encourage = font_large.render("Even great wizards fail sometimes...", True, SILVERY_WHITE)
            encourage_rect = encourage.get_rect(center=(WIDTH//2, defeat_y + 80))
            screen.blit(encourage, encourage_rect)
            
            tip = font_medium.render("Tip: Perfect your timing!", True, PHOENIX_ORANGE)
            tip_rect = tip.get_rect(center=(WIDTH//2, defeat_y + 140))
            screen.blit(tip, tip_rect)
            
            score_text = font_large.render(f"* House Points: {self.score}", True, ENCHANTED_GOLD)
            score_rect = score_text.get_rect(center=(WIDTH//2, defeat_y + 210))
            screen.blit(score_text, score_rect)
            
            replay_text = font_medium.render("Press SPACE to Try Again", True, EMERALD)
            replay_rect = replay_text.get_rect(center=(WIDTH//2, defeat_y + 290))
            screen.blit(replay_text, replay_rect)

    def start_level(self, level_idx):
        self.current_level = level_idx
        self.state = "playing"
        self.player = Player()
        self.obstacles = []
        self.letters = []
        self.collected_letters = ""
        self.score = 0
        self.spawn_timer = 0
        self.letter_index = 0
        self.target_phrase = LEVELS[level_idx]["phrase"]

# ------------------ Main Game Loop ------------------
game = Game()
while running:
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game.state == "welcome":
                if game.story_button.is_clicked(mouse_pos):
                    game.state = "story"
            if game.state == "playing":
                if game.home_button.is_clicked(mouse_pos):
                    game.go_to_welcome()
                
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game.state == "welcome":
                    game.start_level(game.current_level)
                    game.target_phrase = LEVELS[game.current_level]["phrase"]
                elif game.state == "story":
                    game.state = "welcome"
                elif game.state == "level_complete":
                    game.start_level(game.current_level)
                    game.target_phrase = LEVELS[game.current_level]["phrase"]
                elif game.state in ["all_complete", "lost"]:
                    game.current_level = 0
                    game.start_level(game.current_level)
                    game.target_phrase = LEVELS[game.current_level]["phrase"]
                elif game.state == "playing" and game.control_mode == "keyboard":
                    game.player.jump()
                    
            if event.key == pygame.K_UP and game.state == "playing" and game.control_mode == "keyboard":
                game.player.jump()
            if event.key == pygame.K_ESCAPE:
                if game.state == "playing":
                    game.go_to_welcome()
                else:
                    running = False
            if event.key == pygame.K_h:
                game.control_mode = "hand"
                hand_control_enabled = True
            if event.key == pygame.K_k:
                game.control_mode = "keyboard"
                hand_control_enabled = False
    
    if game.state == "welcome":
        game.story_button.check_hover(mouse_pos)
    elif game.state == "playing":
        game.home_button.check_hover(mouse_pos)

    if game.control_mode == "hand":
        with jump_lock:
            if jump_triggered:
                game.player.jump()
                jump_triggered = False
    
    game.update()
    game.draw(screen)
    pygame.display.flip()
    clock.tick(60)

if webcam_available:
    cap.release()
    hands.close()
pygame.quit()