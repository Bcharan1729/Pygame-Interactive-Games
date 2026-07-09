#!/usr/bin/env python3
"""Angry Birds prototype.

Run with `python main.py` from a directory that has an `images/`
folder next to it containing: angry_birds.png, blocks.png,
background.png, sling-2.png, sling-2-r.png, selected-buttons.png.
"""

import math
import random

import numpy as np
import pygame


# ==========================================================================
# Constants
# ==========================================================================

# --- bird / block identities (plain ints instead of an enum, since we're
# keeping this to only the modules already in use) ---
BIRD_RED, BIRD_YELLOW, BIRD_BLUE, BIRD_BLACK = 0, 1, 2, 3
BLOCK_GLASS, BLOCK_WOOD, BLOCK_BRICK = 0, 1, 2

# --- physics ---
BIRD_GRAVITY = 0.1
BLOCK_GRAVITY_X = 0.0
BLOCK_GRAVITY_Y = 0.0
BOUNCE_DAMPING_Y = -0.4          # vertical velocity kept after a bounce
BOUNCE_DAMPING_X = 0.8           # horizontal velocity kept after a bounce
GROUND_Y = 650
LEFT_WALL_X = 80
RIGHT_WALL_X = 1360
REST_EPSILON = 0.1               # velocity below which we consider "stopped"
REST_DISTANCE_EPSILON = 0.5      # distance below which we snap to rest

# Per-type stats, indexed by BIRD_* / BLOCK_*.
BIRD_MASSES = [5, 3, 1, 7]
# damage[bird][block] = [glass, wood, brick]
BIRD_DAMAGE = [
    [10, 10, 10],   # red
    [7, 16, 7],     # yellow
    [15, 5, 5],     # blue
    [8, 8, 16],     # black
]
BLOCK_MASSES = [10, 7, 15]
BLOCK_DAMAGE = [[], [], []]
BLOCK_HEALTH = [60, 80, 100]   # glass, wood, brick

DAMAGE_MULTIPLIER = 3          # scales bird->block damage on impact

# --- slingshot / input ---
DOUBLE_CLICK_TIME_MS = 400
SLING_LAUNCH_POWER = 0.2
SLING_MAX_PULL_RADIUS = 60
SLING_ROPE_TRIM = 40            # how far back from the pouch the rope is drawn
SLING_RELEASE_DELAY_MS = 110    # pause before a fired bird starts moving

SLINGSHOT_CENTERS = [(330, 500), (1110, 500)]

# [ [left_rope_anchor, right_rope_anchor], ... ] one pair per slingshot
SLING_ROPE_ANCHORS = [
    [(310, 500), (355, 498)],
    [(1127, 500), (1085, 500)],
]

# Where the two halves of each sling image are drawn on screen.
SLING_BACK_LAYER_POS = [(290, 460), (1070, 460)]   # drawn behind birds/blocks
SLING_FRONT_LAYER_POS = [(279, 460), (1093, 460)]  # drawn in front

# --- block layout ---
BLOCK_SIZE = 80
BLOCK_ROWS = 6
BLOCK_COLS = 2
BLOCK_BASE_Y = 635
P1_STRUCTURE_ORIGIN_X = 160
P2_STRUCTURE_ORIGIN_X = 1280

# --- misc ---
BACKGROUND_POS = (80, 0)


# ==========================================================================
# Asset loading
# ==========================================================================

def slice_sheet(sheet, x, y, w, h):
    """Cut a w x h frame out of a sprite sheet at (x, y).

    Coordinates are truncated to ints before building the Rect (same as
    pygame's own Rect() does internally with raw floats). Doing it here
    once means the sheet math below (e.g. i * 73.3) can stay simple
    without silently landing a rect outside the sheet.
    """
    rect = pygame.Rect(int(x), int(y), int(w), int(h))
    return sheet.subsurface(rect).copy()


def crop(sheet, x1, y1, x2, y2):
    """Cut a frame out of a sheet given two corners instead of a size."""
    return slice_sheet(sheet, x1, y1, x2 - x1, y2 - y1)


