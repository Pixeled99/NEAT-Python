from logic import *
from game_logic import Player, Obstacle
import pygame
import math
import numpy as np
import random

speed = 7.5
accel = 10

pygame.init()
screen = pygame.display.set_mode((1200, 800))
clock = pygame.time.Clock()
running = True
frames = 0
generation = 1
pop_size = 250
next = 2000
best_score = (0,0)

agents = [Agent(3, 1, Node.tanh, 1, Node.ReLu) for _ in range(pop_size)]
players : list[Player] = [Player(i, 50, screen.get_height(), 50, 50) for i in agents]
best_player = sorted([p for p in players if p.alive], key=lambda x : x.agent.fitness)[-1]
agent = best_player.agent
graph = agent.graph
obstacles : list[Obstacle] = []

while running:
    neural_x, neural_y = screen.get_width(), (screen.get_height()/4)*3
    screen.fill("white")
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                [player.jump() for player in players]
            
    ### GAME

    if len(obstacles) == 0:
        above = random.choice((True, False))
        obstacle = Obstacle(screen.get_width(), screen.get_height(), 20, random.randrange(75,125))
        if above:
            obstacle = Obstacle(screen.get_width(), screen.get_height()-50, 20, random.randrange(25,80))
        obstacles.append(obstacle)
        for player in players:
            if player.alive:
                player.obstacles += 1
    for player in players:
        if player.alive:
            player.update(obstacles, speed)
            if player.agent.graph.run([(player.next_obstacle(obstacles)[0]/500), 1.0 if player.next_obstacle(obstacles)[2] == screen.get_height() else 0.0, (speed-7.5)/10])[0] > 0.5:
                player.jump()
            player.rect = screen.blit(player.surface, (player.x,player.y-player.height))
            if player.agent.fitness >= best_score[0]:
                best_score = (player.agent.fitness,generation)
    if len([player.alive for player in players if player.alive]) != 0:
        for obstacle in obstacles:
            obstacle.update(speed)
            if obstacle.x < 0:
                next = random.randrange(300,600)
                obstacles.remove(obstacle)
            obstacle.rect = screen.blit(obstacle.surface, (obstacle.x,obstacle.y-obstacle.height))
    
    font = pygame.font.SysFont('Ariel', 40)
    text_surface = font.render(f"Generation {generation}", False, "black")
    screen.blit(text_surface, (0,0))
    text_surface7 = font.render(f"Top Score {round(best_score[0],2)} - {best_score[1]}", False, "black")
    screen.blit(text_surface7, (0,text_surface.get_height()))
    text_surface2 = font.render(f"Fitness {best_player.agent.fitness}", False, "black")
    screen.blit(text_surface2, (screen.get_width()-text_surface2.get_width(),0))
    text_surface3 = font.render(f"Alive {len([i for i in players if i.alive])}", False, "black")
    screen.blit(text_surface3, (screen.get_width()-text_surface3.get_width(),text_surface2.get_height()))
    text_surface4 = font.render(f"Obstacles {best_player.obstacles}", False, "black")
    screen.blit(text_surface4, (screen.get_width()-text_surface4.get_width(),text_surface2.get_height()+text_surface3.get_height()))
    text_surface5 = font.render(f"Speed {round(speed,2)}", False, "black")
    screen.blit(text_surface5, (screen.get_width()-text_surface5.get_width(),text_surface2.get_height()+text_surface3.get_height()+text_surface4.get_height()))
    text_surface6 = font.render(f"Acceleration {round(accel/1000,4)}", False, "black")
    screen.blit(text_surface6, (screen.get_width()-text_surface6.get_width(),text_surface2.get_height()+text_surface3.get_height()+text_surface4.get_height()+text_surface5.get_height()))
    
    pos_dict = {}
    radius = neural_y/max([len(nodes) for nodes in graph.nodes])/3/len(graph.nodes)
    font = pygame.font.SysFont('Ariel', int(radius))
    agent = best_player.agent
    graph = agent.graph
    for row, node_list in enumerate(graph.nodes):
        y = neural_y/len(node_list)/2
        for node in node_list:
            pos_x, pos_y = row*(neural_x/len(graph.nodes))+(neural_x/len(graph.nodes)/2),y
            pygame.draw.circle(screen, "black", (pos_x,pos_y), radius)
            pos_dict[node] = (pos_x, pos_y)
            for connection in node.con_from:
                node_from = connection.node
                weight = connection.weight
                if weight >= 0:
                    pygame.draw.line(screen, "green", (pos_x,pos_y), pos_dict[node_from], int(radius/4.0*(abs(weight))) if int(radius/4.0*(abs(weight))) > 0 else 1)
                else:
                    pygame.draw.line(screen, "red", (pos_x,pos_y), pos_dict[node_from], int(radius/4.0*(abs(weight))) if int(radius/4.0*(abs(weight))) > 0 else 1)
                mid_x = (pos_x + pos_dict[node_from][0])/2
                dif_x = pos_x - pos_dict[node_from][0]
                mid_y = (pos_y + pos_dict[node_from][1])/2
                dif_y = pos_dict[node_from][1] - pos_y
                hype = np.sqrt(dif_x**2 + dif_y**2)
                degrees = math.degrees(math.asin(dif_y/hype))
                new_font = pygame.font.SysFont('Ariel', int(radius/2))
                text_surface = new_font.render(str(weight), False, "black")
                text_surface = pygame.transform.rotate(text_surface, degrees)
                screen.blit(text_surface, (mid_x-text_surface.get_width()/2,mid_y-text_surface.get_height()/2))
            y += neural_y/len(node_list)
    for _, node_list in enumerate(graph.nodes[1:]):
        for node in node_list:
            text_surface = font.render(str(node.bias), False, "white")
            screen.blit(text_surface, (pos_dict[node][0]-text_surface.get_width()/2,pos_dict[node][1]-text_surface.get_height()/2))
            small_font = pygame.font.SysFont('Ariel', int(radius/3))
            text_surface2 = small_font.render(node.function.__name__, False, "white")
            screen.blit(text_surface2, (pos_dict[node][0]-text_surface2.get_width()/2,pos_dict[node][1]-text_surface2.get_height()/2+text_surface.get_height()/2))
            
    if len([player.alive for player in players if player.alive]) == 0:
        next = 2000
        speed = 7.5
        accel = 10
        next_pop = []
        top = int(len(agents)*0.3)
        next_pop.extend(agents[:top])
        while len(next_pop) != pop_size:
            arr = np.array([agent.fitness+1 for agent in agents])
            arr = arr / sum(arr)
            index = np.random.choice(len(arr), p=arr)
            pos_dict = {}
            new_agent = Agent(agents[index].inputs, agents[index].outputs, agents[index].output_func, agents[index].hidden_max, agents[index].hidden_func)
            new_agent.graph.nodes = []
            for i, row in enumerate(agents[index].graph.nodes):
                new_agent.graph.nodes.append([])
                for j, node in enumerate(row):
                    pos_dict[node] = (i,j)
                    new_agent.graph.nodes[-1].append(Node(node.function, node.bias, 0.0, []))
            for i, row in enumerate(agents[index].graph.nodes):
                for j, node in enumerate(row):
                    for connection in node.con_to:
                        con_to = connection.node
                        location_to = pos_dict[con_to]
                        new_agent.graph.nodes[i][j].con_to.append(Connection(new_agent.graph.nodes[location_to[0]][location_to[1]], connection.weight))
                        new_agent.graph.nodes[location_to[0]][location_to[1]].con_from.append(Connection(new_agent.graph.nodes[i][j], connection.weight))
            new_agent.mutate()
            next_pop.append(new_agent)
        agents = next_pop
        for agent in agents:
            agent.fitness = 0
        generation += 1
        players : list[Player] = [Player(i, 50, screen.get_height(), 50, 50) for i in agents]
        obstacles : list[Obstacle] = []

    best_player = sorted([p for p in players if p.alive], key=lambda x : x.agent.fitness)[-1]
    speed += accel/1000
    speed = min(speed, 30)
        
    pygame.display.flip()

    clock.tick(60)

pygame.quit()