"""
Luffy – Gomu Gomu no PISTOL  (Legendary Edition)
===================================================
Cinematic manga-style animation built entirely from pygame primitives.
Multi-pass cel-shading, ink outlines, halftone dots, speed-line bursts,
impact kanji, chromatic-abberation flash, screen shake.

Controls
--------
SPACE / click  → Gomu Gomu no PISTOL
ESC / Q        → Quit
"""

import math, sys, random
import pygame
from pygame import gfxdraw

# ── init ──────────────────────────────────────────────────────────────
pygame.init()
W, H = 960, 640
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Luffy – Gomu Gomu no PISTOL  ✦  Legendary")
clock  = pygame.time.Clock()
FPS    = 60

# ── palette ───────────────────────────────────────────────────────────
class C:
    BG          = (245, 238, 215)       # aged manga paper
    BG_DARK     = (220, 210, 185)
    INK         = ( 18,  14,  22)       # deep ink black
    INK_SOFT    = ( 40,  34,  50)
    SKIN_LIT    = (250, 205, 148)
    SKIN_MID    = (232, 172, 100)
    SKIN_SHA    = (195, 128,  68)
    SKIN_DRK    = (155,  92,  40)
    HAIR        = ( 22,  18,  28)
    HAT_LIT     = (242, 200,  72)
    HAT_MID     = (210, 162,  38)
    HAT_SHA     = (170, 122,  18)
    HAT_BAND    = (192,  28,  32)
    HAT_BAND_D  = (140,  16,  20)
    VEST_LIT    = (210,  48,  52)
    VEST_MID    = (172,  28,  32)
    VEST_SHA    = (120,  14,  18)
    VEST_RIM    = (240,  80,  70)
    SHORT_LIT   = ( 80, 110, 200)
    SHORT_MID   = ( 52,  78, 165)
    SHORT_SHA   = ( 28,  48, 118)
    WHITE       = (255, 255, 255)
    SCAR        = (200,  70,  70)
    SPEED_BLUE  = (100, 195, 230)
    SPEED_CYAN  = (160, 230, 248)
    IMPACT_YLW  = (255, 228,  50)
    IMPACT_ORG  = (255, 130,  20)
    IMPACT_RED  = (220,  30,  20)
    SHINE       = (255, 248, 200)
    KANJI_RED   = (200,  20,  20)

# ── helpers ───────────────────────────────────────────────────────────
def lerp(a, b, t): return a + (b-a)*t
def lerpC(ca, cb, t):
    return tuple(int(lerp(ca[i], cb[i], t)) for i in range(3))
def clamp(v, lo=0.0, hi=1.0): return max(lo, min(hi, v))
def ease_out(t): return 1-(1-t)**3
def ease_in(t):  return t**3
def ease_io(t):  return t*t*(3-2*t)

# ── thick anti-aliased circle outline ────────────────────────────────
def aa_circle(surf, color, cx, cy, r, w=2):
    for i in range(w):
        ri = r - i
        if ri > 0:
            gfxdraw.aacircle(surf, int(cx), int(cy), int(ri), color)

# ── filled polygon with outline ───────────────────────────────────────
def poly(surf, fill, pts, outline=None, ow=2):
    if len(pts) < 3: return
    ipts = [(int(x), int(y)) for x,y in pts]
    if fill:
        gfxdraw.filled_polygon(surf, ipts, fill)
        gfxdraw.aapolygon(surf, ipts, fill)
    if outline:
        pygame.draw.polygon(surf, outline, ipts, ow)

# ── thick line ────────────────────────────────────────────────────────
def thick_line(surf, color, p1, p2, w):
    x1,y1 = int(p1[0]),int(p1[1])
    x2,y2 = int(p2[0]),int(p2[1])
    dx, dy = x2-x1, y2-y1
    dist = math.hypot(dx,dy)
    if dist == 0: return
    nx, ny = -dy/dist, dx/dist
    hw = w/2
    pts = [
        (x1+nx*hw, y1+ny*hw), (x2+nx*hw, y2+ny*hw),
        (x2-nx*hw, y2-ny*hw), (x1-nx*hw, y1-ny*hw)
    ]
    poly(surf, color, pts)

# ── bezier sampler ────────────────────────────────────────────────────
def bezier3(p0, p1, p2, p3, n=40):
    pts = []
    for i in range(n+1):
        t = i/n
        u = 1-t
        x = u**3*p0[0] + 3*u**2*t*p1[0] + 3*u*t**2*p2[0] + t**3*p3[0]
        y = u**3*p0[1] + 3*u**2*t*p1[1] + 3*u*t**2*p2[1] + t**3*p3[1]
        pts.append((x,y))
    return pts

