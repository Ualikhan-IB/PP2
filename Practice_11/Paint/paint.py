import pygame
import sys
import math

pygame.init()

# ─────────────────────────────────────────────
#  WINDOW & CANVAS SETUP
# ─────────────────────────────────────────────
WIN_W, WIN_H = 900, 640
NAV_H        = 64          # height of the top toolbar

screen = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("Paint – Extended")
clock    = pygame.time.Clock()
ui_font  = pygame.font.SysFont("Arial", 13, bold=True)

# Canvas is a separate surface drawn below the toolbar.
# We draw shapes onto this, not directly onto the screen.
drawing_surface = pygame.Surface((WIN_W, WIN_H - NAV_H))
drawing_surface.fill((255, 255, 255))

# ─────────────────────────────────────────────
#  UI COLOURS
# ─────────────────────────────────────────────
C_NAV_BG   = (40,  40,  50)    # toolbar background
C_SELECTED = (80,  140, 220)   # highlight for the active tool button
C_BORDER   = (100, 100, 110)   # button / swatch border
C_TEXT     = (220, 220, 220)   # button label text

# ─────────────────────────────────────────────
#  COLOUR PALETTE  (18 swatches, 2 rows × 9 cols)
# ─────────────────────────────────────────────
COLORS = [
    (  0,   0,   0), (255, 255, 255), (128, 128, 128), (192, 192, 192),
    (255,   0,   0), (128,   0,   0), (255, 128,   0), (128,  64,   0),
    (255, 255,   0), (128, 128,   0), (  0, 255,   0), (  0, 128,   0),
    (  0, 255, 255), (  0, 128, 128), (  0,   0, 255), (  0,   0, 128),
    (255,   0, 255), (128,   0, 128),
]

# ─────────────────────────────────────────────
#  TOOL IDENTIFIERS
# ─────────────────────────────────────────────
PEN       = "pen"
RECT      = "rect"
CIRCLE    = "circle"
ERASER    = "eraser"
SQUARE    = "square"       # Task 1 – axis-aligned square
RTRI      = "rtri"         # Task 2 – right triangle
EQTRI     = "eqtri"        # Task 3 – equilateral triangle
RHOMBUS   = "rhombus"      # Task 4 – rhombus (diamond)


# ─────────────────────────────────────────────
#  BUTTON WIDGET
# ─────────────────────────────────────────────
class Button:
    """A simple clickable toolbar button that highlights when its tool is active."""

    def __init__(self, x, y, w, h, text, tool_id):
        self.area    = pygame.Rect(x, y, w, h)
        self.text    = text
        self.tool_id = tool_id

    def render(self, surface, active_tool):
        """Draw button; blue background when this tool is selected."""
        bg = C_SELECTED if self.tool_id == active_tool else C_NAV_BG
        pygame.draw.rect(surface, bg,       self.area, border_radius=6)
        pygame.draw.rect(surface, C_BORDER, self.area, 1, border_radius=6)
        label = ui_font.render(self.text, True, C_TEXT)
        surface.blit(label, (
            self.area.centerx - label.get_width()  // 2,
            self.area.centery - label.get_height() // 2,
        ))

    def hit(self, pos):
        """Return True if pos is inside this button."""
        return self.area.collidepoint(pos)


# ─────────────────────────────────────────────
#  TOOL BUTTONS  (two rows to fit all 8 tools)
# ─────────────────────────────────────────────
# Row 1 – original tools
tool_buttons = [
    Button( 10, 4,  62, 26, "Pen",    PEN),
    Button( 76, 4,  62, 26, "Rect",   RECT),
    Button(142, 4,  62, 26, "Circle", CIRCLE),
    Button(208, 4,  62, 26, "Eraser", ERASER),
    # Row 2 – new shape tools (Tasks 1-4)
    Button( 10, 34, 62, 26, "Square", SQUARE),
    Button( 76, 34, 70, 26, "R.Tri",  RTRI),
    Button(150, 34, 70, 26, "Eq.Tri", EQTRI),
    Button(224, 34, 74, 26, "Rhombus",RHOMBUS),
]

# ─────────────────────────────────────────────
#  PALETTE GRID  (2 rows × 9 swatches)
# ─────────────────────────────────────────────
sw     = 22     # swatch size in pixels
pal_x0 = 462    # x origin of the palette grid
palette_rects = []
for i in range(len(COLORS)):
    col_i = i % 9
    row_i = i // 9
    r = pygame.Rect(pal_x0 + col_i * (sw + 3), 6 + row_i * (sw + 4), sw, sw)
    palette_rects.append(r)

# ─────────────────────────────────────────────
#  TOOLBAR CONTROL RECTS
# ─────────────────────────────────────────────
size_plus     = pygame.Rect(310, 28, 26, 22)    # brush size +
size_minus    = pygame.Rect(340, 28, 26, 22)    # brush size −
btn_clear     = pygame.Rect(WIN_W - 80, 15, 70, 34)   # clear canvas
color_preview = pygame.Rect(302,  4,  36, 36)   # active colour box
size_label_y  = 10   # y position of the "Size:" label


