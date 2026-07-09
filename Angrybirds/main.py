"""
Luffy - Gomu Gomu no Pistol
----------------------------
An original, shape-drawn 2D Luffy character (no image/sprite assets,
no background) that performs the stretchy "Pistol" punch attack.

Controls:
    SPACE   -> Trigger Gomu Gomu no Pistol
    ESC / Q -> Quit

Drawing style is inspired by the classic One Piece look (straw hat,
red vest, blue shorts, black spiky hair) but is built entirely from
primitive shapes (circles, polygons, lines) rather than any copied
artwork.
"""

import math
import sys
import pygame

# ----------------------------- Setup -----------------------------------
pygame.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Luffy - Gomu Gomu no Pistol")
clock = pygame.time.Clock()
FPS = 80

# Transparent ("no background") -> we clear with a flat neutral color
# each frame. If you want true transparency you'd need a different
# pipeline (this is a standard window surface), so we use a simple
# light backdrop that stays out of the way of the character.
BG_COLOR = (235, 235, 235)

# Colors
SKIN = (250, 207, 165)
SKIN_SHADOW = (230, 180, 140)
HAIR = (25, 22, 30)
VEST_RED = (190, 35, 40)
VEST_RED_DARK = (150, 20, 25)
SHORTS_BLUE = (60, 75, 150)
HAT_STRAW = (235, 196, 90)
HAT_STRAW_DARK = (200, 160, 60)
HAT_BAND_RED = (180, 30, 35)
OUTLINE = (20, 18, 22)
WHITE = (255, 255, 255)
MOTION_LINE = (120, 200, 210)

# ----------------------------- Character state --------------------------
# Luffy's body anchor (roughly torso center)
BODY_X, BODY_Y = 260, 330

# Punching arm state machine
STATE_IDLE = "idle"
STATE_WINDUP = "windup"
STATE_PUNCH = "punch"
STATE_HOLD = "hold"
STATE_RETRACT = "retract"

state = STATE_IDLE
state_timer = 0.0

# Arm stretch parameters
ARM_BASE_LEN = 70        # resting arm length
ARM_WINDUP_LEN = 40      # pulled-back (cocked) length
ARM_MAX_LEN = 620        # fully extended punch length
arm_len = ARM_BASE_LEN
arm_angle_deg = 0        # 0 = pointing right

WINDUP_TIME = 0.18
PUNCH_TIME = 0.10        # very fast snap-out
HOLD_TIME = 0.12         # brief hold at full extension
RETRACT_TIME = 0.35

hold_timer = 0.0

motion_lines = []  # list of dicts for little speed-line effects


def trigger_pistol():
    global state, state_timer, hold_timer
    if state == STATE_IDLE:
        state = STATE_WINDUP
        state_timer = 0.0


def ease_out_quad(t):
    return 1 - (1 - t) * (1 - t)


def ease_in_quad(t):
    return t * t


def update(dt):
    global state, state_timer, arm_len, hold_timer, motion_lines

    state_timer += dt

    if state == STATE_WINDUP:
        t = min(state_timer / WINDUP_TIME, 1.0)
        arm_len = ARM_BASE_LEN + (ARM_WINDUP_LEN - ARM_BASE_LEN) * ease_out_quad(t)
        if t >= 1.0:
            state = STATE_PUNCH
            state_timer = 0.0

    elif state == STATE_PUNCH:
        t = min(state_timer / PUNCH_TIME, 1.0)
        arm_len = ARM_WINDUP_LEN + (ARM_MAX_LEN - ARM_WINDUP_LEN) * ease_in_quad(t)
        # spawn motion lines while punching out
        if t < 1.0:
            motion_lines.append({
                "x": BODY_X + math.cos(math.radians(arm_angle_deg)) * arm_len * 0.5,
                "y": BODY_Y - 20 + math.sin(math.radians(arm_angle_deg)) * 8,
                "life": 0.25,
                "len": 30 + 40 * t,
            })
        if t >= 1.0:
            hold_timer = 0.0
            state = STATE_HOLD

    elif state == STATE_HOLD:
        hold_timer += dt
        if hold_timer >= HOLD_TIME:
            state = STATE_RETRACT
            state_timer = 0.0

    elif state == STATE_RETRACT:
        t = min(state_timer / RETRACT_TIME, 1.0)
        eased = ease_out_quad(t)
        arm_len = ARM_MAX_LEN + (ARM_BASE_LEN - ARM_MAX_LEN) * eased
        if t >= 1.0:
            arm_len = ARM_BASE_LEN
            state = STATE_IDLE
            state_timer = 0.0

    # update motion lines
    for m in motion_lines:
        m["life"] -= dt
    motion_lines = [m for m in motion_lines if m["life"] > 0]