def bezier2(p0, p1, p2, n=30):
    pts = []
    for i in range(n+1):
        t = i/n
        u = 1-t
        x = u**2*p0[0] + 2*u*t*p1[0] + t**2*p2[0]
        y = u**2*p0[1] + 2*u*t*p1[1] + t**2*p2[1]
        pts.append((x,y))
    return pts

def draw_thick_curve(surf, color, pts, w):
    if len(pts) < 2: return
    for i in range(len(pts)-1):
        thick_line(surf, color, pts[i], pts[i+1], w)
    # round caps
    for p in [pts[0], pts[-1]]:
        pygame.draw.circle(surf, color, (int(p[0]),int(p[1])), max(1,w//2))

# ── state machine ─────────────────────────────────────────────────────
ST_IDLE, ST_WIND, ST_PUNCH, ST_HOLD, ST_RET = 0,1,2,3,4
state      = ST_IDLE
st_timer   = 0.0
hold_timer = 0.0
T_WIND  = 0.20
T_PUNCH = 0.10
T_HOLD  = 0.18
T_RET   = 0.42

ARM_BASE  = 82
ARM_WIND  = 44
ARM_MAX   = 580
arm_len   = float(ARM_BASE)
idle_t    = 0.0

shake      = [0,0]
shake_mag  = 0.0

# particles
class Particle:
    def __init__(self, x,y, vx,vy, color, life, r, grav=0):
        self.x,self.y = x,y
        self.vx,self.vy = vx,vy
        self.color = color
        self.life = self.max_life = life
        self.r = r
        self.grav = grav
    def update(self,dt):
        self.x += self.vx*dt
        self.y += self.vy*dt
        self.vy += self.grav*dt
        self.life -= dt
        return self.life > 0
    def draw(self,surf):
        a = clamp(self.life/self.max_life)
        r = max(1, int(self.r*a))
        c = (*self.color, int(255*a))
        s = pygame.Surface((r*2+2,r*2+2), pygame.SRCALPHA)
        gfxdraw.filled_circle(s, r+1,r+1, r, c)
        surf.blit(s,(int(self.x)-r-1,int(self.y)-r-1))

class SpeedLine:
    def __init__(self, x,y, angle, length, life, w=1.5):
        self.x,self.y = x,y
        self.angle = angle
        self.length = length
        self.life = self.max_life = life
        self.w = w
    def update(self,dt):
        self.x -= 600*dt*math.cos(self.angle)
        self.life -= dt
        return self.life > 0
    def draw(self,surf):
        a = clamp(self.life/self.max_life)**0.5
        ex = self.x + math.cos(self.angle)*self.length
        ey = self.y + math.sin(self.angle)*self.length
        c = (*C.SPEED_BLUE, int(200*a))
        s = pygame.Surface((W,H), pygame.SRCALPHA)
        pygame.draw.line(s, c,(int(self.x),int(self.y)),(int(ex),int(ey)),max(1,int(self.w)))
        surf.blit(s,(0,0))

particles  = []
speed_lines= []

def spawn_impact(x, y):
    for _ in range(55):
        ang = random.uniform(0,math.pi*2)
        spd = random.uniform(80,420)
        col = random.choice([C.IMPACT_YLW,C.IMPACT_ORG,C.IMPACT_RED,C.WHITE])
        r   = random.uniform(3,12)
        li  = random.uniform(0.25,0.55)
        particles.append(Particle(x,y, math.cos(ang)*spd, math.sin(ang)*spd, col, li, r, 300))
    # ring shockwave-style lines
    for i in range(22):
        ang = (i/22)*math.pi*2
        spd = random.uniform(220,380)
        particles.append(Particle(x,y, math.cos(ang)*spd, math.sin(ang)*spd, C.SHINE, 0.18, 4))

# ── trigger ───────────────────────────────────────────────────────────
def trigger():
    global state, st_timer
    if state == ST_IDLE:
        state, st_timer = ST_WIND, 0.0

# ── update ────────────────────────────────────────────────────────────
def update(dt):
    global state, st_timer, hold_timer, arm_len, idle_t, shake_mag, shake

    idle_t  += dt
    st_timer += dt
    shake_mag = max(0, shake_mag - dt*18)
    shake = [random.uniform(-shake_mag,shake_mag)*10,
             random.uniform(-shake_mag,shake_mag)*10]

    if state == ST_WIND:
        t = clamp(st_timer/T_WIND)
        arm_len = lerp(ARM_BASE, ARM_WIND, ease_out(t))
        if t >= 1: state,st_timer = ST_PUNCH, 0.0

    elif state == ST_PUNCH:
        t = clamp(st_timer/T_PUNCH)
        arm_len = lerp(ARM_WIND, ARM_MAX, ease_in(t))
        # spray speed lines
        if t < 0.95:
            frac = arm_len/ARM_MAX
            for _ in range(4):
                ox = random.uniform(-50,50)
                oy = random.uniform(-60,60)
                sx = BX + 38 + arm_len*0.4 + ox
                sy = BY - 55 + oy
                speed_lines.append(SpeedLine(
                    sx, sy, 0,
                    random.uniform(40,120)*frac + 30,
                    random.uniform(0.1,0.22),
                    random.uniform(1.5,3.5)))
        if t >= 1:
            hold_timer = 0.0
            state = ST_HOLD
            shake_mag = 1.0
            spawn_impact(BX+38+ARM_MAX*0.99, BY-55)

    elif state == ST_HOLD:
        hold_timer += dt
        if hold_timer >= T_HOLD:
            state,st_timer = ST_RET, 0.0

    elif state == ST_RET:
        t = clamp(st_timer/T_RET)
        arm_len = lerp(ARM_MAX, ARM_BASE, ease_out(t))
        if t >= 1:
            arm_len = ARM_BASE
            state,st_timer = ST_IDLE, 0.0

    # update fx
    speed_lines[:] = [sl for sl in speed_lines if sl.update(dt)]
    particles[:]   = [p  for p  in particles  if p.update(dt)]

# ── body anchor ───────────────────────────────────────────────────────
BX, BY = 260, 320

# ══════════════════════════════════════════════════════════════════════
#  DRAWING FUNCTIONS
# ══════════════════════════════════════════════════════════════════════

def draw_bg(surf):
    surf.fill(C.BG)
    # subtle halftone dot grid
    s = pygame.Surface((W,H), pygame.SRCALPHA)
    step = 18
    for gy in range(0, H, step):
        for gx in range(0, W, step):
            d = int(1.5 + 0.5*math.sin(gx*0.04)*math.sin(gy*0.04))
            gfxdraw.filled_circle(s, gx, gy, d, (160,148,120,55))
    surf.blit(s, (0,0))

    # panel lines (manga panel border feel)
    for i in range(3):
        pygame.draw.line(surf, C.BG_DARK, (0, i), (W, i), 1)
        pygame.draw.line(surf, C.BG_DARK, (0, H-1-i), (W, H-1-i), 1)

def draw_radial_speedlines(surf):
    """Background radial burst during punch – manga style."""
    if state not in (ST_PUNCH, ST_HOLD): return
    frac = 1.0 if state==ST_HOLD else clamp(st_timer/T_PUNCH)
    cx, cy = BX+38+ARM_MAX*0.5, BY-55
    s = pygame.Surface((W,H), pygame.SRCALPHA)
    count = 64
    for i in range(count):
        ang = (i/count)*math.pi*2
        r0  = 40
        r1  = random.uniform(300,600)
        x0  = cx + math.cos(ang)*r0
        y0  = cy + math.sin(ang)*r0
        x1  = cx + math.cos(ang)*r1
        y1  = cy + math.sin(ang)*r1
        alpha = int(frac * random.uniform(60,130))
        col = (*C.SPEED_BLUE, alpha) if i%3 else (*C.SPEED_CYAN, alpha//2)
        pygame.draw.line(s, col, (int(x0),int(y0)),(int(x1),int(y1)),
                         1 if i%2 else 2)
    surf.blit(s,(0,0))


# ── hat ───────────────────────────────────────────────────────────────
def draw_hat(surf, cx, cy):
    # brim shadow
    brim_pts_sha = [(cx-78,cy+16),(cx+78,cy+16),(cx+70,cy+28),(cx-70,cy+28)]
    poly(surf, C.HAT_SHA, brim_pts_sha)

    # brim main
    brim_pts = [(cx-76,cy+6),(cx+76,cy+6),(cx+68,cy+20),(cx-68,cy+20)]
    poly(surf, C.HAT_MID, brim_pts, C.INK, 2)

    # brim lit top surface
    brim_top = [(cx-72,cy+2),(cx+72,cy+2),(cx+68,cy+12),(cx-68,cy+12)]
    poly(surf, C.HAT_LIT, brim_top)

    # brim highlight streak
    hl_pts = bezier2((cx-50,cy+4),(cx,cy),(cx+50,cy+4))
    draw_thick_curve(surf, C.SHINE, hl_pts, 3)

    # dome back shadow
    dome_sha_r = pygame.Rect(cx-50, cy-68, 100, 76)
    pygame.draw.ellipse(surf, C.HAT_SHA, dome_sha_r)

    # dome main
    dome_r = pygame.Rect(cx-46, cy-72, 92, 76)
    pygame.draw.ellipse(surf, C.HAT_MID, dome_r)
    pygame.draw.ellipse(surf, C.INK, dome_r, 2)

    # dome lit
    dome_lit_r = pygame.Rect(cx-42, cy-70, 60, 54)
    pygame.draw.ellipse(surf, C.HAT_LIT, dome_lit_r)

    # dome specular
    spec_r = pygame.Rect(cx-28, cy-68, 32, 20)
    pygame.draw.ellipse(surf, C.SHINE, spec_r)

    # red band
    band_r = pygame.Rect(cx-48, cy-10, 96, 22)
    pygame.draw.ellipse(surf, C.HAT_BAND, band_r)
    pygame.draw.ellipse(surf, C.HAT_BAND_D, band_r, 3)
    band_hl = pygame.Rect(cx-38, cy-8, 50, 8)
    pygame.draw.ellipse(surf, C.VEST_RIM, band_hl)

    # ink outline dome
    pygame.draw.ellipse(surf, C.INK, dome_r, 3)
    pygame.draw.polygon(surf, C.INK, [(cx-76,cy+6),(cx+76,cy+6),(cx+68,cy+20),(cx-68,cy+20)], 2)


# ── hair ─────────────────────────────────────────────────────────────
def draw_hair(surf, cx, cy):
    # hair base dome (behind face)
    pygame.draw.ellipse(surf, C.HAIR, (cx-38, cy-42, 76, 60))

    # individual spikes
    spikes = [
        (-2.25, 28), (-2.05, 22), (-1.78, 32), (-1.52, 24),
        (-1.25, 30), (-0.98, 20), (-0.72, 26), (-0.48, 18),
    ]
    for ang, slen in spikes:
        bx = cx + math.cos(ang)*30
        by = cy - 2 + math.sin(ang)*30
        tx = cx + math.cos(ang)*(30+slen)
        ty = cy - 2 + math.sin(ang)*(30+slen)
        perp = ang + math.pi/2
        w = 8
        p1 = (bx+math.cos(perp)*w, by+math.sin(perp)*w)
        p2 = (bx-math.cos(perp)*w, by-math.sin(perp)*w)
        poly(surf, C.HAIR, [p1,p2,(tx,ty)], C.INK, 2)

    # sideburns
    pygame.draw.ellipse(surf, C.HAIR, (cx-42, cy+2, 16, 24))
    pygame.draw.ellipse(surf, C.HAIR, (cx+26, cy+2, 16, 24))

    # hair shine
    shine_pts = bezier2((cx-18,cy-38),(cx-8,cy-44),(cx+4,cy-40))
    draw_thick_curve(surf, (80,72,90), shine_pts, 3)


# ── face ─────────────────────────────────────────────────────────────
def draw_face(surf, cx, cy):
    # jaw shadow
    pygame.draw.ellipse(surf, C.SKIN_SHA, (cx-32, cy-6, 64, 52))
    # main face
    pygame.draw.ellipse(surf, C.SKIN_MID, (cx-33, cy-38, 66, 72))
    pygame.draw.ellipse(surf, C.SKIN_LIT, (cx-31, cy-40, 62, 60))
    # face outline
    pygame.draw.ellipse(surf, C.INK, (cx-33, cy-40, 66, 74), 3)

    # cheek blush
    s = pygame.Surface((W,H), pygame.SRCALPHA)
    gfxdraw.filled_ellipse(s, cx-22, cy+8, 10, 6, (220,100,80,50))
    gfxdraw.filled_ellipse(s, cx+22, cy+8, 10, 6, (220,100,80,50))
    surf.blit(s,(0,0))

    # ears
    for ex, ew in [(cx-35, 1), (cx+35, -1)]:
        pygame.draw.ellipse(surf, C.SKIN_MID, (ex-9, cy+2, 18, 22))
        pygame.draw.ellipse(surf, C.INK, (ex-9, cy+2, 18, 22), 2)
        pygame.draw.ellipse(surf, C.SKIN_SHA, (ex-4+ew*2, cy+6, 8, 12))

    punch_squint = 1 if state in (ST_PUNCH,ST_HOLD) else 0

    # eyebrows – bold manga style
    for side in (-1, 1):
        ex0 = cx + side*26
        ex1 = cx + side*8
        ey0 = cy - 14 + punch_squint*2
        ey1 = cy - 18 + punch_squint*3
        pts = bezier2((ex0,ey0),(cx+side*17,ey1-2),(ex1,ey1))
        draw_thick_curve(surf, C.INK, pts, 4)

    # eyes
    for side in (-1,1):
        ecx = cx + side*18
        ecy = cy - 3 + punch_squint*2
        # white
        pygame.draw.ellipse(surf, C.WHITE, (ecx-10, ecy-7, 20, 14))
        # iris
        pygame.draw.ellipse(surf, (50,35,20), (ecx-6, ecy-5, 12, 10))
        # pupil
        pygame.draw.ellipse(surf, C.INK, (ecx-4, ecy-4, 8, 8))
        # shine
        gfxdraw.filled_circle(surf, ecx-2, ecy-2, 3, C.WHITE)
        # eye outline
        pygame.draw.ellipse(surf, C.INK, (ecx-10, ecy-7, 20, 14), 2)
        # upper lid crease
        pts = bezier2((ecx-10,ecy-3),(ecx,ecy-9-punch_squint*2),(ecx+10,ecy-3))
        draw_thick_curve(surf, C.INK, pts, 2)

    # scar (2 short parallel lines)
    pygame.draw.line(surf, C.SCAR, (cx-15,cy+5),(cx-9,cy+14), 3)
    pygame.draw.line(surf, C.SCAR, (cx-12,cy+5),(cx-6,cy+14), 2)

    # nose
    pts = bezier2((cx+2,cy+4),(cx+5,cy+10),(cx+1,cy+16))
    draw_thick_curve(surf, C.SKIN_DRK, pts, 2)

    # big grin
    gw = 28 + (state in (ST_PUNCH,ST_HOLD))*4
    smile = bezier2((cx-gw,cy+21),(cx,cy+36),(cx+gw,cy+21), 20)
    draw_thick_curve(surf, C.INK, smile, 3)

    # teeth fill
    tooth_pts = [(cx-gw+2,cy+22)] + list(bezier2((cx-gw+2,cy+22),(cx,cy+34),(cx+gw-2,cy+22),20)) + [(cx+gw-2,cy+22)]
    poly(surf, C.WHITE, tooth_pts)
    # tooth dividers
    for ox in [-16,-8,0,8,16]:
        bx2 = cx + ox
        pygame.draw.line(surf, C.SKIN_MID,(bx2, cy+22),(bx2, cy+30), 1)
    draw_thick_curve(surf, C.INK, smile, 3)


# ── torso ─────────────────────────────────────────────────────────────
def draw_torso(surf, cx, cy):
    # vest shadow layer
    sha_pts = [
        (cx-34, cy-42), (cx+36, cy-42),
        (cx+50, cy+62), (cx-50, cy+62)
    ]
    poly(surf, C.VEST_SHA, sha_pts)

    # vest mid
    mid_pts = [
        (cx-32, cy-44), (cx+34, cy-44),
        (cx+46, cy+60), (cx-46, cy+60)
    ]
    poly(surf, C.VEST_MID, mid_pts, C.INK, 3)

    # vest lit left panel
    lit_l = [
        (cx-32, cy-44), (cx-10, cy-44),
        (cx-8,  cy+60), (cx-46, cy+60)
    ]
    poly(surf, C.VEST_LIT, lit_l)

    # vest lit right panel
    lit_r = [
        (cx+10, cy-44), (cx+34, cy-44),
        (cx+46, cy+60), (cx+8,  cy+60)
    ]
    poly(surf, C.VEST_LIT, lit_r)

    # rim-light edge right
    rim_pts = [
        (cx+32, cy-40), (cx+36, cy-40),
        (cx+48, cy+56), (cx+44, cy+56)
    ]
    poly(surf, C.VEST_RIM, rim_pts)

    # chest skin strip (open vest)
    chest = [
        (cx-10, cy-40), (cx+10, cy-40),
        (cx+9,  cy+60), (cx-9,  cy+60)
    ]
    poly(surf, C.SKIN_MID, chest)
    poly(surf, C.SKIN_LIT, [(cx-8,cy-38),(cx+6,cy-38),(cx+5,cy+60),(cx-7,cy+60)])

    # ink outline vest
    poly(surf, None, mid_pts, C.INK, 3)

    # vest fold lines
    for yoff, xshift in [(cy-10,3),(cy+15,5),(cy+35,8)]:
        pts = bezier2((cx-30+xshift,yoff-2),(cx,yoff+4),(cx+30+xshift,yoff-2))
        pygame.draw.lines(surf, C.VEST_SHA, False, [(int(x),int(y)) for x,y in pts], 2)


# ── shorts ────────────────────────────────────────────────────────────
def draw_shorts(surf, cx, cy):
    sha = [
        (cx-46, cy-2), (cx+46, cy-2),
        (cx+42, cy+52), (cx-42, cy+52)
    ]
    poly(surf, C.SHORT_SHA, sha)

    mid = [
        (cx-44, cy-4), (cx+44, cy-4),
        (cx+40, cy+50), (cx-40, cy+50)
    ]
    poly(surf, C.SHORT_MID, mid, C.INK, 3)

    lit = [
        (cx-10, cy-4), (cx+40, cy-4),
        (cx+36, cy+50), (cx-8,  cy+50)
    ]
    poly(surf, C.SHORT_LIT, lit)

    # highlight band
    hl = [(cx+4,cy),(cx+36,cy),(cx+34,cy+10),(cx+2,cy+10)]
    s = pygame.Surface((W,H), pygame.SRCALPHA)
    gfxdraw.filled_polygon(s, [(int(x),int(y)) for x,y in hl], (*C.WHITE,40))
    surf.blit(s,(0,0))

    # waistband
    wb = [(cx-44,cy-4),(cx+44,cy-4),(cx+44,cy+4),(cx-44,cy+4)]
    poly(surf, C.SHORT_SHA, wb, C.INK, 2)

    poly(surf, None, mid, C.INK, 3)


# ── leg ───────────────────────────────────────────────────────────────
def draw_leg(surf, hx, hy, flip, bob=0):
    # thigh
    kx = hx + flip*6
    ky = hy + 50 + bob*0.3
    # calf
    fx = kx + flip*10
    fy = ky + 50

    # shadow layer
    draw_thick_curve(surf, C.SKIN_SHA,
        bezier2((hx,hy),(kx-flip*4,ky-10),(kx,ky)), 24)
    # mid skin
    draw_thick_curve(surf, C.SKIN_MID,
        bezier2((hx,hy),(kx-flip*4,ky-10),(kx,ky)), 20)
    # lit
    draw_thick_curve(surf, C.SKIN_LIT,
        bezier2((hx+flip*4,hy),(kx,ky-12),(kx+flip*2,ky)), 14)

    # knee cap
    pygame.draw.circle(surf, C.SKIN_MID, (int(kx),int(ky)), 13)
    pygame.draw.circle(surf, C.SKIN_LIT, (int(kx+flip*3),int(ky-3)), 7)
    pygame.draw.circle(surf, C.INK, (int(kx),int(ky)), 13, 2)

    # calf
    draw_thick_curve(surf, C.SKIN_SHA,
        bezier2((kx,ky),(fx+flip*2,ky+25),(fx,fy)), 20)
    draw_thick_curve(surf, C.SKIN_MID,
        bezier2((kx,ky),(fx+flip*2,ky+25),(fx,fy)), 17)
    draw_thick_curve(surf, C.SKIN_LIT,
        bezier2((kx+flip*4,ky),(fx+flip*4,ky+20),(fx+flip*3,fy-4)), 10)

    # foot
    foot_pts = [
        (fx-8,fy),(fx+flip*28,fy-4),
        (fx+flip*26,fy+10),(fx-8,fy+8)
    ]
    poly(surf, C.SKIN_SHA, foot_pts)
    poly(surf, C.SKIN_MID, [(fx-6,fy-2),(fx+flip*24,fy-5),(fx+flip*22,fy+8),(fx-6,fy+6)], C.INK, 2)

    # outline legs
    draw_thick_curve(surf, C.INK,
        bezier2((hx,hy),(kx-flip*4,ky-10),(kx,ky)), 2)
    draw_thick_curve(surf, C.INK,
        bezier2((kx,ky),(fx+flip*2,ky+25),(fx,fy)), 2)


# ── static arm ────────────────────────────────────────────────────────
def draw_static_arm(surf, sx, sy):
    # back arm tucked with clenched fist toward viewer
    ex = sx - 52
    ey = sy + 38
    mx = sx - 26
    my = sy + 18
    pts = bezier2((sx,sy),(mx,my),(ex,ey))
    draw_thick_curve(surf, C.SKIN_SHA, pts, 22)
    draw_thick_curve(surf, C.SKIN_MID, pts, 18)
    draw_thick_curve(surf, C.SKIN_LIT,
        bezier2((sx-4,sy-4),(mx-4,my-6),(ex-4,ey-6)), 10)
    draw_thick_curve(surf, C.INK, pts, 2)

    # fist
    fist_c = (int(ex),int(ey))
    pygame.draw.circle(surf, C.SKIN_SHA, fist_c, 16)
    pygame.draw.circle(surf, C.SKIN_MID, fist_c, 14)
    pygame.draw.circle(surf, C.SKIN_LIT, (int(ex-4),int(ey-4)), 8)
    pygame.draw.circle(surf, C.INK, fist_c, 15, 2)
    # knuckle lines
    for ky_off in [-8,-3,3,8]:
        pygame.draw.line(surf, C.SKIN_SHA,
                         (int(ex+6),int(ey+ky_off)),
                         (int(ex+13),int(ey+ky_off)), 2)


# ── rubber arm ────────────────────────────────────────────────────────
def draw_rubber_arm(surf, sx, sy, alen):
    ex   = sx + alen
    ey   = sy
    frac = clamp(alen / ARM_MAX)
    w    = max(8, int(22 - frac*14))

    # rubbery wiggle
    wag = 0
    if state in (ST_PUNCH, ST_HOLD):
        wag = math.sin(idle_t*32)*(1-frac*0.85)*16
    cx1, cy1 = sx + alen*0.3, sy - wag*1.4
    cx2, cy2 = sx + alen*0.7, sy + wag

    pts = bezier3((sx,sy),(cx1,cy1),(cx2,cy2),(ex,ey), n=48)

    # shadow pass
    draw_thick_curve(surf, C.SKIN_SHA, pts, w+6)
    # mid skin
    draw_thick_curve(surf, C.SKIN_MID, pts, w+2)
    # lit top
    lit_pts = bezier3((sx,sy-w//3),(cx1,cy1-w//3),(cx2,cy2-w//3),(ex,ey-w//3), n=48)
    draw_thick_curve(surf, C.SKIN_LIT, lit_pts, max(3, w//2))
    # specular streak
    if w > 10:
        sp_pts = bezier3(
            (sx,sy-w//2+2),(cx1,cy1-w//2+2),(cx2,cy2-w//2+2),(ex,ey-w//2+2), n=20)
        draw_thick_curve(surf, C.SHINE, sp_pts, max(2, w//4))

    # stretch muscle lines
    if frac > 0.25:
        for i in range(1,6):
            t0 = i * 0.16
            if t0 >= 1: break
            idx = int(t0*48)
            if idx < len(pts):
                px, py = pts[idx]
                perp_off = w*0.45
                pygame.draw.line(surf, C.SKIN_DRK,
                    (int(px), int(py-perp_off)),
                    (int(px), int(py+perp_off)), 2)

    # ink outline
    draw_thick_curve(surf, C.INK, pts, 2)

    # FIST ────────────────────────────────────
    fist_r = 16 + int(frac*5)
    fc = (int(ex), int(ey))
    # shadow
    pygame.draw.circle(surf, C.SKIN_SHA, (fc[0]+3,fc[1]+4), fist_r+2)
    # base
    pygame.draw.circle(surf, C.SKIN_MID, fc, fist_r+1)
    # lit
    pygame.draw.circle(surf, C.SKIN_LIT, fc, fist_r-1)
    # specular
    gfxdraw.filled_circle(surf, fc[0]-fist_r//3, fc[1]-fist_r//3,
                           max(2,fist_r//3), (*C.SHINE, 200))
    # knuckles
    for koff in [-10,-4,4,10]:
        kx_ = int(ex + fist_r*0.55)
        ky_ = int(ey + koff)
        pygame.draw.line(surf, C.SKIN_SHA, (kx_,ky_),(kx_+int(fist_r*0.42),ky_), 2)
    # ink outline
    pygame.draw.circle(surf, C.INK, fc, fist_r+1, 3)

    return ex, ey


# ── hat string ────────────────────────────────────────────────────────
def draw_hat_string(surf, hx, hy):
    if state not in (ST_PUNCH, ST_HOLD, ST_RET): return
    t = 1.0 if state in (ST_PUNCH,ST_HOLD) else clamp(1-st_timer/T_RET)
    pts = bezier2((hx,hy),(hx-55,hy-28),(hx-120,hy-8), n=20)
    s = pygame.Surface((W,H), pygame.SRCALPHA)
    for i in range(len(pts)-1):
        alpha = int(t*200)
        pygame.draw.line(s, (*C.HAT_BAND,alpha),
            (int(pts[i][0]),int(pts[i][1])),
            (int(pts[i+1][0]),int(pts[i+1][1])), 2)
    surf.blit(s,(0,0))


# ── impact star ───────────────────────────────────────────────────────
def draw_impact(surf, fx, fy):
    if state != ST_HOLD: return
    pulse = 1 + 0.08*math.sin(idle_t*40)
    outer = 65*pulse
    inner = 24
    spikes = 12
    pts = []
    for i in range(spikes*2):
        ang = (i/(spikes*2))*math.pi*2 - math.pi/2
        r   = outer if i%2==0 else inner
        pts.append((fx+math.cos(ang)*r, fy+math.sin(ang)*r))
    # glow layers
    for glow_r, glow_a in [(85,30),(70,55),(55,80)]:
        s = pygame.Surface((W,H), pygame.SRCALPHA)
        gfxdraw.filled_circle(s, int(fx), int(fy), int(glow_r*pulse),
                              (*C.IMPACT_YLW, glow_a))
        surf.blit(s,(0,0))
    # star
    poly(surf, C.IMPACT_YLW, pts)
    poly(surf, C.IMPACT_ORG, pts, C.INK, 3)
    # white core
    pygame.draw.circle(surf, C.WHITE, (int(fx),int(fy)), 18)
    pygame.draw.circle(surf, C.IMPACT_ORG,(int(fx),int(fy)), 18, 3)

    # IMPACT text – manga style
    try:
        font_big = pygame.font.SysFont("Arial Black, Impact, Arial", 42, bold=True)
        font_sub = pygame.font.SysFont("Arial Black, Impact, Arial", 22, bold=True)
    except:
        font_big = pygame.font.SysFont(None, 52, bold=True)
        font_sub = pygame.font.SysFont(None, 28, bold=True)

    def outlined_text(surf, txt, font, color, outline_col, x, y, angle=0):
        ts = font.render(txt, True, color)
        to = font.render(txt, True, outline_col)
        ts = pygame.transform.rotate(ts, angle)
        to = pygame.transform.rotate(to, angle)
        for dx2,dy2 in [(-2,0),(2,0),(0,-2),(0,2),(-2,-2),(2,-2),(-2,2),(2,2)]:
            surf.blit(to,(x+dx2, y+dy2))
        surf.blit(ts,(x,y))

    outlined_text(surf,"GOMU GOMU no", font_sub, C.IMPACT_YLW, C.KANJI_RED,
                  int(fx+outer+10), int(fy-36), -8)
    outlined_text(surf,"PISTOL!!!", font_big, C.WHITE, C.KANJI_RED,
                  int(fx+outer+4), int(fy-6), -5)


# ── ground shadow ─────────────────────────────────────────────────────
def draw_shadow(surf, cx, cy):
    s = pygame.Surface((W,H), pygame.SRCALPHA)
    gfxdraw.filled_ellipse(s, int(cx+8), int(cy), 68, 12, (40,30,20,50))
    surf.blit(s,(0,0))


# ── UI ────────────────────────────────────────────────────────────────
def draw_ui(surf):
    try:
        ufont = pygame.font.SysFont("Arial", 17)
    except:
        ufont = pygame.font.SysFont(None, 20)

    hint = ufont.render("SPACE / Click → Gomu Gomu no PISTOL!      ESC/Q → Quit", True, (100,88,70))
    surf.blit(hint,(16, H-30))

    state_names = {ST_IDLE:"idle",ST_WIND:"wind-up",ST_PUNCH:"PUNCH!",
                   ST_HOLD:"HOLD",ST_RET:"retract"}
    st_surf = ufont.render(f"State: {state_names.get(state,'?')}", True, (130,110,80))
    surf.blit(st_surf,(16,12))


# ═══════════════════════════════════════════════════════════════════════
#  MASTER DRAW
# ═══════════════════════════════════════════════════════════════════════
def draw_scene():
    # world surface (shaken)
    world = pygame.Surface((W,H))
    draw_bg(world)
    draw_radial_speedlines(world)

    # sprite layer with alpha for particles
    sprite = pygame.Surface((W,H), pygame.SRCALPHA)

    # compute body position
    bob = math.sin(idle_t*2.0)*5 if state==ST_IDLE else 0
    bx, by = BX, BY + int(bob)
    hx, hy = bx-5, by-84
    shr = (bx+32, by-52)   # right shoulder (punching)
    shl = (bx-30, by-50)   # left shoulder  (static)
    hipy= by+46

    # draw order: back→front
    draw_shadow(world, bx, by+130)

    # back leg
    draw_leg(world, bx-14, hipy, -1, bob)
    # torso
    draw_torso(world, bx, by)
    # shorts
    draw_shorts(world, bx, by+46)
    # front leg
    draw_leg(world, bx+14, hipy,  1, -bob*0.5)
    # back arm
    draw_static_arm(world, shl[0], shl[1])
    # head (hair first, then face)
    draw_hair(world, hx, hy)
    draw_face(world, hx, hy)
    # hat string
    draw_hat_string(world, hx+18, hy-82)
    # hat
    draw_hat(world, hx, hy-42+int(bob*0.4))
    # rubber arm on top
    fx, fy = draw_rubber_arm(world, shr[0], shr[1], arm_len)
    # impact effect
    draw_impact(world, fx, fy)

    # particles
    for p in particles: p.draw(world)
    for sl in speed_lines: sl.draw(world)

    draw_ui(world)

    # screen shake blit
    screen.blit(world, (int(shake[0]), int(shake[1])))


# ═══════════════════════════════════════════════════════════════════════
#  MAIN LOOP
# ═══════════════════════════════════════════════════════════════════════
def main():
    global state, st_timer
    last = pygame.time.get_ticks()

    while True:
        now = pygame.time.get_ticks()
        dt  = min((now - last)/1000.0, 0.05)
        last = now

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.quit(); sys.exit()
                if ev.key == pygame.K_SPACE:
                    trigger()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                trigger()

        update(dt)
        draw_scene()
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()