# ─────────────────────────────────────────────
#  TOOLBAR DRAW
# ─────────────────────────────────────────────
def draw_toolbar(active_tool, active_color, brush_sz):
    """Render the entire toolbar: background, buttons, palette, controls."""
    # Background bar
    pygame.draw.rect(screen, C_NAV_BG, (0, 0, WIN_W, NAV_H))

    # Tool buttons
    for btn in tool_buttons:
        btn.render(screen, active_tool)

    # Active colour preview box
    pygame.draw.rect(screen, active_color, color_preview, border_radius=4)
    pygame.draw.rect(screen, C_TEXT,       color_preview, 2, border_radius=4)

    # Brush size label and ± buttons
    screen.blit(ui_font.render(f"Sz:{brush_sz}", True, C_TEXT), (302, size_label_y))
    pygame.draw.rect(screen, C_BORDER, size_plus,  border_radius=4)
    pygame.draw.rect(screen, C_BORDER, size_minus, border_radius=4)
    screen.blit(ui_font.render("+", True, C_TEXT),
                (size_plus.centerx  - 4, size_plus.centery  - 8))
    screen.blit(ui_font.render("-", True, C_TEXT),
                (size_minus.centerx - 4, size_minus.centery - 8))

    # Palette swatches
    for i, r in enumerate(palette_rects):
        pygame.draw.rect(screen, COLORS[i], r, border_radius=3)
        pygame.draw.rect(screen, C_BORDER,  r, 1, border_radius=3)

    # Clear canvas button
    pygame.draw.rect(screen, (180, 40, 40), btn_clear, border_radius=6)
    screen.blit(ui_font.render("Clear", True, C_TEXT),
                (btn_clear.centerx - 18, btn_clear.centery - 7))


# ─────────────────────────────────────────────
#  COORDINATE HELPER
# ─────────────────────────────────────────────
def to_canvas(mx, my):
    """Convert screen mouse position → canvas-local coordinates (subtract toolbar)."""
    return mx, my - NAV_H


# ─────────────────────────────────────────────
#  APPLICATION STATE
# ─────────────────────────────────────────────
tool      = PEN
color     = COLORS[0]   # default: black
size      = 5           # brush/outline thickness in pixels
pressing  = False       # True while left mouse button is held
drag_from = None        # canvas-coords of the drag start point
snap      = None        # copy of canvas saved before shape preview begins


# ─────────────────────────────────────────────
#  TOOLBAR CLICK HANDLER
# ─────────────────────────────────────────────
def toolbar_click(mx, my):
    """Handle a click anywhere in the toolbar area."""
    global tool, color, size

    # Tool buttons
    for btn in tool_buttons:
        if btn.hit((mx, my)):
            tool = btn.tool_id
            return

    # Palette swatches
    for i, r in enumerate(palette_rects):
        if r.collidepoint(mx, my):
            color = COLORS[i]
            return

    # Brush size controls
    if size_plus.collidepoint(mx, my):
        size = min(60, size + 1)
    elif size_minus.collidepoint(mx, my):
        size = max(1, size - 1)

    # Clear canvas
    elif btn_clear.collidepoint(mx, my):
        drawing_surface.fill((255, 255, 255))


# ─────────────────────────────────────────────
#  FREEHAND DRAW / ERASE
# ─────────────────────────────────────────────
def paint_dot(mx, my):
    """Stamp a filled circle at the current mouse position (pen tool)."""
    cx, cy = to_canvas(mx, my)
    pygame.draw.circle(drawing_surface, color, (cx, cy), size)


def erase_dot(mx, my):
    """Stamp a white circle (3× pen size) to erase at the current position."""
    cx, cy = to_canvas(mx, my)
    pygame.draw.circle(drawing_surface, (255, 255, 255), (cx, cy), size * 3)


# ─────────────────────────────────────────────
#  SHAPE HELPERS
# ─────────────────────────────────────────────
def _right_tri_points(sx, sy, ex, ey):
    """
    Compute the three vertices of a right triangle.
    The right angle is at the drag-start corner (sx, sy).
    The two legs run horizontally to (ex, sy) and vertically to (sx, ey).
    """
    return [(sx, sy), (ex, sy), (sx, ey)]


def _eq_tri_points(sx, sy, ex, ey):
    """
    Compute the three vertices of an equilateral triangle.
    The base runs from drag-start to the right along the x-axis;
    base length = horizontal drag distance.  The apex is above the midpoint
    at height = base × (√3 / 2) so all three sides are equal.
    """
    base   = abs(ex - sx)           # length of the base
    # Midpoint of the base (apex hangs above/below based on drag direction)
    mid_x  = (sx + ex) / 2
    # Height of equilateral triangle: h = base * sqrt(3)/2
    height = base * math.sqrt(3) / 2
    # Apex goes above if we dragged rightward, below otherwise
    apex_y = sy - height if ex >= sx else sy + height
    return [(sx, sy), (ex, sy), (int(mid_x), int(apex_y))]


