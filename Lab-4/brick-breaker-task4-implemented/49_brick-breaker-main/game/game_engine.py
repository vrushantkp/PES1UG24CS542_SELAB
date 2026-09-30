import os
import pygame
from .paddle import Paddle
from .ball import Ball
from .brick import Brick

# Game Engine

WHITE = (255, 255, 255)
BG = (15, 15, 25)

BRICK_COLORS = [
    (200, 60, 60),
    (200, 140, 60),
    (200, 200, 60),
    (80, 180, 80),
    (80, 140, 200),
]


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.paddle = Paddle(
            width // 2 - 50,
            height - 30,
            100,
            14
        )

        self.ball = Ball(
            width // 2,
            height - 50,
            radius=8
        )

        self.ball.vx = 4
        self.ball.vy = -4

        self.rows = 5
        self.cols = 8

        self.bricks = self._build_bricks(
            self.rows,
            self.cols
        )

        self.lives = 3
        self.score = 0

        self.font = pygame.font.SysFont(
            "Arial",
            28
        )

        self.game_over = False
        self.result = None
        self.exit_requested = False

        self.difficulty = "medium"

        self.difficulty_settings = {
            "easy": {
                "ball_speed": 3,
                "paddle_width": 120,
            },
            "medium": {
                "ball_speed": 4,
                "paddle_width": 100,
            },
            "hard": {
                "ball_speed": 6,
                "paddle_width": 80,
            },
        }

        # Task 4: optional sound system.
        # Sound loading is intentionally non-fatal so the game still
        # works if the mixer or an individual audio file is unavailable.
        self.sounds = {}
        self.sound_enabled = False
        self._game_over_sound_played = False
        self._load_sounds()

    # ---------------------------------------------------------
    # Sound
    # ---------------------------------------------------------

    def _load_sounds(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            sound_dir = os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "assets",
                    "sounds"
                )
            )

            sound_files = {
                "paddle": "paddle.wav",
                "wall": "wall.wav",
                "brick": "brick.wav",
                "win": "win.wav",
                "game_over": "game_over.wav",
            }

            for name, filename in sound_files.items():
                path = os.path.join(
                    sound_dir,
                    filename
                )

                try:
                    if os.path.isfile(path):
                        self.sounds[name] = pygame.mixer.Sound(path)
                except (pygame.error, OSError):
                    # A single bad/missing file must not disable
                    # the rest of the game or other sounds.
                    continue

            self.sound_enabled = bool(self.sounds)

        except (pygame.error, OSError):
            # Audio is optional. Gameplay must continue if the mixer
            # cannot be initialized (for example, on a system without
            # an available audio device).
            self.sounds = {}
            self.sound_enabled = False

    def _play_sound(self, name):
        if not self.sound_enabled:
            return

        sound = self.sounds.get(name)

        if sound is None:
            return

        try:
            sound.play()
        except pygame.error:
            # Audio failure must never crash gameplay.
            pass

    # ---------------------------------------------------------
    # Brick creation
    # ---------------------------------------------------------

    def _build_bricks(self, rows, cols):
        bricks = []

        margin = 30
        gap = 6
        top = 60

        brick_w = (
            self.width
            - margin * 2
            - gap * (cols - 1)
        ) // cols

        brick_h = 22

        for r in range(rows):
            for c in range(cols):
                x = margin + c * (brick_w + gap)
                y = top + r * (brick_h + gap)

                bricks.append(
                    Brick(
                        x,
                        y,
                        brick_w,
                        brick_h
                    )
                )

        return bricks

    # ---------------------------------------------------------
    # Event handling
    # ---------------------------------------------------------

    def handle_event(self, event):
        if not self.game_over:
            return

        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_1:
            self._start_new_game("easy")

        elif event.key == pygame.K_2:
            self._start_new_game("medium")

        elif event.key == pygame.K_3:
            self._start_new_game("hard")

        elif event.key == pygame.K_ESCAPE:
            self.exit_requested = True

    # ---------------------------------------------------------
    # Input
    # ---------------------------------------------------------

    def handle_input(self):
        if self.game_over:
            return

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.paddle.move(
                -self.paddle.speed,
                self.width
            )

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.paddle.move(
                self.paddle.speed,
                self.width
            )

    # ---------------------------------------------------------
    # Main update
    # ---------------------------------------------------------

    def update(self):
        if self.game_over:
            return

        start_x = self.ball.x
        start_y = self.ball.y

        dx = self.ball.vx
        dy = self.ball.vy

        # -----------------------------------------------------
        # Paddle collision
        # -----------------------------------------------------

        paddle_rect = self.paddle.rect()

        paddle_hit_time = self._paddle_top_collision(
            start_x,
            start_y,
            dx,
            dy,
            paddle_rect
        )

        if paddle_hit_time is not None:
            self.ball.x = start_x + dx * paddle_hit_time
            self.ball.y = paddle_rect.top - self.ball.radius

            self.ball.vy = -abs(self.ball.vy)

            remaining = 1.0 - paddle_hit_time

            self.ball.x += self.ball.vx * remaining
            self.ball.y += self.ball.vy * remaining

            self._play_sound("paddle")

        else:
            self.ball.x += dx
            self.ball.y += dy

        # -----------------------------------------------------
        # Wall collisions
        # -----------------------------------------------------

        wall_hit = False

        if self.ball.x - self.ball.radius < 0:
            self.ball.x = self.ball.radius
            self.ball.vx = abs(self.ball.vx)
            wall_hit = True

        elif self.ball.x + self.ball.radius > self.width:
            self.ball.x = self.width - self.ball.radius
            self.ball.vx = -abs(self.ball.vx)
            wall_hit = True

        if self.ball.y - self.ball.radius < 0:
            self.ball.y = self.ball.radius
            self.ball.vy = abs(self.ball.vy)
            wall_hit = True

        if wall_hit:
            self._play_sound("wall")

        # -----------------------------------------------------
        # Brick collisions
        # -----------------------------------------------------

        if paddle_hit_time is None:
            ball_rect = self.ball.rect()

            for brick in self.bricks:
                if not brick.alive:
                    continue

                brick_rect = brick.rect()

                if ball_rect.colliderect(brick_rect):
                    side = self._brick_collision_side(
                        start_x,
                        start_y,
                        self.ball.x,
                        self.ball.y,
                        brick_rect
                    )

                    brick.alive = False
                    self.score += 1

                    if side == "horizontal":
                        self.ball.vx *= -1
                    else:
                        self.ball.vy *= -1

                    self._separate_from_brick(
                        brick_rect,
                        side
                    )

                    self._play_sound("brick")

                    break

        # -----------------------------------------------------
        # Ball lost
        # -----------------------------------------------------

        if self.ball.y - self.ball.radius > self.height:
            self.lives -= 1

            if self.lives <= 0:
                self.game_over = True
                self.result = "lose"
                self._play_game_over_sound()
            else:
                self._reset_ball()

        # -----------------------------------------------------
        # Win condition
        # -----------------------------------------------------

        if all(not brick.alive for brick in self.bricks):
            self.game_over = True
            self.result = "win"
            self._play_game_over_sound()

    def _play_game_over_sound(self):
        if self._game_over_sound_played:
            return

        self._game_over_sound_played = True

        if self.result == "win":
            self._play_sound("win")
        else:
            self._play_sound("game_over")

    # ---------------------------------------------------------
    # Paddle collision
    # ---------------------------------------------------------

    def _paddle_top_collision(
        self,
        start_x,
        start_y,
        dx,
        dy,
        paddle_rect
    ):
        if dy <= 0:
            return None

        start_bottom = start_y + self.ball.radius
        paddle_top = paddle_rect.top

        if start_bottom >= paddle_top:
            if start_y <= paddle_top + self.ball.radius:
                if (
                    paddle_rect.left - self.ball.radius
                    <= start_x
                    <= paddle_rect.right + self.ball.radius
                ):
                    return 0.0

            return None

        distance = paddle_top - start_bottom
        collision_time = distance / dy

        if collision_time < 0.0 or collision_time > 1.0:
            return None

        hit_x = start_x + dx * collision_time

        if (
            paddle_rect.left - self.ball.radius
            <= hit_x
            <= paddle_rect.right + self.ball.radius
        ):
            return collision_time

        return None

    # ---------------------------------------------------------
    # Brick collision side detection
    # ---------------------------------------------------------

    def _brick_collision_side(
        self,
        start_x,
        start_y,
        end_x,
        end_y,
        brick_rect
    ):
        dx = end_x - start_x
        dy = end_y - start_y

        expanded = brick_rect.inflate(
            self.ball.radius * 2,
            self.ball.radius * 2
        )

        candidates = []

        if (
            dx > 0
            and start_x <= expanded.left <= end_x
        ):
            t = (expanded.left - start_x) / dx

            if 0 <= t <= 1:
                candidates.append((t, "horizontal"))

        elif (
            dx < 0
            and start_x >= expanded.right >= end_x
        ):
            t = (expanded.right - start_x) / dx

            if 0 <= t <= 1:
                candidates.append((t, "horizontal"))

        if (
            dy > 0
            and start_y <= expanded.top <= end_y
        ):
            t = (expanded.top - start_y) / dy

            if 0 <= t <= 1:
                candidates.append((t, "vertical"))

        elif (
            dy < 0
            and start_y >= expanded.bottom >= end_y
        ):
            t = (expanded.bottom - start_y) / dy

            if 0 <= t <= 1:
                candidates.append((t, "vertical"))

        if candidates:
            return min(
                candidates,
                key=lambda item: item[0]
            )[1]

        ball_rect = self.ball.rect()

        overlap_x = (
            min(ball_rect.right, brick_rect.right)
            - max(ball_rect.left, brick_rect.left)
        )

        overlap_y = (
            min(ball_rect.bottom, brick_rect.bottom)
            - max(ball_rect.top, brick_rect.top)
        )

        if overlap_x < overlap_y:
            return "horizontal"

        return "vertical"

    # ---------------------------------------------------------
    # Separate ball from brick
    # ---------------------------------------------------------

    def _separate_from_brick(self, brick_rect, side):
        if side == "horizontal":
            if self.ball.vx > 0:
                self.ball.x = brick_rect.right + self.ball.radius
            else:
                self.ball.x = brick_rect.left - self.ball.radius
        else:
            if self.ball.vy > 0:
                self.ball.y = brick_rect.bottom + self.ball.radius
            else:
                self.ball.y = brick_rect.top - self.ball.radius

    # ---------------------------------------------------------
    # Start fresh game
    # ---------------------------------------------------------

    def _start_new_game(self, difficulty):
        settings = self.difficulty_settings[difficulty]

        self.difficulty = difficulty

        self.score = 0
        self.lives = 3

        self.game_over = False
        self.result = None
        self.exit_requested = False
        self._game_over_sound_played = False

        self.bricks = self._build_bricks(
            self.rows,
            self.cols
        )

        paddle_width = settings["paddle_width"]

        self.paddle.width = paddle_width
        self.paddle.x = (
            self.width // 2
            - paddle_width // 2
        )
        self.paddle.y = self.height - 30

        self.ball.x = self.width // 2
        self.ball.y = self.height - 50

        speed = settings["ball_speed"]

        self.ball.vx = speed
        self.ball.vy = -speed

        if hasattr(self, "_game_over_logged"):
            del self._game_over_logged

    # ---------------------------------------------------------
    # Reset ball after losing a life
    # ---------------------------------------------------------

    def _reset_ball(self):
        speed = self.difficulty_settings[
            self.difficulty
        ]["ball_speed"]

        self.ball.x = self.width // 2
        self.ball.y = self.height - 50

        self.ball.vx = speed
        self.ball.vy = -speed

    # ---------------------------------------------------------
    # Rendering
    # ---------------------------------------------------------

    def render(self, screen):
        screen.fill(BG)

        pygame.draw.rect(
            screen,
            WHITE,
            self.paddle.rect()
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (
                int(self.ball.x),
                int(self.ball.y)
            ),
            self.ball.radius
        )

        for i, brick in enumerate(self.bricks):
            if brick.alive:
                row = i // self.cols

                color = BRICK_COLORS[
                    row % len(BRICK_COLORS)
                ]

                pygame.draw.rect(
                    screen,
                    color,
                    brick.rect()
                )

        score_text = self.font.render(
            f"Score: {self.score}",
            True,
            WHITE
        )

        screen.blit(
            score_text,
            (10, 10)
        )

        lives_text = self.font.render(
            f"Lives: {self.lives}",
            True,
            WHITE
        )

        screen.blit(
            lives_text,
            (
                self.width - 130,
                10
            )
        )

        # -----------------------------------------------------
        # End screen
        # -----------------------------------------------------

        if self.game_over:
            overlay = pygame.Surface(
                (
                    self.width,
                    self.height
                ),
                pygame.SRCALPHA
            )

            overlay.fill(
                (0, 0, 0, 190)
            )

            screen.blit(
                overlay,
                (0, 0)
            )

            if self.result == "win":
                result_text = "YOU WIN!"
            else:
                result_text = "GAME OVER"

            result_font = pygame.font.SysFont(
                "Arial",
                56,
                bold=True
            )

            result_surface = result_font.render(
                result_text,
                True,
                WHITE
            )

            result_rect = result_surface.get_rect(
                center=(
                    self.width // 2,
                    self.height // 2 - 120
                )
            )

            screen.blit(
                result_surface,
                result_rect
            )

            score_font = pygame.font.SysFont(
                "Arial",
                30
            )

            final_score_surface = score_font.render(
                f"Final Score: {self.score}",
                True,
                WHITE
            )

            final_score_rect = final_score_surface.get_rect(
                center=(
                    self.width // 2,
                    self.height // 2 - 55
                )
            )

            screen.blit(
                final_score_surface,
                final_score_rect
            )

            menu_font = pygame.font.SysFont(
                "Arial",
                24
            )

            options = [
                ("1 - Easy", 5),
                ("2 - Medium", 40),
                ("3 - Hard", 75),
                ("ESC - Exit", 125),
            ]

            for text, offset in options:
                surface = menu_font.render(
                    text,
                    True,
                    WHITE
                )

                rect = surface.get_rect(
                    center=(
                        self.width // 2,
                        self.height // 2 + offset
                    )
                )

                screen.blit(
                    surface,
                    rect
                )
