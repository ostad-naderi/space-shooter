import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((600, 900))
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 40)

text = font.render("TEST OK!", True, (255, 255, 255))
color = [255, 0, 0]

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if e.type == pygame.FINGERDOWN:
            if color[0] == 255:
                color = [0, 255, 0]
            else:
                color = [255, 0, 0]

    screen.fill(color)
    screen.blit(text, (150, 400))
    pygame.display.flip()
    clock.tick(60)
