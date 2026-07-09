"""
Angry Birds Sprite Sheet Loader
================================
Loads individual bird sprites from the angry_birds.png sprite sheet.

Sprite sheet layout (top to bottom):
  Row 1  - Red Bird      (5 animation frames)
  Row 2  - Blue Bird     (5 animation frames)
  Row 3  - Chuck/Yellow  (5 animation frames)
  Row 4  - Bomb/Black    (8 animation frames, incl. heat-up sequence)
  Row 5  - Matilda/White (6 animation frames)
  Row 6  - Hal/Green     (7 animation frames)
  Row 7  - Terence/Big   (1 large + 4 small side frames)
  Row 8  - Orange Bird   (4 frames) + Stella/Pink (4 frames)

Usage:
    sprites = BirdSpriteSheet("angry_birds.png")

    # Get all frames for a bird
    red_frames = sprites.get_bird("red")       # list of pygame.Surface

    # Get a single frame
    chuck_frame_0 = sprites.get_frame("chuck", 0)

    # Get at a custom display size
    big_red = sprites.get_frame("red", 0, scale=(100, 100))

    # Draw in your game loop
    screen.blit(red_frames[0], (x, y))
"""

import pygame
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Sprite coordinates — (x0, y0, x1, y1) pixel rectangles in the sheet
# Measured directly from the PNG (799 × 1169 px).
# ---------------------------------------------------------------------------

PAD = 2   # 2-pixel safety margin around each sprite

_RAW: dict[str, list[tuple[int, int, int, int]]] = {
    # --- Row 1: Red Bird (5 frames) ---
    "red": [
        (185, 34, 247, 96),
        (259, 34, 321, 96),
        (333, 34, 395, 96),
        (406, 34, 468, 96),
        (474, 34, 541, 96),
    ],

    # --- Row 2: Blue Bird (5 frames) ---
    "blue": [
        (218, 139, 259, 180),
        (277, 139, 318, 180),
        (340, 139, 380, 180),
        (404, 139, 445, 180),
        (462, 139, 505, 180),
    ],

    # --- Row 3: Chuck / Yellow Bird (5 frames) ---
    "chuck": [
        (188, 208, 266, 282),
        (264, 208, 342, 282),
        (339, 208, 416, 282),
        (417, 208, 493, 282),
        (493, 208, 572, 282),
    ],

    # --- Row 4: Bomb / Black Bird (8 frames, last 2 are heated/exploding) ---
    "bomb": [
        (119, 306, 184, 406),
        (194, 306, 259, 406),
        (267, 306, 331, 406),
        (336, 306, 401, 406),
        (411, 306, 477, 406),
        (486, 306, 550, 406),
        (558, 306, 622, 406),
        (626, 306, 691, 406),
    ],

    # --- Row 5: Matilda / White Bird (6 frames) ---
    "matilda": [
        (143, 432, 226, 540),
        (230, 432, 312, 540),
        (315, 432, 396, 540),
        (402, 432, 484, 540),
        (499, 432, 559, 540),
        (566, 432, 651, 540),
    ],

    # --- Row 6: Hal / Green Boomerang Bird (7 frames) ---
    "hal": [
        (411, 551, 493, 639),   # frame 0: idle / tucked
        ( 88, 551, 183, 756),   # frame 1: full body with wing spread
        (192, 551, 288, 756),   # frame 2
        (301, 551, 398, 756),   # frame 3
        (501, 551, 622, 756),   # frame 4
        (514, 551, 613, 756),   # frame 5
        (632, 551, 728, 756),   # frame 6
    ],

    # --- Row 7: Terence / Big Red Bird ---
    # Frame 0 is the giant Terence; frames 1-4 are the small detail sprites
    "terence": [
        (361, 765, 683, 1054),   # large Terence
        (114, 988, 170, 1051),   # small side sprite 1
        (174, 988, 230, 1051),   # small side sprite 2
        (233, 988, 287, 1051),   # small side sprite 3
        (293, 988, 347, 1051),   # small side sprite 4
    ],

    # --- Row 8a: Orange Bird / Bubbles (4 frames, pre-inflate) ---
    "orange": [
        ( 98, 1088, 155, 1141),
        (167, 1088, 225, 1141),
        (236, 1088, 294, 1141),
        (308, 1088, 366, 1141),
    ],

    # --- Row 8b: Stella / Pink Bird (4 frames) ---
    "stella": [
        (382, 1088, 444, 1149),
        (456, 1088, 518, 1149),
        (530, 1088, 592, 1149),
        (602, 1088, 665, 1149),
    ],

    # The large inflated Orange Bird sits in the Terence row visually;
    # it's the big orange circle at ~(361,765)-(683,1054). That entire region
    # is captured by terence[0], so if you need only the orange balloon you
    # can crop it separately.  We leave that to the caller.
}


def _apply_padding(
    rects: list[tuple[int, int, int, int]],
    pad: int,
    sheet_w: int,
    sheet_h: int,
) -> list[tuple[int, int, int, int]]:
    out = []
    for x0, y0, x1, y1 in rects:
        out.append((
            max(0, x0 - pad),
            max(0, y0 - pad),
            min(sheet_w, x1 + pad),
            min(sheet_h, y1 + pad),
        ))
    return out


