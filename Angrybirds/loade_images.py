import pygame
import numpy as np
import math



def main():
    pygame.init()
    WIDTH = 800
    HEIGHT = 600

    screen = pygame.display.set_mode((WIDTH, HEIGHT),pygame.FULLSCREEN)
    birds=pygame.image.load("images/angry_birds.png").convert_alpha()
    red=birds.subsurface((180,0,619,120))
    red_birds=[]
    for i in range(5):
        red_birds.append(red.subsurface((i*75,0,75,120)))
    blue=birds.subsurface((210,135,300,55))
    blue_birds=[]
    for i in range(5):
        blue_birds.append(blue.subsurface((i*60,0,60,55)))
    yellow=birds.subsurface((186,205,400,85))
    yellow_birds=[]
    for i in range(5):
        yellow_birds.append(yellow.subsurface((i*78,0,78,85)))
    black=birds.subsurface((115,305,575,105))
    black_birds=[]
    for i in range(6):
        black_birds.append(black.subsurface((i*73.3,0,73.3,105)))
    for i in range(2):
        black_birds.append(black.subsurface((440+i*67.5,0,67.5,105)))
    white=birds.subsurface((140,430,516,110))
    white_birds=[]
    for i in range(6):
        white_birds.append(white.subsurface((i*86,0,86,110)))
    blocks=pygame.image.load("images/blocks.png").convert_alpha()
    glass=blocks.subsurface((0,0,85,350))
    glass_blocks=[]
    for i in range(4):
        glass_blocks.append(glass.subsurface((2,i*85+i*3.3,80,80)))
    wood=blocks.subsurface((584,2,80,350))
    wood_blocks=[]
    for i in range(4):
        wood_blocks.append((wood.subsurface((0,i*85+i*3.3,80,80))))
    brick=blocks.subsurface((1170,1,345,81))
    brick_blocks=[]
    for i in range(4):
        brick_blocks.append((brick.subsurface((i*85,0,80,80))))
    clock = pygame.time.Clock()
    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        screen.fill((255, 255, 255))
        # screen.blit(red,(0,0))
        # for i in range(5):
        #     screen.blit(red_birds[i],(100+i*75,0))
        # screen.blit(blue_birds[4],(0,0))
        # screen.blit(yellow_birds[0],(0,0))
        # screen.blit(black_birds[1],(0,0))
        # screen.blit(black_birds[7],(0,0))
        # screen.blit(white_birds[5],(0,0))
        # screen.blit(glass_blocks[3],(0,0))
        # screen.blit(wood_blocks[3],(0,0))
        screen.blit(brick_blocks[0],(0,0))
        pygame.display.flip()

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()