import pygame
import math
import random
import sys

pygame.init()
pygame.font.init()
pygame.mixer.init()
sound_effect = pygame.mixer.Sound("hitmarker.mp3")

# Player and map info
player_pos = [128, 128]
player_angle = 0
player_pitch = 0
player_z = 15.0
player_speed = 1
game_map = [
    "WWWWWWWWWW",
    "W        W",
    "W        W",
    "W        W",
    "W        W",
    "WWWWWWWWWW",
]

# Screen information
WIDTH = 1920
HEIGHT = 1080

# Performance settings
FOV = math.pi / 2
VERTICAL_FOV = math.pi / 3
NUM_RAYS = int(WIDTH / 16)
MAX_DEPTH = 800
DELTA_ANGLE = FOV / NUM_RAYS
SCREEN_DIST = (WIDTH // 2) / math.tan(FOV / 2)
SCALE = WIDTH // NUM_RAYS

# Target class
class Target:
    def __init__(self, pos_x, pos_y, pos_z, image, moving=False):
        self.pos_x = pos_x * 64
        self.pos_y = pos_y * 64
        self.pos_z = pos_z
        self.size = 0.5
        self.image = image
        self.distance = 0
        self.moving = moving
        self.move_dx = random.choice([-1, 1]) * random.uniform(0.5, 1.5)
        self.move_dy = random.choice([-1, 1]) * random.uniform(0.5, 1.5)

    def respawn(self, targets):
        #prevent x,y positions from colliding
        max_x = len(game_map[0]) - 2
        max_y = len(game_map) - 2
        occupied_positions = set(
            (t.pos_x // 64, t.pos_y // 64) for t in targets if t != self
        )
        while True:
            pos_x = random.randint(1, max_x)
            pos_y = random.randint(1, max_y)
            if (pos_x, pos_y) not in occupied_positions:
                break
        self.pos_x = pos_x * 64
        self.pos_y = pos_y * 64
        self.pos_z = random.randint(-15, 15)
        #movement direction change
        self.move_dx = random.choice([-1, 1]) * random.uniform(0.5, 1.5)
        self.move_dy = random.choice([-1, 1]) * random.uniform(0.5, 1.5)

    def update(self, player_pos, player_z, player_angle, player_pitch):
        # position update if moving.
        if self.moving:
            self.pos_x += self.move_dx
            self.pos_y += self.move_dy
            map_col = int(self.pos_x) // 64
            map_row = int(self.pos_y) // 64
            if self.pos_x < 64 or self.pos_x > (len(game_map[0]) - 1) * 64 or game_map[map_row][map_col] == "W":
                self.move_dx *= -1
                self.pos_x += self.move_dx * 2  # Move back into bounds
            if self.pos_y < 64 or self.pos_y > (len(game_map) - 1) * 64 or game_map[map_row][map_col] == "W":
                self.move_dy *= -1
                self.pos_y += self.move_dy * 2  # Move back into bounds

        dx = self.pos_x - player_pos[0]
        dy = self.pos_y - player_pos[1]
        dz = self.pos_z - player_z
        # The straight line distance between the target and the player, neglecting height
        horizontal_distance = math.hypot(dx, dy)  # Distance on the ground plane
        # The straight line distance between the target and the player, including height
        self.distance = math.hypot(horizontal_distance, dz)
        # angle difference horizontally between fixed reference and target
        self.theta = math.atan2(dy, dx)
        # angle difference vertically between fixed reference and target
        self.phi = math.atan2(dz, horizontal_distance)
        # Required change in horizontal angle to reach the target
        angle_difference = self.theta - player_angle

        # Normalize angle.
        def normalize_angle(angle):
            while angle > math.pi:
                angle -= 2 * math.pi
            while angle < -math.pi:
                angle += 2 * math.pi
            return angle

        self.delta_theta = normalize_angle(angle_difference)
        # Required change in vertical angle to reach the target.
        self.delta_phi = player_pitch - self.phi
        # Scale the size of the target with distance.
        self.proj_height = (SCREEN_DIST / self.distance) * self.size * 64
        # save / calc the location to draw x.
        self.screen_x = ((self.delta_theta + FOV / 2) * WIDTH) / FOV
        # save / calc the location to draw y.
        self.screen_y = (
            (HEIGHT // 2) + (self.delta_phi * SCREEN_DIST) - (self.proj_height / 2)
        )

    def drawTarget(self, window):
        is_in_front_of_player = self.distance > 0
        half_horizontal_fov = math.pi / 2
        is_within_horizontal_fov = (
            -half_horizontal_fov < self.delta_theta < half_horizontal_fov
        )
        if is_in_front_of_player and is_within_horizontal_fov:
            target_surface = pygame.transform.scale(
                self.image, (int(self.proj_height), int(self.proj_height))
            )
            window.blit(
                target_surface, (self.screen_x - self.proj_height // 2, self.screen_y)
            )

    def isClicked(self):
        target_radius = self.proj_height / 2
        mouse_x, mouse_y = pygame.mouse.get_pos()
        target_center_y = self.screen_y + self.proj_height / 2
        dx = abs(self.screen_x - mouse_x)
        dy = abs(target_center_y - mouse_y)
        # is it in the radius of the target???
        is_within_crosshair = dx < target_radius and dy < target_radius
        # had the dumbest if statement before, changed...
        return is_within_crosshair


def rayCasting(player_pos, player_angle, pitch, window, wall_texture):
    player_x, player_y = player_pos
    current_angle = player_angle - (FOV / 2)

    # ray loop
    for ray in range(NUM_RAYS):
        sin_angle = math.sin(current_angle)
        cos_angle = math.cos(current_angle)
        depth = 0
        # cast current ray.
        while depth < MAX_DEPTH:
            depth += 1
            # This is the position of the incremented ray
            ray_x = player_x + depth * cos_angle
            ray_y = player_y + depth * sin_angle
            # grid coordinate normalization
            map_col = int(ray_x) // 64
            map_row = int(ray_y) // 64
            # is the ray in the map?
            if 0 <= map_row < len(game_map) and 0 <= map_col < len(
                game_map[0]
            ):  # HAS BEEN HIT WALL
                if game_map[map_row][map_col] == "W":
                    break
            else:
                break

        # render walls
        if depth < MAX_DEPTH:
            corrected_depth = depth * math.cos(player_angle - current_angle)
            wall_height = (SCREEN_DIST / corrected_depth) * 64
            # slice the wall texture
            wall_texture_column = wall_texture.subsurface(0, 0, 64, 64)
            # scale the wall texture column to the projected wall height
            wall_texture_column = pygame.transform.scale(
                wall_texture_column, (SCALE, int(wall_height))
            )
            # calculate the y to draw the wall, accounting for player pitch
            vertical_offset = math.tan(pitch) * SCREEN_DIST
            screen_y = (HEIGHT // 2 - wall_height // 2) + vertical_offset
            # draw the wall
            window.blit(wall_texture_column, (ray * SCALE, screen_y))
            # increment angle for next ray
        current_angle += DELTA_ANGLE


def disableMouse():
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    pygame.mouse.get_rel()


# ADDED CROSSHAIR
def draw_crosshair():
    crosshair_size = 20
    color = (0, 0, 0)
    thickness = 2
    pygame.draw.line(
        window,
        color,
        (WIDTH // 2 - crosshair_size, HEIGHT // 2),
        (WIDTH // 2 + crosshair_size, HEIGHT // 2),
        thickness,
    )
    pygame.draw.line(
        window,
        color,
        (WIDTH // 2, HEIGHT // 2 - crosshair_size),
        (WIDTH // 2, HEIGHT // 2 + crosshair_size),
        thickness,
    )


def handlePlayerMovement(keyboard):
    global player_pos
    new_x = player_pos[0]
    new_y = player_pos[1]

    sin_angle = math.sin(player_angle)
    cos_angle = math.cos(player_angle)

    if keyboard[pygame.K_w]:
        new_x += cos_angle * player_speed
        new_y += sin_angle * player_speed
    if keyboard[pygame.K_a]:
        new_x += sin_angle * player_speed
        new_y -= cos_angle * player_speed
    if keyboard[pygame.K_s]:
        new_x -= cos_angle * player_speed
        new_y -= sin_angle * player_speed
    if keyboard[pygame.K_d]:
        new_x -= sin_angle * player_speed
        new_y += cos_angle * player_speed
    player_pos[0] = new_x
    player_pos[1] = new_y


def gameLoop(task):
    global player_angle, player_pitch, player_pos
    clock = pygame.time.Clock()
    gameloop = True

    window = pygame.display.get_surface()

    # load textures in local. Potential optimization on target_image
    wall_texture = pygame.image.load("wall_texture.png").convert()
    wall_texture = pygame.transform.scale(wall_texture, (64, 64))
    ceiling_texture = pygame.image.load("ceiling_texture.png").convert()
    ceiling_texture = pygame.transform.scale(ceiling_texture, (WIDTH, HEIGHT))
    target_image = pygame.image.load("target.png").convert_alpha()

    # Hide the mouse and set the initial score
    disableMouse()
    score = 0
    font = pygame.font.Font(None, 36) # Font for displaying the score

    # Determine if targets should move based on task
    moving_targets = task.get('moving_targets', False)

    targets = [
        Target(2, 2, 0, target_image, moving=moving_targets),
        Target(7, 2, 0, target_image, moving=moving_targets),
        Target(2, 3, 10, target_image, moving=moving_targets),
        Target(7, 3, -10, target_image, moving=moving_targets),
        Target(4, 2, 5, target_image, moving=moving_targets),
        Target(4, 3, -5, target_image, moving=moving_targets),
        Target(3, 4, 0, target_image, moving=moving_targets),
        Target(6, 4, 0, target_image, moving=moving_targets),
        Target(5, 2, 15, target_image, moving=moving_targets),
        Target(5, 4, -15, target_image, moving=moving_targets),
    ]

    while gameloop:
        window.fill((255, 255, 255))

        ceiling_offset = int(math.tan(player_pitch) * SCREEN_DIST)
        ceiling_rect = ceiling_texture.get_rect()
        ceiling_rect.topleft = (0, ceiling_offset - 500)
        window.blit(ceiling_texture, ceiling_rect)

        mouse_rel = pygame.mouse.get_rel()
        player_angle += mouse_rel[0] / 1000
        player_pitch -= mouse_rel[1] / 1000

        handlePlayerMovement(pygame.key.get_pressed())
        # score and respawning
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameloop = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pygame.mouse.set_pos(WIDTH // 2, HEIGHT // 2)
                targets.sort(key=lambda target: target.distance)
                for target in targets:
                    if target.isClicked():
                        sound_effect.play()
                        target.respawn(targets)
                        score += 1
                        break

        rayCasting(player_pos, player_angle, player_pitch, window, wall_texture)
        for target in targets:
            target.update(player_pos, player_z, player_angle, player_pitch)
        targets.sort(key=lambda target: target.distance, reverse=True)
        for target in targets:
            target.drawTarget(window)

        draw_crosshair(window)

        score_text = font.render(f"Score: {score}", True, (10, 10, 10))
        # fixed the scoring display
        window.blit(score_text, (225, 50))
        pygame.display.update()
        clock.tick(240)

    pygame.quit()