# ---------------------------------------------------------------------------

@dataclass
class BirdSpriteSheet:
    """
    Load and slice the Angry Birds sprite sheet into individual surfaces.

    Parameters
    ----------
    path : str
        File path to angry_birds.png.
    padding : int
        Extra pixels to include around each sprite boundary (default 2).
    colorkey : tuple or None
        If provided, set as the colorkey for transparency (e.g. (255,255,255)).
        Leave as None to keep the PNG's built-in alpha channel.
    """

    path: str
    padding: int = PAD
    colorkey: Optional[tuple[int, int, int]] = None

    _sheet: pygame.Surface = field(init=False, repr=False)
    _cache: dict[str, list[pygame.Surface]] = field(
        init=False, repr=False, default_factory=dict
    )

    # ------------------------------------------------------------------
    def __post_init__(self) -> None:
        self._sheet = pygame.image.load(self.path).convert_alpha()
        w, h = self._sheet.get_size()
        self._rects: dict[str, list[tuple[int, int, int, int]]] = {
            name: _apply_padding(coords, self.padding, w, h)
            for name, coords in _RAW.items()
        }

    # ------------------------------------------------------------------
    def _extract(self, rect: tuple[int, int, int, int]) -> pygame.Surface:
        x0, y0, x1, y1 = rect
        surface = pygame.Surface((x1 - x0, y1 - y0), pygame.SRCALPHA)
        surface.blit(self._sheet, (0, 0), pygame.Rect(x0, y0, x1 - x0, y1 - y0))
        if self.colorkey is not None:
            surface.set_colorkey(self.colorkey)
        return surface

    # ------------------------------------------------------------------
    def get_bird(self, name: str) -> list[pygame.Surface]:
        """
        Return all animation frames for a bird as a list of surfaces.

        Parameters
        ----------
        name : str
            One of: 'red', 'blue', 'chuck', 'bomb', 'matilda',
                    'hal', 'terence', 'orange', 'stella'
        """
        name = name.lower()
        if name not in self._rects:
            raise KeyError(
                f"Unknown bird '{name}'. "
                f"Valid names: {list(self._rects.keys())}"
            )
        if name not in self._cache:
            self._cache[name] = [
                self._extract(r) for r in self._rects[name]
            ]
        return self._cache[name]

    # ------------------------------------------------------------------
    def get_frame(
        self,
        name: str,
        frame: int = 0,
        scale: Optional[tuple[int, int]] = None,
    ) -> pygame.Surface:
        """
        Return a single animation frame, optionally rescaled.

        Parameters
        ----------
        name : str
            Bird name (see get_bird).
        frame : int
            Frame index (0-based).
        scale : (width, height) or None
            If given, the surface is scaled to this size before returning.
        """
        surf = self.get_bird(name)[frame]
        if scale is not None:
            surf = pygame.transform.smoothscale(surf, scale)
        return surf

    # ------------------------------------------------------------------
    @property
    def bird_names(self) -> list[str]:
        """All available bird names."""
        return list(self._rects.keys())

    # ------------------------------------------------------------------
    def frame_count(self, name: str) -> int:
        """Number of animation frames for the given bird."""
        return len(self._rects[name.lower()])


# ---------------------------------------------------------------------------
# Demo: display all birds in a scrollable window
# ---------------------------------------------------------------------------

def run_demo(sprite_path: str = "images/angry_birds.png") -> None:
    pygame.init()
    screen = pygame.display.set_mode((900, 600))
    pygame.display.set_caption("Angry Birds Sprite Viewer")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 14)

    sprites = BirdSpriteSheet(sprite_path)

    SCALE = 64   # display every frame at this height
    MARGIN = 12
    BG = (40, 40, 40)
    LABEL_COLOR = (220, 220, 100)

    # Build a flat list of (label, surface)
    all_frames: list[tuple[str, pygame.Surface]] = []
    for name in sprites.bird_names:
        frames = sprites.get_bird(name)
        for i, surf in enumerate(frames):
            h = surf.get_height() or 1
            scaled = pygame.transform.smoothscale(
                surf, (int(surf.get_width() * SCALE / h), SCALE)
            )
            all_frames.append((f"{name}[{i}]", scaled))

    scroll_y = 0
    max_scroll = 0

    # Layout into rows
    ROW_HEIGHT = SCALE + 40
    COLS = 8
    rows = [all_frames[i : i + COLS] for i in range(0, len(all_frames), COLS)]
    total_height = len(rows) * ROW_HEIGHT + MARGIN * 2
    max_scroll = max(0, total_height - 600)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if event.type == pygame.MOUSEWHEEL:
                scroll_y = max(0, min(max_scroll, scroll_y - event.y * 30))

        screen.fill(BG)

        for row_i, row in enumerate(rows):
            y = MARGIN + row_i * ROW_HEIGHT - scroll_y
            if y + ROW_HEIGHT < 0 or y > 600:
                continue
            x = MARGIN
            for label, surf in row:
                screen.blit(surf, (x, y))
                lbl = font.render(label, True, LABEL_COLOR)
                screen.blit(lbl, (x, y + SCALE + 4))
                x += surf.get_width() + MARGIN

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "images/angry_birds.png"
    run_demo(path)