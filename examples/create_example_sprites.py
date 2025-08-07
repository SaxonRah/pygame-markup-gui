# create_example_sprites.py
import pygame
import os


def create_example_sprites():
    """Create example pixel art sprites for testing"""
    pygame.init()

    # Create sprites directory
    os.makedirs("assets/sprites", exist_ok=True)

    # UI Corner sprite (8x8 pixels)
    corner = pygame.Surface((8, 8), pygame.SRCALPHA)
    corner.fill((255, 255, 255, 0))  # Transparent
    # Draw a simple corner pattern
    for i in range(8):
        for j in range(8):
            if (i == 0 or j == 0 or
                    (i == 1 and j <= 2) or
                    (j == 1 and i <= 2)):
                corner.set_at((i, j), (255, 255, 255, 255))  # White
    pygame.image.save(corner, "assets/sprites/ui_corner.png")

    # UI Edge sprite (8x8 pixels)
    edge = pygame.Surface((8, 8), pygame.SRCALPHA)
    edge.fill((255, 255, 255, 0))
    # Top and bottom border
    for i in range(8):
        edge.set_at((i, 0), (255, 255, 255, 255))
        edge.set_at((i, 1), (255, 255, 255, 128))
    pygame.image.save(edge, "assets/sprites/ui_edge.png")

    # Button corner sprite
    btn_corner = pygame.Surface((6, 6), pygame.SRCALPHA)
    btn_corner.fill((255, 255, 255, 0))
    for i in range(6):
        for j in range(6):
            if i == 0 or j == 0 or (i == 1 and j == 1):
                btn_corner.set_at((i, j), (255, 255, 255, 255))
    pygame.image.save(btn_corner, "assets/sprites/btn_corner.png")

    # Button edge sprite
    btn_edge = pygame.Surface((6, 6), pygame.SRCALPHA)
    btn_edge.fill((255, 255, 255, 0))
    for i in range(6):
        btn_edge.set_at((i, 0), (255, 255, 255, 255))
    pygame.image.save(btn_edge, "assets/sprites/btn_edge.png")

    # Background texture
    texture = pygame.Surface((16, 16), pygame.SRCALPHA)
    for i in range(16):
        for j in range(16):
            # Create a simple noise pattern
            intensity = 255 if (i + j) % 3 == 0 else 200
            texture.set_at((i, j), (intensity, intensity, intensity, 255))
    pygame.image.save(texture, "assets/sprites/texture_bg.png")

    # Crown icon
    crown = pygame.Surface((16, 16), pygame.SRCALPHA)
    crown.fill((255, 255, 255, 0))
    # Simple crown shape
    crown_pixels = [
        (7, 2), (8, 2),
        (6, 3), (7, 3), (8, 3), (9, 3),
        (5, 4), (6, 4), (7, 4), (8, 4), (9, 4), (10, 4),
        (4, 5), (5, 5), (6, 5), (7, 5), (8, 5), (9, 5), (10, 5), (11, 5)
    ]
    for x, y in crown_pixels:
        crown.set_at((x, y), (255, 255, 255, 255))
    pygame.image.save(crown, "assets/sprites/crown.png")

    # Slot background
    slot_bg = pygame.Surface((64, 64), pygame.SRCALPHA)
    slot_bg.fill((255, 255, 255, 50))  # Semi-transparent white
    pygame.image.save(slot_bg, "assets/sprites/slot_bg.png")

    # Slot corner
    slot_corner = pygame.Surface((8, 8), pygame.SRCALPHA)
    slot_corner.fill((255, 255, 255, 0))
    for i in range(3):
        for j in range(3):
            slot_corner.set_at((i, j), (255, 255, 255, 255))
    pygame.image.save(slot_corner, "assets/sprites/slot_corner.png")

    print("Example sprites created in assets/sprites/")


if __name__ == "__main__":
    create_example_sprites()