from logic import Agent
import random
import pygame

class Player:
    def __init__(self, agent : Agent, x : int, y : int, width : int, height : int) -> None:
        self.agent = agent
        self.x = x
        self.y = y
        self.org_y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect([self.x,self.y-self.height,self.width,self.height])
        self.surface = pygame.Surface((self.width,self.height))
        self.surface.set_alpha(32)
        self.surface.fill("black")
        self.alive = True
        self.jumps = 0
        self.obstacles = 0
        self.vert_speed = 0.0
    
    def update(self, obstacles, speed):
        self.agent.fitness += 1 + (speed-7.5)
        self.agent.fitness = round(self.agent.fitness, 2)
        if self.rect.colliderect(min(obstacles, key=lambda x: x.x)) == True:
            self.alive = False
            self.agent.fitness -= ((self.jumps-self.obstacles)*100) if ((self.jumps-self.obstacles)*100) < 0 else 0
            if self.agent.fitness < 0:
                self.agent.fitness = 0
        self.y -= self.vert_speed
        if self.y < self.org_y:
            self.vert_speed -= 1
        else:
            self.y = self.org_y
            self.vert_speed = 0
            
    def next_obstacle(self, obstacles) -> tuple[int,int,int]:
        try:
            ob_x = min([obstacle for obstacle in obstacles if obstacle.x > self.x], key=lambda x: x.x)
        except:
            return (0,0,0)
        return (ob_x.x-self.x, ob_x.height, ob_x.y)
    
    def jump(self):
        if self.y == self.org_y:
            self.jumps += 1
            self.vert_speed = 17

class Obstacle:
    def __init__(self, x : int, y : int, width : int, height : int) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect([self.x,self.y-self.height,self.width,self.height])
        self.surface = pygame.Surface((self.width,self.height))
        self.surface.fill("black")
    
    def update(self, speed):
        self.x -= speed