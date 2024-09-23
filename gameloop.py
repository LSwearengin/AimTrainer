import pygame
pygame.init()
window = pygame.display.set_mode((500, 500))
pygame.display.set_caption("AimTrainer")
gameloop = True
while gameloop:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameloop = False
    window.fill((0, 0, 0))
    pygame.display.update()
    
pygame.quit()