# ----------------------------- Drawing helpers ---------------------------

def draw_straw_hat(surf, cx, cy, bob=0):
    """Draws the iconic straw hat, slightly above/behind the head."""
    hat_y = cy + bob
    # brim (ellipse)
    brim_rect = pygame.Rect(0, 0, 150, 46)
    brim_rect.center = (cx, hat_y + 8)
    pygame.draw.ellipse(surf, HAT_STRAW, brim_rect)
    pygame.draw.ellipse(surf, OUTLINE, brim_rect, 3)

    # top (dome)
    dome_rect = pygame.Rect(0, 0, 92, 60)
    dome_rect.center = (cx, hat_y - 14)
    pygame.draw.ellipse(surf, HAT_STRAW_DARK, dome_rect)
    dome_rect2 = pygame.Rect(0, 0, 92, 52)
    dome_rect2.center = (cx, hat_y - 18)
    pygame.draw.ellipse(surf, HAT_STRAW, dome_rect2)
    pygame.draw.ellipse(surf, OUTLINE, dome_rect2, 3)

    # red band
    band_rect = pygame.Rect(0, 0, 92, 16)
    band_rect.center = (cx, hat_y - 2)
    pygame.draw.ellipse(surf, HAT_BAND_RED, band_rect)
    pygame.draw.ellipse(surf, OUTLINE, band_rect, 2)


def draw_hair(surf, cx, cy):
    """Spiky black hair using a fan of triangles behind/around the head."""
    spike_count = 9
    base_r = 46
    for i in range(spike_count):
        a = math.radians(160 + i * (220 / (spike_count - 1)))  # arch over top
        tip_len = 34 + (8 if i % 2 == 0 else 0)
        bx = cx + math.cos(a) * base_r * 0.6
        by = cy + math.sin(a) * base_r * 0.6 - 6
        tx = cx + math.cos(a) * (base_r * 0.6 + tip_len)
        ty = cy + math.sin(a) * (base_r * 0.6 + tip_len) - 6
        # spike as a thin triangle
        perp = math.radians(math.degrees(a) + 90)
        w = 9
        p1 = (bx + math.cos(perp) * w, by + math.sin(perp) * w)
        p2 = (bx - math.cos(perp) * w, by - math.sin(perp) * w)
        pygame.draw.polygon(surf, HAIR, [p1, p2, (tx, ty)])
    # hair base cap
    pygame.draw.circle(surf, HAIR, (cx, cy - 4), 44)


def draw_head(surf, cx, cy, grin=True):
    # face
    pygame.draw.circle(surf, SKIN, (cx, cy), 40)
    pygame.draw.circle(surf, OUTLINE, (cx, cy), 40, 3)

    # ears
    pygame.draw.circle(surf, SKIN, (cx - 40, cy + 4), 9)
    pygame.draw.circle(surf, SKIN, (cx + 40, cy + 4), 9)

    # eyes (simple confident slits)
    pygame.draw.line(surf, OUTLINE, (cx - 22, cy - 2), (cx - 8, cy - 6), 3)
    pygame.draw.line(surf, OUTLINE, (cx + 8, cy - 6), (cx + 22, cy - 2), 3)

    # eyebrows
    pygame.draw.line(surf, OUTLINE, (cx - 24, cy - 14), (cx - 8, cy - 16), 3)
    pygame.draw.line(surf, OUTLINE, (cx + 8, cy - 16), (cx + 24, cy - 14), 3)

    # scar under eye (signature Luffy detail)
    pygame.draw.line(surf, OUTLINE, (cx - 16, cy + 6), (cx - 10, cy + 12), 2)

    # nose
    pygame.draw.line(surf, OUTLINE, (cx, cy), (cx - 2, cy + 8), 2)

    # big grin
    if grin:
        mouth_rect = pygame.Rect(0, 0, 36, 20)
        mouth_rect.center = (cx, cy + 20)
        pygame.draw.arc(surf, OUTLINE, mouth_rect, math.radians(200), math.radians(340), 3)
        pygame.draw.polygon(surf, WHITE, [
            (cx - 14, cy + 20), (cx + 14, cy + 20), (cx, cy + 28)
        ])
        pygame.draw.line(surf, OUTLINE, (cx - 14, cy + 20), (cx + 14, cy + 20), 2)

    draw_hair(surf, cx, cy)
    draw_straw_hat(surf, cx, cy - 46)