class Assets:
    """Holds every loaded/sliced surface the game uses."""

    def __init__(self, image_dir="images/"):
        if not image_dir.endswith("/"):
            image_dir += "/"
        self.image_dir = image_dir

        self.buttons = {}
        self.background = None
        self.sling_back = []    # [left_sling, right_sling]
        self.sling_front = []
        self.bird_frames = []   # bird_frames[bird_id][frame_index]
        self.block_frames = []  # block_frames[block_id][frame_index]

    def _load(self, filename):
        return pygame.image.load(self.image_dir + filename).convert_alpha()

    def load(self):
        self._load_buttons()
        self._load_slings()
        self.background = self._load("background.png")
        self._load_birds()
        self._load_blocks()
        return self

    def _load_buttons(self):
        sheet = self._load("selected-buttons.png")
        self.buttons = {
            "restart": crop(sheet, 31, 14, 115, 97),
            "pause_small": crop(sheet, 171, 14, 217, 73),
            "pause_small2": crop(sheet, 217, 14, 263, 73),
            "play": crop(sheet, 266, 12, 492, 149),
            "pause": crop(sheet, 31, 121, 114, 204),
            "next": crop(sheet, 155, 112, 250, 217),
            "play_small": crop(sheet, 26, 223, 110, 306),
            "sound": crop(sheet, 154, 242, 259, 347),
            "menu": crop(sheet, 29, 324, 113, 407),
            "fast_forward": crop(sheet, 160, 376, 249, 465),
        }

    def _load_slings(self):
        left_sheet = self._load("sling-2.png")
        right_sheet = self._load("sling-2-r.png")

        left_outer = slice_sheet(left_sheet, 0, 0, 65, 300)
        left_inner = slice_sheet(left_sheet, 65, 0, 235, 300)
        right_inner = slice_sheet(right_sheet, 235, 0, 50, 225)
        right_outer = slice_sheet(right_sheet, 157, 0, 50, 225)

        # "back" layer draws behind birds/blocks, "front" layer on top,
        # matching the original LR/LL/RR/RL draw order.
        self.sling_back = [left_inner, right_outer]
        self.sling_front = [left_outer, right_inner]

    def _load_birds(self):
        sheet = self._load("angry_birds.png")

        red_sheet = crop(sheet, 180, 0, 180 + 619, 120)
        red = [slice_sheet(red_sheet, i * 75, 0, 75, 120) for i in range(5)]

        blue_sheet = crop(sheet, 210, 135, 210 + 300, 135 + 55)
        blue = [slice_sheet(blue_sheet, i * 60, 0, 60, 55) for i in range(5)]

        yellow_sheet = crop(sheet, 186, 205, 186 + 400, 205 + 85)
        yellow = [slice_sheet(yellow_sheet, i * 78, 0, 78, 85) for i in range(5)]

        black_sheet = crop(sheet, 115, 305, 115 + 575, 305 + 105)
        black = [slice_sheet(black_sheet, i * 73.3, 0, 73.3, 105) for i in range(6)]
        black += [slice_sheet(black_sheet, 440 + i * 67.5, 0, 67.5, 105) for i in range(2)]

        # Index must match BIRD_RED=0, BIRD_YELLOW=1, BIRD_BLUE=2, BIRD_BLACK=3.
        self.bird_frames = [red, yellow, blue, black]

    def _load_blocks(self):
        sheet = self._load("blocks.png")

        glass_sheet = crop(sheet, 0, 0, 85, 350)
        glass = [slice_sheet(glass_sheet, 2, i * 85 + i * 3.3, 80, 80) for i in range(4)]

        wood_sheet = crop(sheet, 584, 2, 584 + 80, 2 + 350)
        wood = [slice_sheet(wood_sheet, 0, i * 85 + i * 3.3, 80, 80) for i in range(4)]

        brick_sheet = crop(sheet, 1170, 1, 1170 + 345, 1 + 81)
        brick = [slice_sheet(brick_sheet, i * 85, 0, 80, 80) for i in range(4)]

        # Index must match BLOCK_GLASS=0, BLOCK_WOOD=1, BLOCK_BRICK=2.
        self.block_frames = [glass, wood, brick]

    def bird_frame(self, bird_id, frame_id):
        return self.bird_frames[bird_id][frame_id]

    def block_frame(self, block_id, frame_id):
        return self.block_frames[block_id][frame_id]


# ==========================================================================
# Entities
# ==========================================================================

