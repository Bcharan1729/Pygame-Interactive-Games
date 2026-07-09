class RedBird(pygame.sprite.Sprite):
    def __init__(self, position, vector):
        super().__init__()

        self.image = pygame.image.load(
            "images/red-bird.png"
        ).convert_alpha()

        self.rect = self.image.get_rect()
        self.rect.center = position

        self.vector = vector

        self.mass = 5
        self.damage = [10, 10, 10]

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


class Chuck(pygame.sprite.Sprite):
    def __init__(self, position, vector):
        super().__init__()

        self.image = pygame.image.load(
            "images/red-bird.png"
        ).convert_alpha()

        self.rect = self.image.get_rect()
        self.rect.center = position

        self.vector = vector

        self.mass = 3
        self.damage = [7, 16, 7]

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


class Blues(pygame.sprite.Sprite):
    def __init__(self, position, vector):
        super().__init__()

        self.image = pygame.image.load(
            "images/red-bird.png"
        ).convert_alpha()

        self.rect = self.image.get_rect()
        self.rect.center = position

        self.vector = vector

        self.mass = 1
        self.damage = [15,5,5]

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


class Bomb(pygame.sprite.Sprite):
    def __init__(self, position, vector):
        super().__init__()

        self.image = pygame.image.load(
            "images/red-bird.png"
        ).convert_alpha()

        self.rect = self.image.get_rect()
        self.rect.center = position

        self.vector = vector

        self.mass = 7
        self.damage = [8,8,16]

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