import pygame
import sys

pygame.init()
SCREEN = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Truss Simulator - Structural Visualizer")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

nodes = []
members = []
supports = {}
loads = {}
selected_node = None

running = True
while running:
    pos = pygame.mouse.get_pos()
    SCREEN.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
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

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            for i, node in enumerate(nodes):
                if ((node[0] - pos[0])**2 + (node[1] - pos[1])**2)**0.5 < 15:
                    members = [m for m in members if i not in m]
                    
                    updated_members = []
                    for n1, n2 in members:
                        new_n1 = n1 - 1 if n1 > i else n1
                        new_n2 = n2 - 1 if n2 > i else n2
                        updated_members.append((new_n1, new_n2))
                    members = updated_members

                    nodes.pop(i)
                    if i in supports:
                        del supports[i]
                    if i in loads:
                        del loads[i]

                    if selected_node == i:
                        selected_node = None
                    elif selected_node is not None and selected_node > i:
                        selected_node -= 1

                    break
        elif event.type == pygame.KEYDOWN:
            hovered_node = None
            for i, node in enumerate(nodes):
                if ((node[0] - pos[0])**2 + (node[1] - pos[1])**2)**0.5 < 15:
                    hovered_node = i
                    break

            if hovered_node is not None:
                if event.key == pygame.K_s:
                    supports[hovered_node] = 'fixed'
                    print("Added fixed support at node", hovered_node)
                elif event.key == pygame.K_h:
                    supports[hovered_node] = 'hinge'
                    print("Added hinge support at node", hovered_node)
                elif event.key == pygame.K_r:
                    if hovered_node in supports:
                        del supports[hovered_node]
                        print("Removed support from node", hovered_node)
                elif event.key == pygame.K_l:
                    loads[hovered_node] = (0, -100)
                    print("Added load at node", hovered_node)
                elif event.key == pygame.K_d:
                    if hovered_node in loads:
                        del loads[hovered_node]
                        print("Removed load from node", hovered_node)

    for i, s_type, in supports.items():
        if s_type == 'fixed':
            pygame.draw.rect(SCREEN, GREEN, (nodes[i][0] - 10, nodes[i][1] - 10, 20, 20))
        elif s_type == 'hinge':
            pygame.draw.circle(SCREEN, GREEN, nodes[i], 10)
            pass

    for member in members:
        pygame.draw.line(SCREEN, BLACK, nodes[member[0]], nodes[member[1]], 3)

    for i, node in enumerate(nodes):
        color = BLUE if i == selected_node else BLACK
        pygame.draw.circle(SCREEN, color, node, 6)

    pygame.display.flip()

pygame.quit()
sys.exit()