def draw_torso(surf, cx, cy):
    # red open vest as a rounded polygon
    points = [
        (cx - 34, cy - 30),
        (cx + 34, cy - 30),
        (cx + 44, cy + 60),
        (cx - 44, cy + 60),
    ]
    pygame.draw.polygon(surf, VEST_RED, points)
    pygame.draw.polygon(surf, OUTLINE, points, 3)
    # chest skin showing (open vest)
    pygame.draw.polygon(surf, SKIN, [
        (cx - 8, cy - 26), (cx + 8, cy - 26), (cx + 10, cy + 40), (cx - 10, cy + 40)
    ])
    # vest shading
    pygame.draw.line(surf, VEST_RED_DARK, (cx - 30, cy - 20), (cx - 38, cy + 50), 4)


def draw_shorts(surf, cx, cy):
    rect = pygame.Rect(0, 0, 90, 46)
    rect.center = (cx, cy)
    pygame.draw.rect(surf, SHORTS_BLUE, rect, border_radius=10)
    pygame.draw.rect(surf, OUTLINE, rect, 3, border_radius=10)


def draw_leg(surf, hip, length, angle_deg, bend=True):
    a = math.radians(angle_deg)
    knee = (hip[0] + math.cos(a) * length * 0.5, hip[1] + math.sin(a) * length * 0.5 + 14)
    foot = (knee[0] + math.cos(a) * length * 0.55, knee[1] + math.sin(a) * length * 0.55)
    pygame.draw.line(surf, SKIN, hip, knee, 16)
    pygame.draw.line(surf, SKIN, knee, foot, 14)
    pygame.draw.circle(surf, OUTLINE, (int(foot[0]), int(foot[1])), 9, 2)


def draw_static_arm(surf, shoulder, length, angle_deg):
    """The non-punching arm, tucked back for a dynamic flying pose."""
    a = math.radians(angle_deg)
    elbow = (shoulder[0] + math.cos(a) * length * 0.5,
              shoulder[1] + math.sin(a) * length * 0.5)
    hand = (elbow[0] + math.cos(a + 0.3) * length * 0.5,
            elbow[1] + math.sin(a + 0.3) * length * 0.5)
    pygame.draw.line(surf, SKIN, shoulder, elbow, 15)
    pygame.draw.line(surf, SKIN, elbow, hand, 13)
    pygame.draw.circle(surf, SKIN, (int(hand[0]), int(hand[1])), 9)
    pygame.draw.circle(surf, OUTLINE, (int(hand[0]), int(hand[1])), 9, 2)


def draw_stretch_arm(surf, shoulder, length, angle_deg):
    """The rubber Gomu Gomu arm: stretches thin as it extends."""
    a = math.radians(angle_deg)
    end_x = shoulder[0] + math.cos(a) * length
    end_y = shoulder[1] + math.sin(a) * length

    # Thickness shrinks the longer it stretches (rubbery look),
    # but never gets too thin to read.
    stretch_ratio = min(length / ARM_MAX_LEN, 1.0)
    thickness = max(20 - stretch_ratio * 11, 9)

    # slight sine wiggle along the arm during the punch for a "whip" feel
    segments = 14
    pts = []
    for i in range(segments + 1):
        t = i / segments
        x = shoulder[0] + (end_x - shoulder[0]) * t
        y = shoulder[1] + (end_y - shoulder[1]) * t
        wiggle = math.sin(t * math.pi) * 6 * (1 - stretch_ratio * 0.6)
        if state in (STATE_PUNCH, STATE_HOLD):
            y += wiggle * math.sin(pygame.time.get_ticks() * 0.02)
        pts.append((x, y))

    if len(pts) >= 2:
        pygame.draw.lines(surf, SKIN, False, pts, int(thickness))
        # outline for readability
        pygame.draw.lines(surf, SKIN_SHADOW, False, pts, max(int(thickness) - 6, 2))

    # fist at the end
    fist_r = 16 if stretch_ratio < 0.9 else 18
    pygame.draw.circle(surf, SKIN, (int(end_x), int(end_y)), fist_r)
    pygame.draw.circle(surf, OUTLINE, (int(end_x), int(end_y)), fist_r, 3)
    # knuckle lines
    for off in (-6, 0, 6):
        nx = end_x + math.cos(a + 1.57) * off
        ny = end_y + math.sin(a + 1.57) * off
        pygame.draw.line(surf, SKIN_SHADOW,
                          (nx, ny), (nx + math.cos(a) * 6, ny + math.sin(a) * 6), 2)

    return (end_x, end_y)