class Bird(pygame.sprite.Sprite):
    def __init__(self, assets, position, vector, bird_id, frame_id, reverse, state):
        super().__init__()
        self.assets = assets
        self.bird_id = bird_id
        self.frame_id = frame_id
        self.state = state
        self.reverse = reverse

        self.gx = 0.0
        self.gy = BIRD_GRAVITY

        self.image = self._current_image()
        self.rect = self.image.get_rect(center=position)

        self.vector = vector
        self.mass = BIRD_MASSES[bird_id]
        self.damage = BIRD_DAMAGE[bird_id]

    def _current_image(self):
        frame = self.assets.bird_frame(self.bird_id, self.frame_id)
        if self.reverse:
            frame = pygame.transform.flip(frame, True, False)
        return frame

    def change_bird(self, bird_id, frame_id, state):
        self.bird_id = bird_id
        self.frame_id = frame_id
        self.state = state
        self.image = self._current_image()
        self.rect = self.image.get_rect(center=self.rect.center)

        self.mass = BIRD_MASSES[bird_id]
        self.damage = BIRD_DAMAGE[bird_id]

    def move(self, new_position):
        dx = new_position[0] - self.rect.center[0]
        dy = new_position[1] - self.rect.center[1]
        self.rect = self.rect.move(dx, dy)

    def update(self):
        if self.state == "movement":
            self.gy = BIRD_GRAVITY
            self.rect = self._calc_new_pos(self.rect, self.vector)
        elif self.state == "sling_op1":
            self.gy = 0.0
            self.rect = self._calc_new_pos(self.rect, self.vector)
        # "on_sling" / "sling_op": position is driven directly by the
        # mouse in Game, so there's nothing to integrate here.

    def _calc_new_pos(self, rect, vector):
        # Snap to rest on the ground once velocity/position are both settled.
        if abs(vector[1]) <= REST_EPSILON and abs(rect.center[1] - GROUND_Y) <= REST_DISTANCE_EPSILON:
            self.vector[1] = 0
            vector[1] = 0
            rect = rect.move(0, GROUND_Y - rect.center[1])

        # Snap to rest against the right wall.
        if vector[0] <= REST_EPSILON and abs(rect.center[0] - RIGHT_WALL_X) <= REST_DISTANCE_EPSILON:
            self.vector[0] = 0
            vector[0] = 0
            rect = rect.move(RIGHT_WALL_X - rect.center[0], 0)
        if rect.center[0] >= RIGHT_WALL_X:
            rect = rect.move(RIGHT_WALL_X - rect.center[0], 0)
            self.vector[0] = 0.0

        # Snap to rest against the left wall.
        if vector[0] >= -REST_EPSILON and abs(LEFT_WALL_X - rect.center[0]) <= REST_DISTANCE_EPSILON:
            self.vector[0] = 0
            vector[0] = 0
            rect = rect.move(LEFT_WALL_X - rect.center[0], 0)
        if rect.center[0] <= LEFT_WALL_X:
            rect = rect.move(LEFT_WALL_X - rect.center[0], 0)
            self.vector[0] = 0.0

        # Bounce off the ground.
        if rect.center[1] >= GROUND_Y:
            rect = rect.move(0, GROUND_Y - rect.center[1])
            self.vector[1] = BOUNCE_DAMPING_Y * vector[1]
            self.vector[0] = BOUNCE_DAMPING_X * vector[0]

        dx, dy = self.vector[0], self.vector[1]
        self.vector[0] += self.gx
        if abs(rect.center[1] - GROUND_Y) >= 0.2:
            self.vector[1] += self.gy

        return rect.move(dx, dy)


