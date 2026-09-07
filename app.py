import pygame
import sys
import numpy as np

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
displacement = []
scale_factor = 50
selected_node = None

# matrices and whatever
def get_member_length_and_cosines(node1, node2):
    x1, y1 = node1
    x2, y2 = node2
    
    y1_cartesian = -y1
    y2_cartesian = -y2
    
    length = ((x2 - x1)**2 + (y2_cartesian - y1_cartesian)**2)**0.5
    cos_theta = (x2 - x1) / length
    sin_theta = (y2_cartesian - y1_cartesian) / length 
    
    return length, cos_theta, sin_theta

def get_local_stiffness(node1, node2, EA=999999999):
    length, c, s = get_member_length_and_cosines(node1, node2)
    
    # stiffness stiffness factor (E = material stiffness, A = cross-sectional area)
    stiffness = EA / length
    
    stiffness_matrix = stiffness * np.array([
    [ c*c,  c*s, -c*c, -c*s],  # node 1 x-direction
    [ c*s,  s*s, -c*s, -s*s],  # node 1 y-direction
    [-c*c, -c*s,  c*c,  c*s],  # node 2 x-direction
    [-c*s, -s*s,  c*s,  s*s]   # node 2 y-direction
])
        
    return stiffness_matrix

running = True
while running:
    pos = pygame.mouse.get_pos()
    SCREEN.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

# creating nodes, loads and supports
        
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

# deleting nodes, loads and supports

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

                    new_supports = {}
                    for k,v in list(supports.items()):
                        if k == i:
                            continue
                        elif k > i:
                            new_supports[k-1] = v
                        else:
                            new_supports[k] = v
                    supports = new_supports

                    new_loads = {}
                    for k,v in list(loads.items()):
                        if k == i:
                            continue
                        elif k > i:
                            new_loads[k-1] = v
                        else:
                            new_loads[k] = v
                    loads = new_loads

                    #if i in supports:
                        #del supports[i]
                    #if i in loads:
                        #del loads[i]

                    # ^ this code didnt work if there were more than one loads/supports, so i rewrote it above....

                    if selected_node == i:
                        selected_node = None
                    elif selected_node is not None and selected_node > i:
                        selected_node -= 1

                    break

# removing nodes

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                        num_nodes = len(nodes)
                        if num_nodes < 2:
                            print("Need at least 2 nodes to solve")
                        else:
                            num_dofs = 2 * num_nodes
                                    
                            # fill each matrices with zeros
                            stiffness_global = np.zeros((num_dofs, num_dofs))
                            forces_global = np.zeros(num_dofs)
                                    
                            # add each of the local stiffnesses to stiffness_global
                            for n1, n2 in members:
                                k_elem = get_local_stiffness(nodes[n1], nodes[n2])
                                        
                                # translating each node's (x,y) positions to DOF
                                dofs = [2*n1, 2*n1 + 1, 2*n2, 2*n2 + 1]
                                        
                                for r in range(4):
                                    for c in range(4):
                                        stiffness_global[dofs[r], dofs[c]] += k_elem[r, c]
            
                            # add forces to force_global
                            for node_idx, force in loads.items():
                                forces_global[2 * node_idx] += force[0]       # X force
                                forces_global[2 * node_idx + 1] += -force[1]  # Y force (inverted for Cartesian)
            
                            print("global stiffness matrix assembled Shape:", stiffness_global.shape)
                            print("global force vector F:", forces_global)

                            #differentiate fixed and hinge supports
                            fixed_dofs = []
                            for node_idx, support_type in supports.items():
                                if support_type == 'fixed':
                                    fixed_dofs.extend([2 * node_idx, 2 * node_idx + 1]) # both x and y directions are fixed for fixed support
                                elif support_type == 'hinge':
                                    fixed_dofs.append(2 * node_idx + 1)  # only y direction is fixed for hinge

                            free_dofs = []
                            for dof in range(num_dofs):
                                if dof not in fixed_dofs:
                                    free_dofs.append(dof)

                            if len(free_dofs) == 0:
                                print("all dof fixed")
                            else:
                                try:
                                    stiffness_free = stiffness_global[free_dofs][:, free_dofs]
                                    forces_free = forces_global[free_dofs]
                                    displacement_free = np.linalg.solve(stiffness_free, forces_free)
                                    displacement = np.zeros(num_dofs)
                                    for i, dof in enumerate(free_dofs):
                                        displacement[dof] = displacement_free[i]
                                    for i in range(num_nodes):
                                        dx = displacement[2 * i]
                                        dy = displacement[2 * i + 1]
                                        print(f"Node {i}: Displacement dx = {dx:.4f}, dy = {dy:.4f}")
                                except np.linalg.LinAlgError:
                                    print("error! structure is unstable or unsupported")


            
            else:
                hovered_node = None
                for i, node in enumerate(nodes):
                    if ((node[0] - pos[0])**2 + (node[1] - pos[1])**2)**0.5 < 15:
                        hovered_node = i
                        break

# assigning supports and loads

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


# rendering

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

    for i, force in loads.items():
        nx, ny = nodes[i]
        pygame.draw.line(SCREEN, RED, (nx, ny - 40), (nx, ny), 3)
        pygame.draw.polygon(SCREEN, RED, [(nx, ny), (nx - 6, ny - 12), (nx + 6, ny - 12)])

    pygame.display.flip()

pygame.quit()
sys.exit()