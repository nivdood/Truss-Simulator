import pygame
import sys

pygame.init()
SCREEN = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Truss Simulator - Structural Visualizer")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 102, 204)

nodes = []
members = []
selected_node = None

running = True
while running:
    SCREEN.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            clicked_node = None
            for i, node in enumerate(nodes):
                if ((node[0] - pos[0])**2 + (node[1] - pos[1])**2)**0.5 < 15:
                    clicked_node = i
                    break
            
            if clicked_node is None:
                nodes.append(pos)
            else:
                if selected_node is None:
                    selected_node = clicked_node
                else:
                    if selected_node != clicked_node:
                        members.append((selected_node, clicked_node))
                    selected_node = None

    for member in members:
        pygame.draw.line(SCREEN, BLACK, nodes[member[0]], nodes[member[1]], 3)

    for i, node in enumerate(nodes):
        color = BLUE if i == selected_node else BLACK
        pygame.draw.circle(SCREEN, color, node, 6)

    pygame.display.flip()

pygame.quit()
sys.exit()