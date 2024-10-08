import pygame
import math

pygame.init()
# player / map info
player_pos = [128, 128]
player_angle = 0
player_pitch = 0
player_z = 15.0
game_map = [
    "WWWWWWWWWW",
    "W        W",
    "W        W",
    "W        W",
    "W        W",
    "WWWWWWWWWW",
]
# screen information, impacts peformance.
WIDTH = 1280
HEIGHT = 720
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2.5D Aim Trainer")
# settings that greatly impact performance
FOV = math.pi / 2
VERTICAL_FOV = math.pi / 3
NUM_RAYS = int(int(WIDTH) / 8)
MAX_DEPTH = 800
DELTA_ANGLE = FOV / NUM_RAYS
SCREEN_DIST = (WIDTH // 2) / math.tan(FOV / 2)
SCALE = WIDTH // NUM_RAYS
# texture loading
wall_texture = pygame.image.load("wall_texture.png").convert()
wall_texture = pygame.transform.scale(wall_texture, (64, 64))
ceiling_texture = pygame.image.load("ceiling_texture.png").convert()
ceiling_texture = pygame.transform.scale(ceiling_texture, (WIDTH, HEIGHT))


# Target class
class Target:
    def __init__(self, pos_x, pos_y, pos_z):
        self.pos_x = pos_x * 64
        self.pos_y = pos_y * 64
        self.pos_z = pos_z
        self.size = 0.5
        self.image = pygame.image.load("target.png").convert_alpha()
        self.distance = 0

    def update(self, player_pos, player_z, player_angle, player_pitch):
        # Distance between the target and player on each axis
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

        def normalize_angle(angle):
            while angle > math.pi:
                angle -= 2 * math.pi
            while angle < -math.pi:
                angle += 2 * math.pi
            return angle

        # Normalize angle.
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

    def drawTarget(self):
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
        is_in_front_of_player = self.distance > 0
        if is_in_front_of_player:
            target_radius = self.proj_height / 2
            dx = abs(self.screen_x - WIDTH // 2)
            dy = abs(self.screen_y - HEIGHT // 2)
            # is it in the radius of the target???
            is_within_crosshair = dx < target_radius and dy < target_radius
            if is_within_crosshair:
                return True
        return False


def rayCasting(player_pos, player_angle, pitch):
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
            if 0 <= map_row < len(game_map) and 0 <= map_col < len(game_map[0]):
                # HAS BEEN HIT WALL
                if game_map[map_row][map_col] == "W":
                    break
            else:
                break
        # render walls
        if depth < MAX_DEPTH:
            corrected_depth = depth * math.cos(player_angle - current_angle)
            wall_height = (SCREEN_DIST / (corrected_depth)) * 64
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


def gameLoop():
    global player_angle, player_pitch
    clock = pygame.time.Clock()
    gameloop = True

    disableMouse()

    targets = [
        Target(2, 2, 0),
        Target(7, 2, 0),
        Target(2, 3, 10),
        Target(7, 3, -10),
        Target(4, 2, 5),
        Target(4, 3, -5),
        Target(3, 4, 0),
        Target(6, 4, 0),
        Target(5, 2, 15),
        Target(5, 4, -15),
    ]

    while gameloop:
        window.fill((255, 255, 255))

        ceiling_offset = int(math.tan(player_pitch) * SCREEN_DIST)
        ceiling_rect = ceiling_texture.get_rect()
        ceiling_rect.topleft = (0, ceiling_offset - 350)
        window.blit(ceiling_texture, ceiling_rect)

        mouse_rel = pygame.mouse.get_rel()
        player_angle += mouse_rel[0] / 1000
        player_pitch -= mouse_rel[1] / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameloop = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                for target in targets:
                    if target.isClicked():
                        targets.remove(target)
                        break

        rayCasting(player_pos, player_angle, player_pitch)

        for target in targets:
            target.update(player_pos, player_z, player_angle, player_pitch)
        targets.sort(key=lambda target: target.distance, reverse=True)

        for target in targets:
            target.drawTarget()

        pygame.display.update()
        clock.tick(240)

    pygame.quit()


gameLoop()