def _rhombus_points(sx, sy, ex, ey):
    """
    Compute the four vertices of an axis-aligned rhombus (diamond).
    The bounding box is defined by the drag rectangle.
    Vertices are placed at the midpoints of each side of that box.
    """
    cx = (sx + ex) // 2   # horizontal centre
    cy = (sy + ey) // 2   # vertical centre
    return [
        (cx, sy),   # top
        (ex, cy),   # right
        (cx, ey),   # bottom
        (sx, cy),   # left
    ]


# ─────────────────────────────────────────────
#  SHAPE PREVIEW  (called on MOUSEMOTION + MOUSEUP)
# ─────────────────────────────────────────────
def update_shape(end_x, end_y):
    """
    Restore the pre-drag canvas snapshot, then draw the current shape
    preview on top.  Called continuously during drag for live feedback,
    and once on mouse-up to commit the final shape.
    """
    if snap:
        drawing_surface.blit(snap, (0, 0))   # restore clean canvas

    ex, ey = to_canvas(end_x, end_y)
    sx, sy = drag_from   # drag-start in canvas coordinates

    if tool == RECT:
        # Axis-aligned rectangle – any aspect ratio
        r = pygame.Rect(min(sx, ex), min(sy, ey), abs(ex - sx), abs(ey - sy))
        pygame.draw.rect(drawing_surface, color, r, size)

    elif tool == SQUARE:
        # ── Task 1: Square ────────────────────────────────────────
        # Force equal width and height using the smaller of the two drags.
        # Direction is preserved (drag left/up shrinks the same way).
        side  = min(abs(ex - sx), abs(ey - sy))
        sign_x = 1 if ex >= sx else -1
        sign_y = 1 if ey >= sy else -1
        r = pygame.Rect(
            min(sx, sx + sign_x * side),
            min(sy, sy + sign_y * side),
            side, side
        )
        pygame.draw.rect(drawing_surface, color, r, size)

    elif tool == CIRCLE:
        # Ellipse inscribed in the drag bounding box
        cx = (sx + ex) // 2
        cy = (sy + ey) // 2
        rx = abs(ex - sx) // 2
        ry = abs(ey - sy) // 2
        if rx > 0 and ry > 0:
            pygame.draw.ellipse(drawing_surface, color,
                                (cx - rx, cy - ry, rx * 2, ry * 2), size)

    elif tool == RTRI:
        # ── Task 2: Right triangle ────────────────────────────────
        pts = _right_tri_points(sx, sy, ex, ey)
        pygame.draw.polygon(drawing_surface, color, pts, size)

    elif tool == EQTRI:
        # ── Task 3: Equilateral triangle ─────────────────────────
        pts = _eq_tri_points(sx, sy, ex, ey)
        pygame.draw.polygon(drawing_surface, color, pts, size)

    elif tool == RHOMBUS:
        # ── Task 4: Rhombus ───────────────────────────────────────
        pts = _rhombus_points(sx, sy, ex, ey)
        pygame.draw.polygon(drawing_surface, color, pts, size)


# ─────────────────────────────────────────────
#  SHAPE TOOLS THAT NEED A SNAPSHOT
# ─────────────────────────────────────────────
# All tools that show a live drag preview need to save and restore the canvas.
SHAPE_TOOLS = {RECT, SQUARE, CIRCLE, RTRI, EQTRI, RHOMBUS}


# ─────────────────────────────────────────────
#  MAIN LOOP
# ─────────────────────────────────────────────
while True:
    clock.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if my < NAV_H:
                # Click is inside the toolbar
                toolbar_click(mx, my)
            else:
                # Click is on the canvas – begin a stroke or shape drag
                pressing  = True
                drag_from = to_canvas(mx, my)
                if tool in SHAPE_TOOLS:
                    # Save the current canvas so we can redraw the preview
                    # each frame without leaving ghost shapes behind
                    snap = drawing_surface.copy()

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if pressing and drag_from and tool in SHAPE_TOOLS:
                # Commit the final shape on release
                update_shape(*event.pos)
            pressing  = False
            drag_from = None
            snap      = None   # discard snapshot after commit

        elif event.type == pygame.MOUSEMOTION and pressing:
            mx, my = event.pos
            if my >= NAV_H:   # only draw on the canvas area
                if tool == PEN:
                    paint_dot(mx, my)
                elif tool == ERASER:
                    erase_dot(mx, my)
                elif tool in SHAPE_TOOLS:
                    # Live preview: redraw shape each time mouse moves
                    update_shape(mx, my)

    # ── Render ────────────────────────────────────────────────────
    screen.blit(drawing_surface, (0, NAV_H))   # canvas below toolbar
    draw_toolbar(tool, color, size)
    pygame.display.flip()