class Block(pygame.sprite.Sprite):
    def __init__(self, assets, position, vector, block_id, frame_id):
        super().__init__()
        self.assets = assets
        self.block_id = block_id
        self.frame_id = frame_id
        self.health = BLOCK_HEALTH[block_id]

        self.image = self.assets.block_frame(self.block_id, self.frame_id)
        self.rect = self.image.get_rect(center=position)

        self.vector = vector
        self.mass = BLOCK_MASSES[block_id]
        self.damage = BLOCK_DAMAGE[block_id]

    def update(self):
        max_health = BLOCK_HEALTH[self.block_id]
        damage_taken = max_health - self.health
        self.frame_id = 3 - int((damage_taken * 4) / max_health)
        self.image = self.assets.block_frame(self.block_id, self.frame_id)
        self.rect = self._calc_new_pos(self.rect, self.vector)

    def _calc_new_pos(self, rect, vector):
        if vector[1] <= REST_EPSILON and abs(rect.center[1] - GROUND_Y) <= REST_DISTANCE_EPSILON:
            self.vector[0] = 0
            self.vector[1] = 0
            rect = rect.move(0, GROUND_Y - rect.center[1])

        if rect.center[1] > GROUND_Y:
            rect = rect.move(0, GROUND_Y - rect.center[1])
            self.vector[1] = BOUNCE_DAMPING_Y * vector[1]
            self.vector[0] = BOUNCE_DAMPING_X * vector[0]

        dx, dy = self.vector[0], self.vector[1]
        self.vector[0] += BLOCK_GRAVITY_X
        if abs(rect.center[1] - GROUND_Y) >= 0.2:
            self.vector[1] += BLOCK_GRAVITY_Y

        return rect.move(dx, dy)


# ==========================================================================
# Game
# ==========================================================================

