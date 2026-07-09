#!/usr/bin/env python3

import pygame
import numpy as np
import math
import random

gx_birds=0.0
gy_birds=0.1
gy_blocks=0.0
gx_blocks=0.0
friction=0.3
DOUBLE_CLICK_TIME=400
block_health=[60,80,100]


# damage = [ice, wood, stone]
bird_masses=[5,3,1,7]
bird_damages=[[10,10,10],[7,16,7],[15,5,5],[8,8,16]]
bird_images=[]

block_masses=[10,7,15]
block_damages=[[],[],[]]
block_images=[]

slingpoint_LR=(355,498)
slingpoint_LL=(310,500)
slingpoint_RL=(1085,500)
slingpoint_RR=(1127,500)

slings_centers=[[330,500],[1110,500]]
slingpoints=[[[310,500],[355,498]],[[1127,500],[1085,500]]]

# bird_sling_L=(310,518)
# brid_sling_R=(1127,518)

def get_sprite(sheet, x1, y1, x2, y2):
    return sheet.subsurface(
        (x1, y1, x2 - x1, y2 - y1)
    ).copy()


class Bird(pygame.sprite.Sprite):
    def __init__(self,position,vector,bird_id,frame_id,reverse,state):
        super().__init__()
        self.bird_id=bird_id
        self.frame_id=frame_id
        self.gx=0.0
        self.gy=0.1
        self.state=state
        self.reverse=reverse
        if self.reverse==False:
            self.image=bird_images[bird_id][frame_id]
        else:
            self.image=pygame.transform.flip(bird_images[bird_id][frame_id],True,False)
        self.rect=self.image.get_rect()
        self.rect.center=position

        self.vector=vector
        self.reverse=reverse
        
        self.mass=bird_masses[bird_id]
        self.damage=bird_damages[bird_id]
        self.last_position=position
        self.last_vec=vector
    
    def change_bird(self,bird_id,frame_id,state):
        self.bird_id=bird_id
        self.frame_id=frame_id
        self.state=state
        if self.reverse==False:
            self.image=bird_images[bird_id][frame_id]
        else:
            self.image=pygame.transform.flip(bird_images[bird_id][frame_id],True,False)
        self.rect=self.image.get_rect()
        
        self.mass=bird_masses[bird_id]
        self.damage=bird_damages[bird_id]
        self.last_position=self.rect.center
        self.last_vec=self.vector
        
    def update(self):
        self.last_position=self.rect.center
        self.last_vec=self.vector
        if self.state=="movement":
            self.gy=0.1
            self.rect = self.calc_new_pos(self.rect, self.vector)
        elif self.state=="sling_op1":
            self.gy=0.0
            self.rect = self.calc_new_pos(self.rect,self.vector)
    def move(self,new_position):
        self.rect=self.rect.move(new_position[0]-self.rect.center[0],new_position[1]-self.rect.center[1])


    def calc_new_pos(self, rect, vector):
        if abs(vector[1])<=0.1 and abs(rect.center[1]-650)<=0.5:
            self.vector[1]=0
            vector[1]=0
            rect=rect.move(0,650-rect.center[1])

        if vector[0]<=0.1 and abs(rect.center[0]-1360)<=0.5:
            self.vector[0]=0
            vector[0]=0
            rect=rect.move(1360-rect.center[0],0)
        
        if rect.center[0]>=1360:
            rect=rect.move(1360-rect.center[0],0)
            self.vector[0]=0.0

        if vector[0]>=-0.1 and abs(80-rect.center[0])<=0.5:
            self.vector[0]=0
            vector[0]=0
            rect=rect.move(80-rect.center[0],0)
        
        if rect.center[0]<=80:
            rect=rect.move(80-rect.center[0],0)
            self.vector[0]=0.0
        
        

            
        if(rect.center[1]>=650):
            rect=rect.move(0,650-rect.center[1])
            self.vector[1]=-0.4*vector[1]
            self.vector[0]=0.8*vector[0]
        dx = self.vector[0]
        dy = self.vector[1]
        self.vector[0]+=self.gx
        if abs(rect.center[1]-650)>=0.2:
            self.vector[1]+=self.gy

        return rect.move(dx, dy)

class Block(pygame.sprite.Sprite):
    def __init__(self,position,vector,block_id,frame_id):
        super().__init__()
        self.health=block_health[block_id]
        self.frame_id=frame_id
        self.image=block_images[block_id][frame_id]
        self.rect=self.image.get_rect()
        self.rect.center=position
        self.block_id=block_id

        self.vector=vector
        self.mass=block_masses[block_id]
        self.damage=block_damages[block_id]
    
    def update(self):
        self.frame_id=3-int(((block_health[self.block_id]-self.health)*4)/block_health[self.block_id])
        self.image=block_images[self.block_id][self.frame_id]
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
        self.vector[0]+=gx_blocks
        if abs(rect.center[1]-650)>=0.2:
            self.vector[1]+=gy_blocks

        return rect.move(dx, dy)
    





