#!/usr/bin/env python3

import pygame
import numpy as np
import math

gx=0.0
gy=0.0
friction=0.03


# damage = [ice, wood, stone]
bird_masses=[5,3,1,7]
bird_damages=[[10,10,10],[7,16,7],[15,5,5],[8,8,16]]
bird_images=[]

block_masses=[10,7,15]
block_damages=[[],[],[]]
block_images=[]


class Bird(pygame.sprite.Sprite):
    def __init__(self,position,vector,bird_id,frame_id,reverse):
        super().__init__()
        self.reverse=reverse
        if self.reverse==False:
            self.image=bird_images[bird_id][frame_id]
        else:
            self.image=pygame.transform.flip(bird_images[bird_id][frame_id],True,False)
        self.rect=self.image.get_rect()
        self.rect.center=position

        self.vector=vector
        self.reverse=False
        
        self.mass=bird_masses[bird_id]
        self.damage=bird_damages[bird_id]
    def update(self):
        self.rect = self.calc_new_pos(self.rect, self.vector)

    def calc_new_pos(self, rect, vector):
        if vector[1]<=0.1 and abs(rect.center[1]-650)<=0.5:
            self.vector[0]=0
            self.vector[1]=0
            rect=rect.move(0,650-rect.center[1])
            
        if(rect.center[1]>650):
            rect=rect.move(0,650-rect.center[1])
            self.vector[1]=-0.4*vector[1]
            self.vector[0]=0.8*vector[0]
        dx = self.vector[0]
        dy = self.vector[1]
        self.vector[0]+=gx
        if abs(rect.center[1]-650)>=0.2:
            self.vector[1]+=gy

        return rect.move(dx, dy)

class Block(pygame.sprite.Sprite):
    def __init__(self,position,vector,block_id,frame_id):
        super().__init__()
        self.image=block_images[block_id][frame_id]
        self.rect=self.image.get_rect()
        self.rect.center=position

        self.vector=vector
        self.mass=block_masses[block_id]
        self.damage=block_damages[block_id]
    
    def update(self):
        self.rect = self.calc_new_pos(self.rect, self.vector)

    def calc_new_pos(self, rect, vector):
        if vector[1]<=0.1 and abs(rect.center[1]-650)<=0.5:
            self.vector[0]=0
            self.vector[1]=0
            rect=rect.move(0,650-rect.center[1])
            
        if(rect.center[1]>650):
            rect=rect.move(0,650-rect.center[1])
            self.vector[1]=-0.4*vector[1]
            self.vector[0]=0.8*vector[0]
        dx = self.vector[0]
        dy = self.vector[1]
        self.vector[0]+=gx
        if abs(rect.center[1]-650)>=0.2:
            self.vector[1]+=gy

        return rect.move(dx, dy)
    





def main():
    pygame.init()

    
    info=pygame.display.Info()

    WIDTH = info.current_w
    HEIGHT = info.current_h

    screen = pygame.display.set_mode((WIDTH, HEIGHT),pygame.FULLSCREEN)
    pygame.display.set_caption("Angry Birds Prototype")
    sling =pygame.image.load("images/sling-2.png").convert_alpha()
    sling_r=pygame.image.load("images/sling-2-r.png").convert_alpha()
    sling_LL=sling.subsurface((0,0,65,300))
    sling_LR=sling.subsurface((65,0,235,300))
    sling_RL=sling_r.subsurface((235,0,50,225))
    sling_RR=sling_r.subsurface((157,0,50,225))
    background=pygame.image.load("images/background.png").convert_alpha()
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
    bird_images.append(red_birds)
    bird_images.append(yellow_birds)
    bird_images.append(blue_birds)
    bird_images.append(black_birds)

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
    block_images.append(glass_blocks)
    block_images.append(wood_blocks)
    block_images.append(brick_blocks)
    clock = pygame.time.Clock()

    p1_structure = np.random.randint(1, 4, (6, 2))
    p2_structure = p1_structure.copy()

    p1_blocks=[]
    for i in range(p1_structure.shape[1]):
        for j in range(p1_structure.shape[0]):
            block=Block((160+i*80,635-j*80),[0,0],p1_structure[j][i]-1,3)
            p1_blocks.append(block)
    
    p2_blocks=[]
    for i in range(p2_structure.shape[1]):
        for j in range(p2_structure.shape[0]):
            block=Block((1280-i*80,635-j*80),[0,0],p2_structure[j][i]-1,3)
            p2_blocks.append(block)
    
    bird1 = Bird(
        bird_id=0,
        frame_id=0,
        position=(330, 500),
        vector=[0,0],
        reverse=False
    )
    bird2=Bird(
        bird_id=1,
        frame_id=0,
        position=(1110,500),
        vector=[0,0],
        reverse=True
        
    )

    all_sprites = pygame.sprite.Group()
    all_sprites.add(bird1)
    all_sprites.add(bird2)
    for x in p1_blocks:
        all_sprites.add(x)
    for x in p2_blocks:
        all_sprites.add(x)

    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        all_sprites.update()

        screen.fill((255, 255, 255))
        screen.blit(background,(80,0))
        # screen.blit(sling,(300,460))
        screen.blit(sling_LR,(290,460))
        screen.blit(sling_RR,(1070,460))
        all_sprites.draw(screen)
        screen.blit(sling_LL,(279,460))
        screen.blit(sling_RL,(1093,460))

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()