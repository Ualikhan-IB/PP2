import pygame
import sys

pygame.init()

# Window
WIN_W, WIN_H = 900, 640
NAV_H = 64  # toolbar height

screen = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("Paint")
clock = pygame.time.Clock()
ui_font = pygame.font.SysFont("Arial", 14, bold=True)

# Canvas surface (below toolbar)
drawing_surface = pygame.Surface((WIN_W, WIN_H - NAV_H))
drawing_surface.fill((255, 255, 255))

# UI colors
C_NAV_BG   = (40, 40, 50)
C_SELECTED = (80, 140, 220)
C_BORDER   = (100, 100, 110)
C_TEXT     = (220, 220, 220)

# 18-color palette
COLORS = [
    (  0,   0,   0), (255, 255, 255), (128, 128, 128), (192, 192, 192),
    (255,   0,   0), (128,   0,   0), (255, 128,   0), (128,  64,   0),
    (255, 255,   0), (128, 128,   0), (  0, 255,   0), (  0, 128,   0),
    (  0, 255, 255), (  0, 128, 128), (  0,   0, 255), (  0,   0, 128),
    (255,   0, 255), (128,   0, 128),
]

PEN    = "pen"
RECT   = "rect"
CIRCLE = "circle"
ERASER = "eraser"


class Button:
    def __init__(self, x, y, w, h, text, tool_id):
        self.area    = pygame.Rect(x, y, w, h)
        self.text    = text
        self.tool_id = tool_id

    def render(self, surface, active):
        # Blue if active, dark otherwise
        bg = C_SELECTED if self.tool_id == active else C_NAV_BG
        pygame.draw.rect(surface, bg, self.area, border_radius=6)
        pygame.draw.rect(surface, C_BORDER, self.area, 1, border_radius=6)
        label = ui_font.render(self.text, True, C_TEXT)
        surface.blit(label, (
            self.area.centerx - label.get_width() // 2,
            self.area.centery - label.get_height() // 2
        ))

    def hit(self, pos):
        return self.area.collidepoint(pos)


tool_buttons = [
    Button(10,  12, 70, 40, "Pen",    PEN),
    Button(88,  12, 70, 40, "Rect",   RECT),
    Button(166, 12, 70, 40, "Circle", CIRCLE),
    Button(244, 12, 70, 40, "Eraser", ERASER),
]

# Palette grid: 2 rows x 9 cols
sw = 24
pal_x0 = 460
palette_rects = []
for i in range(len(COLORS)):
    col_i = i % 9
    row_i = i // 9
    r = pygame.Rect(pal_x0 + col_i * (sw + 3), 8 + row_i * (sw + 4), sw, sw)
    palette_rects.append(r)

size_plus     = pygame.Rect(385, 28, 28, 22)
size_minus    = pygame.Rect(418, 28, 28, 22)
btn_clear     = pygame.Rect(WIN_W - 80, 15, 70, 34)
color_preview = pygame.Rect(330, 10, 44, 44)


def draw_toolbar(active_tool, active_color, brush_sz):
    pygame.draw.rect(screen, C_NAV_BG, (0, 0, WIN_W, NAV_H))
    for btn in tool_buttons:
        btn.render(screen, active_tool)
    # Selected color box
    pygame.draw.rect(screen, active_color, color_preview, border_radius=4)
    pygame.draw.rect(screen, C_TEXT, color_preview, 2, border_radius=4)
    # Size label and +/- buttons
    screen.blit(ui_font.render(f"Size: {brush_sz}", True, C_TEXT), (385, 10))
    pygame.draw.rect(screen, C_BORDER, size_plus,  border_radius=4)
    pygame.draw.rect(screen, C_BORDER, size_minus, border_radius=4)
    screen.blit(ui_font.render("+", True, C_TEXT), (size_plus.centerx  - 4, size_plus.centery  - 8))
    screen.blit(ui_font.render("-", True, C_TEXT), (size_minus.centerx - 4, size_minus.centery - 8))
    # Palette swatches
    for i, r in enumerate(palette_rects):
        pygame.draw.rect(screen, COLORS[i], r, border_radius=3)
        pygame.draw.rect(screen, C_BORDER, r, 1, border_radius=3)
    # Clear button
    pygame.draw.rect(screen, (180, 40, 40), btn_clear, border_radius=6)
    screen.blit(ui_font.render("Clear", True, C_TEXT),
                (btn_clear.centerx - 18, btn_clear.centery - 8))


def to_canvas(mx, my):
    # Screen -> canvas coordinates
    return mx, my - NAV_H


# App state
tool      = PEN
color     = COLORS[0]
size      = 5
pressing  = False
drag_from = None  # drag start for shape tools
snap      = None  # canvas backup before shape draw


def toolbar_click(mx, my):
    global tool, color, size
    for btn in tool_buttons:
        if btn.hit((mx, my)):
            tool = btn.tool_id
            return
    for i, r in enumerate(palette_rects):
        if r.collidepoint(mx, my):
            color = COLORS[i]
            return
    if size_plus.collidepoint(mx, my):
        size = min(60, size + 1)
    elif size_minus.collidepoint(mx, my):
        size = max(1, size - 1)
    elif btn_clear.collidepoint(mx, my):
        drawing_surface.fill((255, 255, 255))


def paint_dot(mx, my):
    cx, cy = to_canvas(mx, my)
    pygame.draw.circle(drawing_surface, color, (cx, cy), size)


def erase_dot(mx, my):
    cx, cy = to_canvas(mx, my)
    # Eraser is 3x the pen size
    pygame.draw.circle(drawing_surface, (255, 255, 255), (cx, cy), size * 3)


def update_shape(end_x, end_y):
    # Restore snapshot, draw fresh preview on top
    if snap:
        drawing_surface.blit(snap, (0, 0))
    ex, ey = to_canvas(end_x, end_y)
    sx, sy = drag_from
    if tool == RECT:
        r = pygame.Rect(min(sx, ex), min(sy, ey), abs(ex - sx), abs(ey - sy))
        pygame.draw.rect(drawing_surface, color, r, size)
    elif tool == CIRCLE:
        cx = (sx + ex) // 2
        cy = (sy + ey) // 2
        rx = abs(ex - sx) // 2
        ry = abs(ey - sy) // 2
        if rx > 0 and ry > 0:
            pygame.draw.ellipse(drawing_surface, color,
                                (cx - rx, cy - ry, rx * 2, ry * 2), size)


# Main loop
while True:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if my < NAV_H:
                toolbar_click(mx, my)
            else:
                pressing  = True
                drag_from = to_canvas(mx, my)
                if tool in (RECT, CIRCLE):
                    snap = drawing_surface.copy()  # save before shape
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if pressing and drag_from and tool in (RECT, CIRCLE):
                update_shape(*event.pos)  # commit shape
            pressing  = False
            drag_from = None
            snap      = None
        elif event.type == pygame.MOUSEMOTION and pressing:
            mx, my = event.pos
            if my >= NAV_H:
                if tool == PEN:
                    paint_dot(mx, my)
                elif tool == ERASER:
                    erase_dot(mx, my)
                elif tool in (RECT, CIRCLE):
                    update_shape(mx, my)  # live preview

    screen.blit(drawing_surface, (0, NAV_H))
    draw_toolbar(tool, color, size)
    pygame.display.flip()