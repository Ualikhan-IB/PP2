"""
Paint Application - TSIS2 Complete Edition
Features: Pencil, Line, Brush Size (1/2/3), Flood Fill, Save (Ctrl+S), Text Tool
All shapes respect brush size
"""

import pygame
import sys
import math
import datetime

pygame.init()

# ==================== CONSTANTS ====================
SCREEN_W, SCREEN_H = 900, 640
TOOLBAR_H = 64

BG_CANVAS = (255, 255, 255)
BG_TOOLBAR = (40, 40, 50)
BORDER_CLR = (100, 100, 110)
BTN_BG = (60, 60, 75)
BTN_HOVER = (80, 80, 100)
BTN_ACTIVE = (80, 140, 220)
TEXT_CLR = (220, 220, 220)

# Tools
TOOL_PEN = "pen"
TOOL_LINE = "line"
TOOL_RECT = "rect"
TOOL_CIRCLE = "circle"
TOOL_SQUARE = "square"
TOOL_RTRI = "rtri"
TOOL_EQTRI = "eqtri"
TOOL_RHOMBUS = "rhombus"
TOOL_ERASER = "eraser"
TOOL_FILL = "fill"
TOOL_TEXT = "text"

# Brush sizes
BRUSH_SMALL = 2
BRUSH_MEDIUM = 5
BRUSH_LARGE = 10

# Colors
PALETTE = [
    (0, 0, 0), (255, 255, 255), (128, 128, 128), (192, 192, 192),
    (255, 0, 0), (128, 0, 0), (255, 128, 0), (128, 64, 0),
    (255, 255, 0), (128, 128, 0), (0, 255, 0), (0, 128, 0),
    (0, 255, 255), (0, 128, 128), (0, 0, 255), (0, 0, 128),
    (255, 0, 255), (128, 0, 128),
]

# ==================== SETUP ====================
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Paint - TSIS2 (Pencil, Line, Fill, Text, Save)")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 14, bold=True)
text_font = pygame.font.SysFont("Arial", 24)

canvas = pygame.Surface((SCREEN_W, SCREEN_H - TOOLBAR_H))
canvas.fill(BG_CANVAS)


# ==================== HELPER FUNCTIONS ====================
def to_canvas(x, y):
    """Convert screen to canvas coordinates"""
    return x, y - TOOLBAR_H