def main():
    pygame.init()

    info=pygame.display.Info()

    WIDTH = info.current_w
    HEIGHT = info.current_h

    screen = pygame.display.set_mode((WIDTH, HEIGHT),pygame.FULLSCREEN)
    pygame.display.set_caption("Angry Birds Prototype")

    logo=pygame.image.load("images/pngegg.png")
    logo_adj=pygame.transform.scale(logo,(500,500))
    buttons = pygame.image.load("images/selected-buttons.png").convert_alpha()
    
    restart_btn = get_sprite(buttons, 31, 14, 115, 97)

    small_pause_btn = get_sprite(buttons, 171, 14, 217, 73)
    small_pause2_btn = get_sprite(buttons, 217, 14, 263, 73)

    play_btn = get_sprite(buttons, 266, 12, 492, 149)

    pause_btn = get_sprite(buttons, 31, 121, 114, 204)

    next_btn = get_sprite(buttons, 155, 112, 250, 217)

    play_small_btn = get_sprite(buttons, 26, 223, 110, 306)

    sound_btn = get_sprite(buttons, 154, 242, 259, 347)

    menu_btn = get_sprite(buttons, 29, 324, 113, 407)

    fast_forward_btn = get_sprite(buttons, 160, 376, 249, 465)

    play_btn_rect=play_btn.get_rect()
    play_btn_rect.topleft=(660,500)
    menu_btn_rect=menu_btn.get_rect()
    menu_btn_rect.topleft=(80,0)

    button_images = {
        "restart": restart_btn,
        "pause_small": small_pause_btn,
        "pause_small2": small_pause2_btn,
        "play": play_btn,
        "pause": pause_btn,
        "next": next_btn,
        "play_small": play_small_btn,
        "sound": sound_btn,
        "menu": menu_btn,
        "fast_forward": fast_forward_btn,
    }
    sling =pygame.image.load("images/sling-2.png").convert_alpha()
    sling_r=pygame.image.load("images/sling-2-r.png").convert_alpha()
    sling_LL=sling.subsurface((0,0,65,300))
    sling_LR=sling.subsurface((65,0,235,300))
    sling_RL=sling_r.subsurface((235,0,50,225))
    sling_RR=sling_r.subsurface((157,0,50,225))
    background=pygame.image.load("images/background.png").convert_alpha()
    birds_images=pygame.image.load("images/angry_birds.png").convert_alpha()
    red=birds_images.subsurface((180,0,619,120))
    red_birds=[]
    for i in range(5):
        red_birds.append(red.subsurface((i*75,0,75,120)))
    blue=birds_images.subsurface((210,135,300,55))
    blue_birds=[]
    for i in range(5):
        blue_birds.append(blue.subsurface((i*60,0,60,55)))
    yellow=birds_images.subsurface((186,205,400,85))
    yellow_birds=[]
    for i in range(5):
        yellow_birds.append(yellow.subsurface((i*78,0,78,85)))
    black=birds_images.subsurface((115,305,575,105))
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
        state="on_sling",
        bird_id=2,
        frame_id=0,
        position=(330, 500),
        vector=[0,0],
        reverse=False
    )
    bird2=Bird(
        state="on_sling",
        bird_id=3,
        frame_id=0,
        position=(1110,500),
        vector=[0,0],
        reverse=True
        
    )
    birds=[bird1,bird2]
    bird_sprites=pygame.sprite.Group()
    block_sprites=pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    player1_blocks=pygame.sprite.Group()
    player2_blocks=pygame.sprite.Group()
    sprite_groupofblocks=[player1_blocks,player2_blocks]
    all_sprites.add(bird1)
    all_sprites.add(bird2)
    bird_sprites.add(bird1)
    bird_sprites.add(bird2)
    for x in p1_blocks:
        all_sprites.add(x)
        block_sprites.add(x)
        player1_blocks.add(x)

    for x in p2_blocks:
        all_sprites.add(x)
        block_sprites.add(x)
        player2_blocks.add(x)

    running = True
    players=[1,2]
    player=1
    if player==1:
        p_bird=bird1
    else:
        p_bird=bird2
    last_click=0
    sling_angle=0
    STATE="home"

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if p_bird.rect.collidepoint(event.pos):
                    current_click=pygame.time.get_ticks()
                    if current_click-last_click<=DOUBLE_CLICK_TIME:
                        STATE="sling_op"
                        p_bird.state="sling_op"
                    last_click=current_click
                elif STATE=="home" and play_btn_rect.collidepoint(event.pos):
                    STATE="idle"
                


            if STATE=="sling_op" and event.type== pygame.MOUSEBUTTONUP:
                STATE="sling_op1"
                p_bird.state="sling_op1"
                p_bird.vector=[(slings_centers[player-1][0]-p_bird.rect.center[0])*0.2,(+slings_centers[player-1][1]-p_bird.rect.center[1])*0.2]
                p_bird=birds[player%2]
                player=players[player%2]
                sling_op_time=pygame.time.get_ticks()


        


        all_sprites.update()

        screen.fill((255, 255, 255))
        
        if STATE=="idle":
            screen.blit(background,(80,0))
            screen.blit(button_images["pause"],(0,0))
        # screen.blit(sling,(300,460))
            screen.blit(sling_LR,(290,460))
            screen.blit(sling_RR,(1070,460))
            isthere_collision=False
            for block_check in sprite_groupofblocks[player-1]:
                if birds[player%2].rect.colliderect(block_check.rect):
                    isthere_collision=True
                    block_check.health-=(birds[player%2].damage[block_check.block_id])*3
                    if block_check.health<=0:
                        sprite_groupofblocks[player-1].remove(block_check)
                        all_sprites.remove(block_check)
                        block_sprites.remove(block_check)
            if isthere_collision:
                # bird_sprites.remove(birds[player%2])
                # all_sprites.remove(birds[player%2])
                birds[player%2].change_bird(random.randint(0,3),0,"on_sling")
                birds[player%2].vector=[0,0]
                birds[player%2].move(slings_centers[player%2])
                
                    
            all_sprites.draw(screen)
            screen.blit(sling_LL,(279,460))
            screen.blit(sling_RL,(1093,460))
        elif STATE=="sling_op":
            screen.blit(background,(80,0))
            screen.blit(button_images["pause"], (0, 0))

        # screen.blit(sling,(300,460))
            screen.blit(sling_LR,(290,460))
            screen.blit(sling_RR,(1070,460))
            p_bird.move(pygame.mouse.get_pos())
            deltax=-p_bird.rect.center[0]+slings_centers[player-1][0]
            deltay=-p_bird.rect.center[1]+slings_centers[player-1][1]
            r=(deltax**2+deltay**2)**0.5
            if r>60:
                p_bird.move((slings_centers[player-1][0]-deltax*60/r,slings_centers[player-1][1]-deltay*60/r))
            block_sprites.draw(screen)
            slingpointR=slingpoints[player-1][1]
            slingpointL=slingpoints[player-1][0]
            pygame.draw.line(screen,(90,50,20),slingpointR,(p_bird.rect.center[0]-40*deltax/r,p_bird.rect.center[1]-40*deltay/r),10)
            bird_sprites.draw(screen)
            pygame.draw.line(screen,(90,50,20),slingpointL,(p_bird.rect.center[0]-40*deltax/r,p_bird.rect.center[1]-40*deltay/r),10)
            screen.blit(sling_LL,(279,460))
            screen.blit(sling_RL,(1093,460))
        elif STATE=="sling_op1":
            screen.blit(background,(80,0))
            screen.blit(button_images["pause"], (0, 0))

        # screen.blit(sling,(300,460))
            screen.blit(sling_LR,(290,460))
            screen.blit(sling_RR,(1070,460))
            block_sprites.draw(screen)
            if pygame.time.get_ticks()-sling_op_time>=110:
                birds[player%2].state="movement"
                STATE="launched"
            bird_sprites.draw(screen)
            screen.blit(sling_LL,(279,460))
            screen.blit(sling_RL,(1093,460))
        elif STATE=="home":
            screen.blit(background,(80,0))
            screen.blit(button_images["play"],play_btn_rect.topleft)
            screen.blit(logo_adj,(500,0))
            screen.blit(button_images["menu"],(80,0))
        elif STATE=="launched":
            screen.blit(background,(80,0))
            screen.blit(button_images["pause"],(0,0))
        # screen.blit(sling,(300,460))
            screen.blit(sling_LR,(290,460))
            screen.blit(sling_RR,(1070,460))
            isthere_collision=False
            for block_check in sprite_groupofblocks[player-1]:
                if birds[player%2].rect.colliderect(block_check.rect):
                    isthere_collision=True
                    block_check.health-=(birds[player%2].damage[block_check.block_id])*3
                    if block_check.health<=0:
                        sprite_groupofblocks[player-1].remove(block_check)
                        all_sprites.remove(block_check)
                        block_sprites.remove(block_check)
            # if birds[player%2].vector==[0,0]:
            #     STATE="idle"
            if isthere_collision:
                # bird_sprites.remove(birds[player%2])
                # all_sprites.remove(birds[player%2])
                
                birds[player%2].change_bird(random.randint(0,3),0,"on_sling")
                birds[player%2].vector=[0,0]
                birds[player%2].move(slings_centers[player%2])
                
                    
            all_sprites.draw(screen)
            screen.blit(sling_LL,(279,460))
            screen.blit(sling_RL,(1093,460))
            
        
        # pygame.draw.circle(screen,(65,0,0),slings_centers[0],5)
        # pygame.draw.circle(screen,(65,0,0),bird1.rect.center,5)
        # pygame.draw.circle(screen,(65,0,0),slings_centers[1],5)
        # pygame.draw.circle(screen,(65,0,0),bird2.rect.center,5)
        pygame.display.flip()

        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()

#birds individul gravity