def draw_hat_string(surf, hat_anchor):
    """During the punch, the hat string trails dramatically (as in the
    reference pose) from the hat toward/behind the character."""
    if state in (STATE_PUNCH, STATE_HOLD, STATE_RETRACT):
        # simple curved trail behind the head, opposite of punch direction
        sx, sy = hat_anchor
        ctrl = (sx - 60, sy - 70)
        end = (sx - 140, sy - 40)
        pts = []
        for i in range(20):
            t = i / 19
            x = (1 - t) ** 2 * sx + 2 * (1 - t) * t * ctrl[0] + t ** 2 * end[0]
            y = (1 - t) ** 2 * sy + 2 * (1 - t) * t * ctrl[1] + t ** 2 * end[1]
            pts.append((x, y))
        pygame.draw.lines(surf, HAT_BAND_RED, False, pts, 2)


def draw_motion_lines(surf):
    for m in motion_lines:
        alpha = max(int(255 * (m["life"] / 0.25)), 0)
        color = (*MOTION_LINE,)
        x, y, l = m["x"], m["y"], m["len"]
        line_surf = pygame.Surface((int(l) + 4, 6), pygame.SRCALPHA)
        pygame.draw.line(line_surf, (*MOTION_LINE, alpha), (0, 3), (l, 3), 3)
        surf.blit(line_surf, (x - l, y))


def draw_speed_burst(surf, x, y):
    """Small impact/speed flash at full extension."""
    if state == STATE_HOLD:
        for i in range(8):
            a = math.radians(i * 45 + pygame.time.get_ticks() * 0.05)
            x2 = x + math.cos(a) * 30
            y2 = y + math.sin(a) * 30
            x3 = x + math.cos(a) * 16
            y3 = y + math.sin(a) * 16
            pygame.draw.line(surf, (255, 230, 120), (x3, y3), (x2, y2), 3)


def draw_luffy(surf):
    # slight idle bob
    bob = math.sin(pygame.time.get_ticks() * 0.004) * 4 if state == STATE_IDLE else 0

    body_x, body_y = BODY_X, BODY_Y + bob
    head_pos = (body_x - 6, body_y - 76)
    shoulder = (body_x + 18, body_y - 50)
    static_shoulder = (body_x - 18, body_y - 48)
    hip = (body_x, body_y + 50)

    # back leg, then torso, then front leg (simple depth ordering)
    draw_leg(surf, (hip[0] - 14, hip[1]), 95, 100)
    draw_torso(surf, body_x, body_y)
    draw_shorts(surf, body_x, body_y + 46)
    draw_leg(surf, (hip[0] + 14, hip[1]), 95, 80)

    # static (non-punching) arm tucked behind for dynamic pose
    draw_static_arm(surf, static_shoulder, 65, 200)

    # head
    draw_head(surf, *head_pos)

    # hat string trailing during punch
    draw_hat_string(surf, (head_pos[0] + 20, head_pos[1] - 60))

    # punching arm (on top, drawn last so it reads clearly)
    fist_pos = draw_stretch_arm(surf, shoulder, arm_len, arm_angle_deg)

    draw_speed_burst(surf, *fist_pos)

    return fist_pos


def draw_ui(surf, font):
    label = "Press SPACE to throw Gomu Gomu no PISTOL!  (ESC to quit)"
    txt = font.render(label, True, (60, 60, 60))
    surf.blit(txt, (20, HEIGHT - 36))

    state_label = font.render(f"state: {state}", True, (120, 120, 120))
    surf.blit(state_label, (20, 20))


# ----------------------------- Main loop ---------------------------------

def main():
    global arm_angle_deg
    font = pygame.font.SysFont("arial", 18)
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif event.key == pygame.K_SPACE:
                    trigger_pistol()

        update(dt)

        screen.fill(BG_COLOR)
        draw_motion_lines(screen)
        draw_luffy(screen)
        draw_ui(screen, font)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()