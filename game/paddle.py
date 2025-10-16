import pygame

class Paddle:
    def __init__(self, x: int, y: int, width: int = 12, height: int = 90, speed: float = 420.0):
        self.rect = pygame.Rect(x, y, width, height)
        self.base_speed = float(speed)
        self.speed = float(speed)
        self.score = 0

    def move_player(self, dt: float, up_key: int, down_key: int, bounds: pygame.Rect):
        keys = pygame.key.get_pressed()
        dy = 0.0
        if keys[up_key]:
            dy -= self.speed * dt
        if keys[down_key]:
            dy += self.speed * dt

        if dy != 0.0:
            new_y = self.rect.y + dy
            self.rect.y = int(max(bounds.top, min(bounds.bottom - self.rect.height, new_y)))

    def move_ai(self, dt: float, target_y: float, bounds: pygame.Rect, max_track_speed: float = None):
        if max_track_speed is None:
            max_track_speed = self.speed * 0.9

        center = self.rect.centery
        diff = target_y - center

        if abs(diff) < 6:
            return

        step = max(-max_track_speed * dt, min(max_track_speed * dt, diff))
        self.rect.y = int(max(bounds.top, min(bounds.bottom - self.rect.height, self.rect.y + step)))

    def draw(self, surface: pygame.Surface, color=(240, 240, 240)):
        pygame.draw.rect(surface, color, self.rect)

    def reset(self, x: int, y: int):
        self.rect.topleft = (x, y)