def save_canvas():
    """Save canvas with timestamp"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"canvas_{timestamp}.png"
    pygame.image.save(canvas, filename)
    print(f"✓ Saved as {filename}")


# ==================== FLOOD FILL ====================
def flood_fill(surface, start_pos, fill_color, tolerance=0):
    """Flood fill algorithm using stack"""
    w, h = surface.get_size()
    
    try:
        target_color = surface.get_at(start_pos)[:3]
    except IndexError:
        return
    
    if target_color == fill_color:
        return
    
    stack = [start_pos]
    visited = set()
    
    while stack:
        x, y = stack.pop()
        
        if (x, y) in visited:
            continue
        if x < 0 or x >= w or y < 0 or y >= h:
            continue
        
        try:
            current_color = surface.get_at((x, y))[:3]
        except IndexError:
            continue
        
        if current_color != target_color:
            continue
        
        surface.set_at((x, y), fill_color)
        visited.add((x, y))
        
        # Add neighbors
        stack.extend([(x+1, y), (x-1, y), (x, y+1), (x, y-1)])


# ==================== SHAPE FUNCTIONS ====================
def draw_right_triangle(surf, color, start, end, thickness):
    sx, sy = start
    ex, ey = end
    points = [(sx, sy), (ex, sy), (sx, ey)]
    if thickness == 0:
        pygame.draw.polygon(surf, color, points)
    else:
        pygame.draw.polygon(surf, color, points, thickness)


def draw_equilateral_triangle(surf, color, start, end, thickness):
    sx, sy = start
    ex, ey = end
    base = abs(ex - sx)
    mid_x = (sx + ex) / 2
    height = base * math.sqrt(3) / 2
    apex_y = sy - height if ex >= sx else sy + height
    points = [(sx, sy), (ex, sy), (int(mid_x), int(apex_y))]
    if thickness == 0:
        pygame.draw.polygon(surf, color, points)
    else:
        pygame.draw.polygon(surf, color, points, thickness)


def draw_rhombus(surf, color, start, end, thickness):
    sx, sy = start
    ex, ey = end
    cx = (sx + ex) // 2
    cy = (sy + ey) // 2
    points = [(cx, sy), (ex, cy), (cx, ey), (sx, cy)]
    if thickness == 0:
        pygame.draw.polygon(surf, color, points)
    else:
        pygame.draw.polygon(surf, color, points, thickness)


def draw_square(surf, color, start, end, thickness):
    sx, sy = start
    ex, ey = end
    side = min(abs(ex - sx), abs(ey - sy))
    sign_x = 1 if ex >= sx else -1
    sign_y = 1 if ey >= sy else -1
    rect = pygame.Rect(
        min(sx, sx + sign_x * side),
        min(sy, sy + sign_y * side),
        side, side
    )
    if thickness == 0:
        pygame.draw.rect(surf, color, rect)
    else:
        pygame.draw.rect(surf, color, rect, thickness)


# ==================== TOOLBAR ====================
class ToolButton:
    def __init__(self, x, y, w, h, text, tool_id):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.tool_id = tool_id
    
    def draw(self, screen, current_tool):
        bg = BTN_ACTIVE if self.tool_id == current_tool else BTN_BG
        pygame.draw.rect(screen, bg, self.rect, border_radius=6)
        pygame.draw.rect(screen, BORDER_CLR, self.rect, 1, border_radius=6)
        label = font.render(self.text, True, TEXT_CLR)
        screen.blit(label, (self.rect.centerx - label.get_width()//2,
                           self.rect.centery - label.get_height()//2))
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


# Tool buttons (row 1)
tool_buttons = [
    ToolButton(10, 5, 55, 26, "Pen", TOOL_PEN),
    ToolButton(70, 5, 55, 26, "Line", TOOL_LINE),
    ToolButton(130, 5, 55, 26, "Rect", TOOL_RECT),
    ToolButton(190, 5, 55, 26, "Circle", TOOL_CIRCLE),
    ToolButton(250, 5, 55, 26, "Erase", TOOL_ERASER),
    ToolButton(310, 5, 55, 26, "Fill", TOOL_FILL),
    ToolButton(370, 5, 55, 26, "Text", TOOL_TEXT),
]

# Tool buttons (row 2 - shapes)
tool_buttons_row2 = [
    ToolButton(10, 35, 55, 26, "Square", TOOL_SQUARE),
    ToolButton(70, 35, 55, 26, "R.Tri", TOOL_RTRI),
    ToolButton(130, 35, 55, 26, "Eq.Tri", TOOL_EQTRI),
    ToolButton(190, 35, 55, 26, "Rhombus", TOOL_RHOMBUS),
]

all_buttons = tool_buttons + tool_buttons_row2

# Brush size buttons
size_btn_small = pygame.Rect(460, 8, 40, 26)
size_btn_med = pygame.Rect(505, 8, 40, 26)
size_btn_large = pygame.Rect(550, 8, 40, 26)

# Clear button
clear_btn = pygame.Rect(SCREEN_W - 70, 8, 60, 50)

# Color palette
palette_rects = []
palette_x = 470
palette_y = 38
for i in range(len(PALETTE)):
    col = i % 9
    row = i // 9
    rect = pygame.Rect(palette_x + col * 22, palette_y + row * 22, 20, 20)
    palette_rects.append(rect)


def draw_toolbar(current_tool, current_color, brush_size):
    """Draw the toolbar"""
    pygame.draw.rect(screen, BG_TOOLBAR, (0, 0, SCREEN_W, TOOLBAR_H))
    
    # Draw buttons
    for btn in all_buttons:
        btn.draw(screen, current_tool)
    
    # Brush size section
    label = font.render(f"Size:", True, TEXT_CLR)
    screen.blit(label, (420, 15))
    
    # Size buttons
    colors = {BRUSH_SMALL: (BTN_ACTIVE if brush_size == BRUSH_SMALL else BTN_BG),
              BRUSH_MEDIUM: (BTN_ACTIVE if brush_size == BRUSH_MEDIUM else BTN_BG),
              BRUSH_LARGE: (BTN_ACTIVE if brush_size == BRUSH_LARGE else BTN_BG)}
    
    pygame.draw.rect(screen, colors[BRUSH_SMALL], size_btn_small, border_radius=4)
    pygame.draw.rect(screen, colors[BRUSH_MEDIUM], size_btn_med, border_radius=4)
    pygame.draw.rect(screen, colors[BRUSH_LARGE], size_btn_large, border_radius=4)
    
    screen.blit(font.render("S", True, TEXT_CLR), (475, 14))
    screen.blit(font.render("M", True, TEXT_CLR), (520, 14))
    screen.blit(font.render("L", True, TEXT_CLR), (565, 14))
    
    # Color preview
    preview_rect = pygame.Rect(610, 8, 36, 36)
    pygame.draw.rect(screen, current_color, preview_rect, border_radius=4)
    pygame.draw.rect(screen, BORDER_CLR, preview_rect, 2, border_radius=4)
    
    # Palette
    for i, rect in enumerate(palette_rects):
        pygame.draw.rect(screen, PALETTE[i], rect, border_radius=3)
        pygame.draw.rect(screen, BORDER_CLR, rect, 1, border_radius=3)
    
    # Clear button
    pygame.draw.rect(screen, (180, 40, 40), clear_btn, border_radius=6)
    clear_text = font.render("Clear", True, TEXT_CLR)
    screen.blit(clear_text, (clear_btn.centerx - 18, clear_btn.centery - 7))


# ==================== TEXT TOOL ====================
class TextInput:
    def __init__(self):
        self.active = False
        self.position = None
        self.text = ""
        self.temp_surface = None
    
    def start(self, pos):
        self.active = True
        self.position = pos
        self.text = ""
        self.save_canvas_state()
    
    def save_canvas_state(self):
        self.temp_surface = canvas.copy()
    
    def add_char(self, char):
        self.text += char
        self.update_preview()
    
    def delete_char(self):
        self.text = self.text[:-1]
        self.update_preview()
    
    def update_preview(self):
        # Restore canvas
        canvas.blit(self.temp_surface, (0, 0))
        # Draw text preview
        if self.text:
            text_surf = text_font.render(self.text, True, (0, 0, 0))
            canvas.blit(text_surf, self.position)
    
    def confirm(self, color):
        if self.text:
            text_surf = text_font.render(self.text, True, color)
            canvas.blit(text_surf, self.position)
        self.active = False
        self.text = ""
        self.temp_surface = None
    
    def cancel(self):
        if self.temp_surface:
            canvas.blit(self.temp_surface, (0, 0))
        self.active = False
        self.text = ""
        self.temp_surface = None


# ==================== MAIN LOOP ====================
def main():
    current_tool = TOOL_PEN
    current_color = (0, 0, 0)
    brush_size = BRUSH_MEDIUM
    
    drawing = False
    start_pos = None
    last_pos = None
    preview = None
    
    text_input = TextInput()
    
    while True:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Keyboard shortcuts
            if event.type == pygame.KEYDOWN:
                # Ctrl+S to save
                if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    save_canvas()
                
                # Brush size: 1,2,3
                elif event.key == pygame.K_1:
                    brush_size = BRUSH_SMALL
                elif event.key == pygame.K_2:
                    brush_size = BRUSH_MEDIUM
                elif event.key == pygame.K_3:
                    brush_size = BRUSH_LARGE
                
                # Tool shortcuts
                elif event.key == pygame.K_p:
                    current_tool = TOOL_PEN
                elif event.key == pygame.K_l:
                    current_tool = TOOL_LINE
                elif event.key == pygame.K_f:
                    current_tool = TOOL_FILL
                elif event.key == pygame.K_t:
                    current_tool = TOOL_TEXT
                
                # Text input handling
                elif text_input.active:
                    if event.key == pygame.K_RETURN:
                        text_input.confirm(current_color)
                    elif event.key == pygame.K_ESCAPE:
                        text_input.cancel()
                    elif event.key == pygame.K_BACKSPACE:
                        text_input.delete_char()
                    else:
                        # Only printable characters
                        if event.unicode and event.unicode.isprintable():
                            text_input.add_char(event.unicode)
            
            # Mouse button down
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                
                # Toolbar click
                if y < TOOLBAR_H:
                    # Tool buttons
                    for btn in all_buttons:
                        if btn.is_clicked((x, y)):
                            current_tool = btn.tool_id
                    
                    # Brush size buttons
                    if size_btn_small.collidepoint(x, y):
                        brush_size = BRUSH_SMALL
                    elif size_btn_med.collidepoint(x, y):
                        brush_size = BRUSH_MEDIUM
                    elif size_btn_large.collidepoint(x, y):
                        brush_size = BRUSH_LARGE
                    
                    # Color palette
                    for idx, rect in enumerate(palette_rects):
                        if rect.collidepoint(x, y):
                            current_color = PALETTE[idx]
                    
                    # Clear button
                    if clear_btn.collidepoint(x, y):
                        canvas.fill(BG_CANVAS)
                
                # Canvas click
                else:
                    canvas_pos = to_canvas(x, y)
                    
                    # Flood fill tool
                    if current_tool == TOOL_FILL:
                        flood_fill(canvas, canvas_pos, current_color)
                    
                    # Text tool
                    elif current_tool == TOOL_TEXT:
                        if not text_input.active:
                            text_input.start(canvas_pos)
                    
                    # Other drawing tools
                    else:
                        drawing = True
                        start_pos = canvas_pos
                        last_pos = canvas_pos
                        
                        # For pen/eraser, draw initial dot
                        if current_tool == TOOL_PEN:
                            pygame.draw.circle(canvas, current_color, canvas_pos, brush_size)
                        elif current_tool == TOOL_ERASER:
                            pygame.draw.circle(canvas, BG_CANVAS, canvas_pos, brush_size * 2)
                        
                        # Save preview state for shape tools
                        if current_tool in [TOOL_LINE, TOOL_RECT, TOOL_CIRCLE, 
                                            TOOL_SQUARE, TOOL_RTRI, TOOL_EQTRI, TOOL_RHOMBUS]:
                            preview = canvas.copy()
            
            # Mouse button up
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drawing and start_pos:
                    end_pos = to_canvas(*event.pos)
                    
                    # Draw final shape
                    if current_tool == TOOL_LINE and start_pos:
                        pygame.draw.line(canvas, current_color, start_pos, end_pos, brush_size)
                    
                    elif current_tool == TOOL_RECT and start_pos:
                        x1, y1 = start_pos
                        x2, y2 = end_pos
                        rect = pygame.Rect(min(x1, x2), min(y1, y2), 
                                          abs(x2 - x1), abs(y2 - y1))
                        pygame.draw.rect(canvas, current_color, rect, brush_size)
                    
                    elif current_tool == TOOL_CIRCLE and start_pos:
                        rad = int(math.hypot(end_pos[0] - start_pos[0], 
                                            end_pos[1] - start_pos[1]))
                        pygame.draw.circle(canvas, current_color, start_pos, rad, brush_size)
                    
                    elif current_tool == TOOL_SQUARE and start_pos:
                        draw_square(canvas, current_color, start_pos, end_pos, brush_size)
                    
                    elif current_tool == TOOL_RTRI and start_pos:
                        draw_right_triangle(canvas, current_color, start_pos, end_pos, brush_size)
                    
                    elif current_tool == TOOL_EQTRI and start_pos:
                        draw_equilateral_triangle(canvas, current_color, start_pos, end_pos, brush_size)
                    
                    elif current_tool == TOOL_RHOMBUS and start_pos:
                        draw_rhombus(canvas, current_color, start_pos, end_pos, brush_size)
                
                drawing = False
                start_pos = None
                last_pos = None
                preview = None
            
            # Mouse motion
            if event.type == pygame.MOUSEMOTION and drawing:
                x, y = event.pos
                if y >= TOOLBAR_H:
                    canvas_pos = to_canvas(x, y)
                    
                    if current_tool == TOOL_PEN:
                        # Draw line between last position and current
                        if last_pos:
                            pygame.draw.line(canvas, current_color, last_pos, canvas_pos, brush_size * 2)
                        pygame.draw.circle(canvas, current_color, canvas_pos, brush_size)
                        last_pos = canvas_pos
                    
                    elif current_tool == TOOL_ERASER:
                        pygame.draw.circle(canvas, BG_CANVAS, canvas_pos, brush_size * 3)
                        last_pos = canvas_pos
                    
                    # Preview for shape tools
                    elif current_tool in [TOOL_LINE, TOOL_RECT, TOOL_CIRCLE,
                                          TOOL_SQUARE, TOOL_RTRI, TOOL_EQTRI, TOOL_RHOMBUS]:
                        if preview:
                            canvas.blit(preview, (0, 0))
                            
                            if current_tool == TOOL_LINE:
                                pygame.draw.line(canvas, current_color, start_pos, canvas_pos, brush_size)
                            elif current_tool == TOOL_RECT:
                                x1, y1 = start_pos
                                rect = pygame.Rect(min(x1, canvas_pos[0]), min(y1, canvas_pos[1]),
                                                  abs(canvas_pos[0] - x1), abs(canvas_pos[1] - y1))
                                pygame.draw.rect(canvas, current_color, rect, brush_size)
                            elif current_tool == TOOL_CIRCLE:
                                rad = int(math.hypot(canvas_pos[0] - start_pos[0],
                                                    canvas_pos[1] - start_pos[1]))
                                pygame.draw.circle(canvas, current_color, start_pos, rad, brush_size)
                            elif current_tool == TOOL_SQUARE:
                                draw_square(canvas, current_color, start_pos, canvas_pos, brush_size)
                            elif current_tool == TOOL_RTRI:
                                draw_right_triangle(canvas, current_color, start_pos, canvas_pos, brush_size)
                            elif current_tool == TOOL_EQTRI:
                                draw_equilateral_triangle(canvas, current_color, start_pos, canvas_pos, brush_size)
                            elif current_tool == TOOL_RHOMBUS:
                                draw_rhombus(canvas, current_color, start_pos, canvas_pos, brush_size)
        
        # Drawing
        screen.fill(BG_TOOLBAR)
        
        # Draw canvas
        if text_input.active and text_input.temp_surface:
            screen.blit(canvas, (0, TOOLBAR_H))
        else:
            screen.blit(preview if preview else canvas, (0, TOOLBAR_H))
        
        draw_toolbar(current_tool, current_color, brush_size)
        
        # Cursor preview
        if mouse_pos[1] >= TOOLBAR_H and current_tool not in [TOOL_FILL, TOOL_TEXT]:
            r = brush_size * 3 if current_tool == TOOL_ERASER else brush_size
            pygame.draw.circle(screen, BORDER_CLR, mouse_pos, max(r, 2), 1)
        
        pygame.display.flip()


if __name__ == "__main__":
    main()