#https://www.pygame.org/docs


# needed for pygame. Sets up the window
import pygame
pygame.init()
window = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("AimTrainer")

class Target:
    def __init__(self, pos_x, pos_y, size, filename):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.size = size
        self.filename = filename
        self.pygameSurface = pygame.image.load(filename).convert_alpha()
        self.pygameSurface = pygame.transform.scale(self.pygameSurface, (self.size, self.size))
    def drawTarget(self, window):
        window.blit(self.pygameSurface, (self.pos_x, self.pos_y))
        pygame.display.flip()
    def isClicked(self, mouse_pos):
        if (self.pos_x <= mouse_pos[0] <= self.pos_x + self.size) and (self.pos_y <= mouse_pos[1] <= self.pos_y + self.size):
            return True
        return False
def gameLoop():
    #used to limit the fps
    clock = pygame.time.Clock()
    gameloop = True
    
    # initially should be generated on a function call, depending on the specific task
    targets = []
    targets.append(Target(5, 5, 100, 'target.png'))
    while gameloop:
        window.fill((255, 255, 255))
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameloop = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                for target in targets:
                    if target.isClicked(mouse_pos):
                        targets.remove(target)
        for target in targets:
            target.drawTarget(window)
        pygame.display.update()
        
        
        # LIMIT TO 60 FPS
        clock.tick(60)
        
    pygame.quit()
gameLoop()
        
    