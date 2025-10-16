import pygame
from typing import Tuple

class Ball:
    def __init__(self, x: int, y: int, radius: int = 8, vel: Tuple[float, float] = (280.0, 200.0)):
        self.pos = pygame.Vector2(float(x), float(y))
        self.radius = int(radius)
        self.vel = pygame.Vector2(*vel)
        self.rect = pygame.Rect(0, 0, radius * 2, radius * 2)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def draw(self, surface: pygame.Surface, color=(240, 240, 240)):
        pygame.draw.ellipse(surface, color, self.rect)

    def reset(self, x: int, y: int, serve_dir: int = 1):
        self.pos.update(float(x), float(y))
        self.vel.update(280.0 * serve_dir, 0.0)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def integrate_motion(self, dt: float, substeps: int = 1):
        if substeps < 1:
            substeps = 1
        step_dt = dt / substeps
        for _ in range(substeps):
            self.pos += self.vel * step_dt
            self.rect.center = (int(self.pos.x), int(self.pos.y))
