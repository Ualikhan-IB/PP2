"""
Tools Module - Flood Fill and Shape Utilities
"""

import pygame
import math


def flood_fill(surface, start_pos, fill_color, tolerance=0):
    """
    Flood fill algorithm using stack-based approach.
    
    Args:
        surface: pygame Surface to fill
        start_pos: (x, y) starting position
        fill_color: RGB tuple for fill color
        tolerance: color matching tolerance (0 = exact match)
    """
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
        
        # Add 4-directional neighbors
        stack.extend([(x+1, y), (x-1, y), (x, y+1), (x, y-1)])


def draw_square(surface, color, start, end, thickness):
    """Draw a square (equal width and height)"""
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
        pygame.draw.rect(surface, color, rect)
    else:
        pygame.draw.rect(surface, color, rect, thickness)


def draw_right_triangle(surface, color, start, end, thickness):
    """Draw a right triangle with right angle at start point"""
    sx, sy = start
    ex, ey = end
    points = [(sx, sy), (ex, sy), (sx, ey)]
    if thickness == 0:
        pygame.draw.polygon(surface, color, points)
    else:
        pygame.draw.polygon(surface, color, points, thickness)


def draw_equilateral_triangle(surface, color, start, end, thickness):
    """Draw an equilateral triangle"""
    sx, sy = start
    ex, ey = end
    base = abs(ex - sx)
    mid_x = (sx + ex) / 2
    height = base * math.sqrt(3) / 2
    apex_y = sy - height if ex >= sx else sy + height
    points = [(sx, sy), (ex, sy), (int(mid_x), int(apex_y))]
    if thickness == 0:
        pygame.draw.polygon(surface, color, points)
    else:
        pygame.draw.polygon(surface, color, points, thickness)


def draw_rhombus(surface, color, start, end, thickness):
    """Draw a rhombus (diamond shape)"""
    sx, sy = start
    ex, ey = end
    cx = (sx + ex) // 2
    cy = (sy + ey) // 2
    points = [(cx, sy), (ex, cy), (cx, ey), (sx, cy)]
    if thickness == 0:
        pygame.draw.polygon(surface, color, points)
    else:
        pygame.draw.polygon(surface, color, points, thickness)