class Game:
    """Owns the window, the sprite groups, and the turn state machine.
    STATE is one of: "home", "idle", "sling_op" (aiming),
    "sling_op1" (just released, waiting to start moving).
    """

    def __init__(self, image_dir="images/"):
        pygame.init()

        info = pygame.display.Info()
        self.width, self.height = info.current_w, info.current_h
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
        pygame.display.set_caption("Angry Birds Prototype")

        self.clock = pygame.time.Clock()
        self.assets = Assets(image_dir).load()

        self.all_sprites = pygame.sprite.Group()
        self.bird_sprites = pygame.sprite.Group()
        self.block_sprites = pygame.sprite.Group()
        self.player_blocks = [pygame.sprite.Group(), pygame.sprite.Group()]

        self.birds = []
        self._setup_birds()
        self._setup_blocks()

        self.players = [1, 2]
        self.player = 1
        self.p_bird = self.birds[0]

        self.last_click_time = 0
        self.sling_op_time = 0
        self.state = "home"
        self.running = True

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------
    def _setup_birds(self):
        bird1 = Bird(self.assets, SLINGSHOT_CENTERS[0], [0, 0],
                     bird_id=BIRD_BLUE, frame_id=0, reverse=False, state="on_sling")
        bird2 = Bird(self.assets, SLINGSHOT_CENTERS[1], [0, 0],
                     bird_id=BIRD_BLACK, frame_id=0, reverse=True, state="on_sling")
        self.birds = [bird1, bird2]
        for bird in self.birds:
            self.all_sprites.add(bird)
            self.bird_sprites.add(bird)

    def _setup_blocks(self):
        p1_structure = np.random.randint(1, 4, (BLOCK_ROWS, BLOCK_COLS))
        p2_structure = p1_structure.copy()

        for col in range(BLOCK_COLS):
            for row in range(BLOCK_ROWS):
                pos = (P1_STRUCTURE_ORIGIN_X + col * BLOCK_SIZE,
                       BLOCK_BASE_Y - row * BLOCK_SIZE)
                self._add_block(pos, p1_structure[row][col] - 1, player_index=0)

        for col in range(BLOCK_COLS):
            for row in range(BLOCK_ROWS):
                pos = (P2_STRUCTURE_ORIGIN_X - col * BLOCK_SIZE,
                       BLOCK_BASE_Y - row * BLOCK_SIZE)
                self._add_block(pos, p2_structure[row][col] - 1, player_index=1)

    def _add_block(self, pos, block_id, player_index):
        block = Block(self.assets, pos, [0, 0], block_id, frame_id=3)
        self.all_sprites.add(block)
        self.block_sprites.add(block)
        self.player_blocks[player_index].add(block)

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_down(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP and self.state == "sling_op":
                self._release_sling()

    def _handle_mouse_down(self, mouse_pos):
        if not self.p_bird.rect.collidepoint(mouse_pos):
            return
        now = pygame.time.get_ticks()
        if now - self.last_click_time <= DOUBLE_CLICK_TIME_MS:
            self.state = "sling_op"
            self.p_bird.state = "sling_op"
        self.last_click_time = now

    def _release_sling(self):
        self.state = "sling_op1"
        self.p_bird.state = "sling_op1"

        center = SLINGSHOT_CENTERS[self.player - 1]
        self.p_bird.vector = [
            (center[0] - self.p_bird.rect.center[0]) * SLING_LAUNCH_POWER,
            (center[1] - self.p_bird.rect.center[1]) * SLING_LAUNCH_POWER,
        ]

        # Hand control to the other player's bird for next turn.
        self.p_bird = self.birds[self.player % 2]
        self.player = self.players[self.player % 2]
        self.sling_op_time = pygame.time.get_ticks()

    # ------------------------------------------------------------------
    # Update / collisions
    # ------------------------------------------------------------------
    def update(self):
        self.all_sprites.update()

    def _resolve_collisions(self):
        attacker = self.birds[self.player % 2]
        target_blocks = self.player_blocks[self.player - 1]

        hit = False
        for block in list(target_blocks):
            if not attacker.rect.colliderect(block.rect):
                continue
            hit = True
            block.health -= attacker.damage[block.block_id] * DAMAGE_MULTIPLIER
            if block.health <= 0:
                target_blocks.remove(block)
                self.all_sprites.remove(block)
                self.block_sprites.remove(block)

        if hit:
            attacker.change_bird(random.randint(0, 3), 0, "on_sling")
            attacker.vector = [0, 0]
            attacker.move(SLINGSHOT_CENTERS[self.player % 2])

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def draw(self):
        self.screen.fill((255, 255, 255))
        if self.state == "idle":
            self._draw_idle()
        elif self.state == "sling_op":
            self._draw_aiming()
        elif self.state == "sling_op1":
            self._draw_release()
        elif self.state == "home":
            self._draw_home()
        pygame.display.flip()

    def _draw_arena_background(self):
        self.screen.blit(self.assets.background, BACKGROUND_POS)
        self.screen.blit(self.assets.sling_back[0], SLING_BACK_LAYER_POS[0])
        self.screen.blit(self.assets.sling_back[1], SLING_BACK_LAYER_POS[1])

    def _draw_sling_front_layer(self):
        self.screen.blit(self.assets.sling_front[0], SLING_FRONT_LAYER_POS[0])
        self.screen.blit(self.assets.sling_front[1], SLING_FRONT_LAYER_POS[1])

    def _draw_idle(self):
        self._draw_arena_background()
        self._resolve_collisions()
        self.all_sprites.draw(self.screen)
        self._draw_sling_front_layer()

    def _draw_aiming(self):
        self._draw_arena_background()

        self.p_bird.move(pygame.mouse.get_pos())
        center = SLINGSHOT_CENTERS[self.player - 1]
        dx = center[0] - self.p_bird.rect.center[0]
        dy = center[1] - self.p_bird.rect.center[1]
        distance = math.hypot(dx, dy)

        if distance > SLING_MAX_PULL_RADIUS:
            scale = SLING_MAX_PULL_RADIUS / distance
            self.p_bird.move((center[0] - dx * scale, center[1] - dy * scale))
            dx *= scale
            dy *= scale
            distance = SLING_MAX_PULL_RADIUS

        self.block_sprites.draw(self.screen)

        rope_left, rope_right = SLING_ROPE_ANCHORS[self.player - 1]
        pouch = (self.p_bird.rect.center[0] - SLING_ROPE_TRIM * dx / distance,
                 self.p_bird.rect.center[1] - SLING_ROPE_TRIM * dy / distance)

        pygame.draw.line(self.screen, (90, 50, 20), rope_right, pouch, 10)
        self.bird_sprites.draw(self.screen)
        pygame.draw.line(self.screen, (90, 50, 20), rope_left, pouch, 10)

        self._draw_sling_front_layer()

    def _draw_release(self):
        self._draw_arena_background()
        self.block_sprites.draw(self.screen)

        if pygame.time.get_ticks() - self.sling_op_time >= SLING_RELEASE_DELAY_MS:
            self.birds[self.player % 2].state = "movement"
            self.state = "idle"

        self.bird_sprites.draw(self.screen)
        self._draw_sling_front_layer()

    def _draw_home(self):
        self.screen.blit(self.assets.buttons["play"], (500, 100))
        self.screen.blit(self.assets.buttons["pause"], (50, 100))

    # ------------------------------------------------------------------
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        pygame.quit()


def main():
    Game(image_dir="images/").run()


if __name__ == "__main__":
    main()
