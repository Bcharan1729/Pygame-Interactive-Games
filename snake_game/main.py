import pygame
import random
import math
pygame.init()
run=True
width=800
height=600
screen=pygame.display.set_mode((width,height))
font=pygame.font.SysFont("Arial", 30)
txt=font.render("Game Over",True,(255,0,0))
txt_rect=txt.get_rect(center=(width/2,height/2))
pygame.display.set_caption("time_pass")
clock=pygame.time.Clock()
font=pygame.font.SysFont("Arial", 30)
class Rectangle():
    def __init__(self,x,y,width,height):
        self.x=x
        self.y=y
        self.width=width
        self.height=height
    @property
    def rect(self):
        return pygame.Rect(self.x,self.y,self.width,self.height)
    @property
    def center(self):
        return (self.x+self.width/2,self.y+self.height/2)
direction=[1,0]
trace=[]
trace.append([Rectangle(0,0,50,50),direction])
speed=200
t=0
score=0
collide=False
gameover=False
while run:
    screen.fill((0,0,0))
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            run=False
        if event.type==pygame.KEYDOWN:
            if pygame.key.get_pressed()[pygame.K_UP] and trace[0][1][1]==0 :
                trace[0][1][0]=0
                trace[0][1][1]=-1
            if pygame.key.get_pressed()[pygame.K_DOWN] and trace[0][1][1]==0:
                trace[0][1][0]=0
                trace[0][1][1]=1
            if pygame.key.get_pressed()[pygame.K_LEFT] and trace[0][1][0]==0:
                trace[0][1][0]=-1
                trace[0][1][1]=0
            if pygame.key.get_pressed()[pygame.K_RIGHT] and trace[0][1][0]==0:
                trace[0][1][0]=1
                trace[0][1][1]=0
    if t%15==0:            
        for i in range(len(trace)-1):
            trace[len(trace)-i-1]=[Rectangle(trace[len(trace)-i-2][0].x,trace[len(trace)-i-2][0].y,50,50),trace[len(trace)-i-2][1]]
        trace[0][0]=Rectangle(trace[0][0].x+trace[0][1][0]*(speed/4),trace[0][0].y+trace[0][1][1]*(speed/4),50,50)
    
        
    if trace[0][0].x<0 or trace[0][0].x>width-trace[0][0].width or trace[0][0].y<0 or  trace[0][0].y>height-trace[0][0].height:
        gameover=True
    
    if  t==0 or collide==True:
        x=random.randint(10,790)
        y=random.randint(10,590)
        target=Rectangle(x,y,20,20)
        collide=False
    if gameover==False:    
        pygame.draw.rect(screen,(255,255,0),target)
    if -50<trace[0][0].x-x<20 and -50<(trace[0][0].y-y)<20:
        score+=1
        a=trace[len(trace)-1][1][0]
        b=trace[len(trace)-1][1][1]
        trace.append([Rectangle(trace[len(trace)-1][0].center[0]-a*50-25,trace[len(trace)-1][0].center[1]-b*50-25,50,50),[a,b]])
        collide=True 
    if gameover==False:
        for i in range(len(trace)):
            pygame.draw.rect(screen,(255,0,0),trace[i][0])
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))  
        score_rect = score_text.get_rect(topleft=(10,10))
        screen.blit(score_text, score_rect)
    for i in  range(1,len(trace)):
        if trace[0][0].rect.colliderect(trace[i][0]):
            gameover=True
    if gameover:
        score_text1=font.render(f"score:{score}",True,(255,255,255))
        score_rect1=score_text.get_rect(center=(width/2,height/2))
        screen.blit(score_text1,score_rect1)
        score_textg=font.render("Game Over",True,(255,0,0))
        score_rectg=score_textg.get_rect()
        score_rectg.x=width/2-50
        score_rectg.y=height/2-50
        screen.blit(score_textg,score_rectg)

    pygame.display.flip()
    clock.tick(60)
    t+=1
pygame.quit()  