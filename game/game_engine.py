import pygame
from typing import Optional
from .paddle import Paddle
from .ball import Ball

WHITE = (240, 240, 240)
GREY = (90, 90, 90)
BLACK = (10, 10, 10)

class GameEngine:
    def __init__(self, width: int = 960, height: int = 540, best_of: int = 5):
        pygame.init()
        self.width, self.height = width, height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Ping Pong – Pygame")
        self.clock = pygame.time.Clock()
        self.bounds = pygame.Rect(0, 0, self.width, self.height)

        self.font = pygame.font.SysFont("Arial", 36)
        self.big_font = pygame.font.SysFont("Arial", 64)

        self._init_audio()

        margin = 30
        self.player = Paddle(margin, (self.height - 100) // 2, height=100)
        self.ai = Paddle(self.width - margin - 12, (self.height - 100) // 2, height=100, speed=380.0)
        self.ball = Ball(self.width // 2, self.height // 2)

        self.best_of = best_of
        self.target_points = (best_of // 2) + 1
        self.running = True
        self.serve_dir = 1
        self._reset_round()

    def _init_audio(self):
        try:
            pygame.mixer.init()
            self.snd_paddle = pygame.mixer.Sound("assets/sounds/paddle.wav")
            self.snd_wall = pygame.mixer.Sound("assets/sounds/wall.wav")
            self.snd_score = pygame.mixer.Sound("assets/sounds/score.wav")
        except Exception:
            self.snd_paddle = self.snd_wall = self.snd_score = None

    def _play(self, snd):
        if snd:
            try:
                snd.play()
            except Exception:
                pass

    def _reset_round(self):
        self.ball.reset(self.width // 2, self.height // 2, self.serve_dir)

    def _draw_center_line(self):
        seg_h, gap, x = 16, 12, self.width // 2
        for y in range(0, self.height, seg_h + gap):
            pygame.draw.line(self.screen, GREY, (x, y), (x, y + seg_h), 3)

    def _draw_scores(self):
        left = self.font.render(str(self.player.score), True, WHITE)
        right = self.font.render(str(self.ai.score), True, WHITE)
        self.screen.blit(left, (self.width * 0.25 - left.get_width() // 2, 20))
        self.screen.blit(right, (self.width * 0.75 - right.get_width() // 2, 20))

    def _handle_wall_collisions(self):
        if self.ball.rect.top <= 0 or self.ball.rect.bottom >= self.height:
            self.ball.vel.y *= -1
            self._play(self.snd_wall)

        if self.ball.rect.right < 0:
            self.ai.score += 1
            self.serve_dir = 1
            self._reset_round()
            self._play(self.snd_score)
        elif self.ball.rect.left > self.width:
            self.player.score += 1
            self.serve_dir = -1
            self._reset_round()
            self._play(self.snd_score)

    def _swept_collision(self, paddle, dt):
        if (paddle is self.player and self.ball.vel.x < 0) or (paddle is self.ai and self.ball.vel.x > 0):
            speed = abs(self.ball.vel.x)
            steps = max(1, min(8, int(speed * dt / 20.0)))
            temp_pos = pygame.Vector2(self.ball.pos)
            temp_rect = self.ball.rect.copy()

            for _ in range(steps):
                temp_pos += self.ball.vel * (dt / steps)
                temp_rect.center = (int(temp_pos.x), int(temp_pos.y))
                if temp_rect.colliderect(paddle.rect):
                    offset = (temp_rect.centery - paddle.rect.centery) / (paddle.rect.height / 2)
                    self.ball.pos = pygame.Vector2(temp_pos)
                    self.ball.rect = temp_rect.copy()
                    self.ball.vel.x *= -1
                    self.ball.vel.y += 220 * offset
                    self.ball.vel.y = max(-520, min(520, self.ball.vel.y))
                    self._play(self.snd_paddle)
                    return True
        return False

    def _update(self, dt):
        self.player.move_player(dt, pygame.K_w, pygame.K_s, self.bounds)
        self.ai.move_ai(dt, self.ball.rect.centery, self.bounds)

        speed = self.ball.vel.length()
        substeps = max(1, min(8, int(speed * dt / 18)))
        self.ball.integrate_motion(dt, substeps)
        self._handle_wall_collisions()

        if not self._swept_collision(self.player, dt):
            self._swept_collision(self.ai, dt)

    def _draw(self):
        self.screen.fill(BLACK)
        self._draw_center_line()
        self.player.draw(self.screen)
        self.ai.draw(self.screen)
        self.ball.draw(self.screen)
        self._draw_scores()
        pygame.display.flip()

    def _check_game_over(self) -> Optional[str]:
        if self.player.score >= self.target_points:
            return "Player Wins!"
        if self.ai.score >= self.target_points:
            return "AI Wins!"
        return None

    def _game_over_screen(self, msg):
        text = self.big_font.render(msg, True, WHITE)
        prompt = self.font.render("Press R to Replay  |  M for Match Options  |  ESC to Exit", True, WHITE)
        self.screen.fill(BLACK)
        self.screen.blit(text, (self.width // 2 - text.get_width() // 2, self.height // 2 - text.get_height()))
        self.screen.blit(prompt, (self.width // 2 - prompt.get_width() // 2, self.height // 2 + 10))
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        waiting = False
                    elif event.key == pygame.K_r:
                        self.player.score = self.ai.score = 0
                        self.serve_dir = 1
                        self._reset_round()
                        waiting = False
                    elif event.key == pygame.K_m:
                        waiting = False
                        self._match_options_menu()

    def _match_options_menu(self):
        options = [3, 5, 7]
        labels = [f"Best of {n} (press {n})" for n in options]
        info = self.font.render("ESC to cancel", True, WHITE)

        while True:
            self.screen.fill(BLACK)
            title = self.big_font.render("Match Options", True, WHITE)
            self.screen.blit(title, (self.width // 2 - title.get_width() // 2, self.height // 2 - 100))
            for i, lbl in enumerate(labels):
                surf = self.font.render(lbl, True, WHITE)
                self.screen.blit(surf, (self.width // 2 - surf.get_width() // 2, self.height // 2 + i * 40))
            self.screen.blit(info, (self.width // 2 - info.get_width() // 2, self.height // 2 + len(labels) * 40 + 20))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    elif event.key in (pygame.K_3, pygame.K_5, pygame.K_7):
                        chosen = int(event.unicode)
                        self.best_of = chosen
                        self.target_points = (chosen // 2) + 1
                        self.player.score = self.ai.score = 0
                        self.serve_dir = 1
                        self._reset_round()
                        return

    def run(self):
        while self.running:
            dt = self.clock.tick(120) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self._update(dt)
            self._draw()
            result = self._check_game_over()
            if result:
                self._game_over_screen(result)
        pygame.quit()
