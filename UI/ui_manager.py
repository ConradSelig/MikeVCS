import pygame
import math

from random import randint
from CSUtils import Switch


class QueueHandler:
    data_fields = []  # modules, nodes, events, wheel_center, midpoints
    connections = []  # list of tuples; ([modules], event, priority)
    queue = []  # list of tuples; ([modules])

    modules = []
    nodes = []
    events = []

    columns = [1, 2, 3, 1, 2, 3]
    next_priority = 0

    def __init__(self):
        self.data_fields = list(setup_display())
        self.modules = self.data_fields[0]
        self.nodes = self.data_fields[1]
        self.events = self.data_fields[2]

    def make_connections(self):
        self.__add_connections()
        # for every connection
        for connection in sorted(self.connections, key=lambda l:l[2], reverse=True):
            # for each module in that connection
            for module in connection[0]:
                # give the event index to that module
                setattr(self.nodes[module], "event", connection[1])
                # give the column index to that module, adjusted for 0 based indexing
                setattr(self.nodes[module], "column", self.columns[connection[1] - 1])

    def __add_connections(self):
        for request in self.queue:
            try:
                connected_events = [[conn[1] - 1 for conn in self.connections]][0]
            except IndexError:
                connected_events = []
            for event_index in range(6):
                if event_index not in connected_events:
                    self.connections.append((request, event_index + 1, self.next_priority))
                    self.queue.remove(request)
                    self.next_priority += 1
                    return

    def request_connection(self, modules):
        for index, module in enumerate(modules):
            with Switch(module) as case:
                if case("Display"):
                    modules[index] = 3
                elif case("AI"):
                    modules[index] = 4
                elif case("Email"):
                    modules[index] = 6
                elif case("Habit"):
                    modules[index] = 1
                elif case("Main"):
                    modules[index] = 2
                elif case("Database"):
                    modules[index] = 5
        self.queue.append([module - 1 for module in modules])

    def close_connection(self, event_index):
        for connection in self.connections:
            if connection[1] == event_index:
                # reset the nodes so the connection is not displayed
                for module in connection[0]:
                    setattr(self.nodes[module], "event", 0)
                    setattr(self.nodes[module], "column", 0)
                self.connections.remove(connection)


class Module:
    name = ""
    public_key = ""
    event_private_key = 0

    def __init__(self, name, public_key):
        self.name = name
        self.public_key = public_key

    def __str__(self):
        return str(self.public_key) + ": " + str(self.name)


class Event:
    public_key = 0
    node_loc = (0, 0)
    width = 0
    color = ()
    column_nodes = []

    def __init__(self, public_key, node_loc, width):
        self.public_key = public_key
        self.node_loc = node_loc
        self.width = width
        self.referenced = False

    def draw(self):
        if self.public_key in [conn[1] for conn in getattr(QueueHandler, "connections")]:
            #pygame.draw.ellipse(SCREEN, BLUE, (self.node_loc[0] - 8, self.node_loc[1] - 8, 16, 16), 4)
            direction = 1
            if self.node_loc[1] > Y_CENTER:
                direction = -1
            ''' body '''
            body = pygame.Rect((self.node_loc[0] - self.width / 4) + self.width / 16,
                               (Y_CENTER - (Y_CENTER * direction) + (15 * direction)) if direction > 0 else self.node_loc[
                                   1],
                               ((self.node_loc[0] + self.width / 4) - self.width / 16) - (
                                           (self.node_loc[0] - self.width / 4) + self.width / 16),
                               (Y_CENTER - (Y_CENTER - self.node_loc[1]) - 15) if direction > 0 else SIZE[1] -
                                                                                                     self.node_loc[1] - 15)
            SCREEN.fill(LIGHT_BACK, rect=body)
            ''' bottom line '''
            pygame.draw.line(SCREEN, self.color,
                             ((self.node_loc[0] - self.width / 4) + self.width / 16, self.node_loc[1]),
                             ((self.node_loc[0] + self.width / 4) - self.width / 16, self.node_loc[1]),
                             8)
            ''' top line '''
            pygame.draw.line(SCREEN, self.color,
                             ((self.node_loc[0] - self.width / 4) + self.width / 16,
                              Y_CENTER - (Y_CENTER * direction) + (15 * direction)),
                             ((self.node_loc[0] + self.width / 4) - self.width / 16,
                              Y_CENTER - (Y_CENTER * direction) + (15 * direction)),
                             8)
            ''' left bottom bump '''
            pygame.draw.line(SCREEN, self.color,
                             ((self.node_loc[0] - self.width / 4) + self.width / 16, self.node_loc[1]),
                             ((self.node_loc[0] - self.width / 4) + self.width / 64,
                              self.node_loc[1] - self.width / 32 * direction),
                             8)
            ''' right bottom bump '''
            pygame.draw.line(SCREEN, self.color,
                             ((self.node_loc[0] + self.width / 4) - self.width / 16, self.node_loc[1]),
                             ((self.node_loc[0] + self.width / 4) - self.width / 64,
                              self.node_loc[1] - self.width / 32 * direction),
                             8)
            ''' left top bump '''
            pygame.draw.line(SCREEN, self.color,
                             ((self.node_loc[0] - self.width / 4) + self.width / 16,
                              Y_CENTER - (Y_CENTER * direction) + (15 * direction)),
                             ((self.node_loc[0] - self.width / 4) + self.width / 64,
                              (Y_CENTER - (Y_CENTER * direction) + (15 * direction)) - self.width / 32 * -direction),
                             8)
            ''' right top bump '''
            pygame.draw.line(SCREEN, self.color,
                             ((self.node_loc[0] + self.width / 4) - self.width / 16,
                              Y_CENTER - (Y_CENTER * direction) + (15 * direction)),
                             ((self.node_loc[0] + self.width / 4) - self.width / 64,
                              (Y_CENTER - (Y_CENTER * direction) + (15 * direction)) - self.width / 32 * -direction),
                             8)


class Node:
    private_key = 0
    path_index = 0
    location = (0, 0)

    def __init__(self, private_key, path_index):
        self.private_key = private_key
        self.path_index = path_index

    def __str__(self):
        return str(self.private_key) + ": " + str(self.path_index) + ". " + str(self.location)


class NodeSet:
    nodes = []
    column = 0  # 1 - 3
    event = 0 # 1 - 6

    def __init__(self, nodes):
        self.nodes = nodes

    def __getattribute__(self, item):
        if item == "all nodes":
            return object.__getattribute__(self, "nodes")
        elif item == "nodes":
            return object.__getattribute__(self, item)[0:5 + object.__getattribute__(self, "column")]
        return object.__getattribute__(self, item)

    def __getitem__(self, index):
        return self.nodes[index]


BACKGROUND = (9, 17, 27)
LIGHT_BACK = (16, 28, 43)
GREEN = (17, 180, 147)
RED = (194, 68, 78)
BLUE = (56, 165, 205)
DARK_BLUE = (33, 102, 127)

pygame.init()
pygame.font.init()

infoObject = pygame.display.Info()
SIZE = (infoObject.current_w, infoObject.current_h)
X_CENTER = SIZE[0]/2
Y_CENTER = SIZE[1]/2

SCREEN = pygame.display.set_mode(SIZE, pygame.FULLSCREEN)
clock = pygame.time.Clock()

TextFont = pygame.font.SysFont('Courant', 30)

def setup_display():
    modules = []
    nodes = []
    events = []

    wheel_center = (SIZE[0] / 7, Y_CENTER)

    for index, module_name in enumerate(["Global Manager", "Email Connection", "Database Management",
                                         "Schedule Management", "Habit Tracker", "AI Elements"]):
        modules.append(Module(module_name, index))

    for mod_index in range(len(modules)):
        next_set = []
        for node_index in range(8):
            next_set.append(Node(mod_index, node_index))
        nodes.append(NodeSet(next_set))

    midpoints = display_modules(wheel_center, 12.03, BLUE, calc_midpoints=True)
    setup_nodes(modules, nodes, midpoints, wheel_center)
    '''rotate node sets to index 0 is on top'''
    nodes = nodes[4:] + nodes[:4]

    top = SIZE[1] / 3 + (SIZE[1] / 24)
    bottom = (SIZE[1] / 3) * 2 - (SIZE[1] / 24)
    left = SIZE[0] / 3 + ((SIZE[0] / 3) / 3)
    right = SIZE[0] - ((SIZE[0]/3)/3)
    center = SIZE[0] / 3 + (SIZE[0] / 3)
    width = right - left

    node_locations = [(left, top),
                      (center, top),
                      (right, top),
                      (left, bottom),
                      (center, bottom),
                      (right, bottom)]
    for index in range(6):
        events.append(Event(index + 1, node_locations[index], width))
        setattr(events[-1], "color", GREEN if randint(0,1) == 0 else RED)

    ''' adds the additional 3 nodes required for event connection '''
    for index in range(3):
        for mod_index in range(len(modules)):
            offset_modifier = 0
            with Switch(mod_index) as case:
                if case(0) or case(5):
                    offset_modifier = 90
                elif case(1) or case(4):
                    offset_modifier = 60
                elif case(2) or case(3):
                    offset_modifier = 30
                setattr(getattr(nodes[mod_index], "all nodes")[5 + index], "location",
                        (node_locations[index][0] - offset_modifier, getattr(nodes[mod_index][4], "location")[1]))

    pygame.display.set_caption("Mike Diagnostics")
    pygame.display.set_icon(pygame.image.load("UI/tray_icon.jpg"))

    return modules, nodes, events, wheel_center, midpoints


def main(QueueHandlerObject, loop_count):

    modules, nodes, events, wheel_center, midpoints = getattr(QueueHandlerObject, "data_fields")

    loop_count += 1
    if loop_count == 1:
        QueueHandlerObject.make_connections()
    elif loop_count == 100:
        '''# Random generator of event connections
        close_index = randint(1,6)
        Queue.close_connection(close_index)
        new_connections = list(set([randint(1,6) for i in range(randint(1,2))]))
        if new_connections != [] and randint(0,1) == 0:
            Queue.request_connection(new_connections)
        '''
        loop_count = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise KeyboardInterrupt
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
                raise KeyboardInterrupt
            if event.key == pygame.K_ESCAPE:
                raise KeyboardInterrupt

    SCREEN.fill(BACKGROUND)

    #draw_guidelines()

    display_modules((wheel_center[0] + 2, wheel_center[1] + 2), 12.03, DARK_BLUE)
    display_modules(wheel_center, 12.03, BLUE)

    vertical_offset_dist = (getattr(nodes[1][4], "location")[1] - getattr(nodes[0][4], "location")[1]) / 2
    for index, node_set in enumerate(nodes):
        connect_nodes(node_set, BLUE, events, vertical_offset_dist)

    ''' Draw every node in module node sets
    for node_set in nodes:
        for node in getattr(node_set, "all nodes"):
                pygame.draw.ellipse(SCREEN, RED,
                                    (getattr(node, "location")[0] - 8, getattr(node, "location")[1] - 8,
                                    16, 16), 4)
    '''

    for event in events:
        event.draw()

    pygame.display.flip()

    return loop_count


def close_display():
    pygame.quit()


def draw_guidelines():
    """ placeholder """
    ''' horizontal lines '''
    pygame.draw.line(SCREEN, RED, (0, Y_CENTER), (SIZE[0], Y_CENTER), 4)  # center
    pygame.draw.line(SCREEN, RED,
                     (0, SIZE[1] / 3 + (SIZE[1] / 24)),
                     (SIZE[0], SIZE[1] / 3 + (SIZE[1] / 24)),
                     4)  # top third
    pygame.draw.line(SCREEN, RED,
                     (0, (SIZE[1] / 3) * 2 - (SIZE[1] / 24)),
                     (SIZE[0], (SIZE[1] / 3) * 2 - (SIZE[1] / 24)),
                     4)  # top third

    ''' vertical lines '''
    pygame.draw.line(SCREEN, RED, (SIZE[0] / 3, 0), (SIZE[0] / 3, SIZE[1]), 4)  # third left
    pygame.draw.line(SCREEN, RED,
                     (SIZE[0] / 3 + (SIZE[0]/3 + (SIZE[0]/3)/3), 0),
                     (SIZE[0] / 3 + (SIZE[0]/3 + (SIZE[0]/3)/3), SIZE[1]),
                     4)  # right 2/3s first third
    pygame.draw.line(SCREEN, RED,
                     (SIZE[0] / 3 + (SIZE[0]/3 - ((SIZE[0]/3)/3)), 0),
                     (SIZE[0] / 3 + (SIZE[0]/3 - ((SIZE[0]/3)/3)), SIZE[1]),
                     4)  # left 2/3s second third


def connect_nodes(node_set, color, events, vertical_offset_dist):
    if getattr(node_set, "column") != 0:
        connection_event = getattr(node_set, "event")
        if connection_event != 0:
            for event in events:
                if getattr(event, "public_key") == connection_event:
                    connection_event = event
            node_set = getattr(node_set, "nodes") + [getattr(connection_event, "node_loc")]
        else:
            node_set = getattr(node_set, "nodes")
        for index in range(len(node_set)):
            try:
                #print(Y_CENTER, getattr(node_set[index], "location"), getattr(node_set[index + 1], "location"))
                #print("--" if getattr(node_set[index], "location")[1] < Y_CENTER else "")
                #print("##" if getattr(node_set[index + 1], "location")[1] > Y_CENTER else "")
                #print(getattr(node_set[index], "location"))

                pygame.draw.line(SCREEN, color,
                         getattr(node_set[index], "location"), getattr(node_set[index + 1], "location"), 4)
            except AttributeError:
                try:
                    if getattr(node_set[index], "location")[1] < Y_CENTER < node_set[index + 1][1]:  # going down
                        #pygame.draw.ellipse(SCREEN, RED, (getattr(node_set[index], "location")[0] - 8, getattr(node_set[index], "location")[1] - 8, 16, 16), 4)

                        node_set.insert(-1, (getattr(node_set[-2],"location")[0] + 15,
                                             Y_CENTER + (Y_CENTER - getattr(node_set[4], "location")[1]) - vertical_offset_dist))

                        pygame.draw.line(SCREEN, color, node_set[-2], node_set[-1], 4)
                    elif getattr(node_set[index], "location")[1] > Y_CENTER > node_set[index + 1][1]:  # going up
                        #pygame.draw.ellipse(SCREEN, RED, (getattr(node_set[index], "location")[0] - 8, getattr(node_set[index], "location")[1] - 8, 16, 16), 4)

                        node_set.insert(-1, (getattr(node_set[-2], "location")[0] + 15,
                                             Y_CENTER - (getattr(node_set[4], "location")[1] - Y_CENTER) + vertical_offset_dist))

                        pygame.draw.line(SCREEN, color, node_set[-2], node_set[-1], 4)

                    pygame.draw.line(SCREEN, color,
                                     getattr(node_set[index], "location"), node_set[index + 1], 4)

                except (IndexError, AttributeError):
                    return node_set
            except IndexError:
                return node_set
        return node_set


def setup_nodes(modules, nodes, midpoints, wheel_center):
    for index, module in enumerate(modules):
        module_nodes = getattr(nodes[index], "nodes")

        for midpoint in midpoints:
            if midpoint[0] == getattr(module, "public_key"):
                for node in module_nodes:
                    if getattr(node, "path_index") == 0:
                        setattr(node, "location", (midpoint[1], midpoint[2]))
                        break

        for node in module_nodes:
            if getattr(node, "path_index") == 1:

                x1 = wheel_center[0]
                x2 = getattr(module_nodes[0], "location")[0]
                y1 = wheel_center[1]
                y2 = getattr(module_nodes[0], "location")[1]
                d = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)  # distance from center to module connection
                t = (d + 40) / d  # desired distance of first node.
                ''' Thank you Sen Jacob for this equation. '''
                setattr(node, "location", (((1-t) * x1) + (t * x2), ((1-t) * y1) + (t * y2)))  # new point

    for index, module in enumerate(modules):
        module_nodes = getattr(nodes[index], "nodes")

        for node in module_nodes:
            if getattr(node, "path_index") == 2:
                with Switch(getattr(module, "public_key")) as case:
                    if case(3) or case(4):
                        x1 = wheel_center[0]
                        y1 = wheel_center[1]
                        if case(3):
                            x2 = getattr(getattr(nodes[2], "nodes")[0], "location")[0]
                            y2 = getattr(getattr(nodes[2], "nodes")[0], "location")[1]
                        else:
                            x2 = getattr(getattr(nodes[5], "nodes")[0], "location")[0]
                            y2 = getattr(getattr(nodes[5], "nodes")[0], "location")[1]
                        d = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)  # distance from center to module connection
                        t = (d + 70) / d  # desired distance of first node.
                        ''' Thank you Sen Jacob for this equation. '''
                        setattr(node, "location", (((1 - t) * x1) + (t * x2), ((1 - t) * y1) + (t * y2)))  # new point
                    else:
                        setattr(node, "location", getattr(module_nodes[1], "location"))

    for index, module in enumerate(modules):
        module_nodes = getattr(nodes[index], "nodes")

        for node in module_nodes:
            if getattr(node, "path_index") == 3:
                with Switch(getattr(module, "public_key")) as case:
                    if case(3) or case(4):
                        x1 = wheel_center[0]
                        y1 = wheel_center[1]
                        if case(3):
                            x2 = getattr(getattr(nodes[1], "nodes")[0], "location")[0]
                            y2 = getattr(getattr(nodes[1], "nodes")[0], "location")[1]
                        else:
                            x2 = getattr(getattr(nodes[0], "nodes")[0], "location")[0]
                            y2 = getattr(getattr(nodes[0], "nodes")[0], "location")[1]
                        d = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)  # distance from center to module connection
                        t = (d + 100) / d  # desired distance of first node.
                        ''' Thank you Sen Jacob for this equation. '''
                        setattr(node, "location", (((1 - t) * x1) + (t * x2), ((1 - t) * y1) + (t * y2)))  # new point
                    elif case(2) or case(5):
                        x1 = wheel_center[0]
                        y1 = wheel_center[1]
                        if case(2):
                            x2 = getattr(getattr(nodes[1], "nodes")[0], "location")[0]
                            y2 = getattr(getattr(nodes[1], "nodes")[0], "location")[1]
                        else:
                            x2 = getattr(getattr(nodes[0], "nodes")[0], "location")[0]
                            y2 = getattr(getattr(nodes[0], "nodes")[0], "location")[1]
                        d = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)  # distance from center to module connection
                        t = (d + 70) / d  # desired distance of first node.
                        ''' Thank you Sen Jacob for this equation. '''
                        setattr(node, "location", (((1 - t) * x1) + (t * x2), ((1 - t) * y1) + (t * y2)))  # new point
                    else:
                        setattr(node, "location", getattr(module_nodes[1], "location"))

    for index, module in enumerate(modules):
        module_nodes = getattr(nodes[index], "nodes")
        index_distance = (Y_CENTER - (SIZE[1] / 3 + (SIZE[1] / 24))) / 4

        for node in module_nodes:
            if getattr(node, "path_index") == 4:
                with Switch(getattr(module, "public_key")) as case:
                    if case(0):
                        setattr(node, "location", (wheel_center[0] + 250, Y_CENTER - index_distance))  # 3
                    if case(1):
                        setattr(node, "location", (wheel_center[0] + 250, Y_CENTER + index_distance))  # 4
                    if case(2):
                        setattr(node, "location", (wheel_center[0] + 250, Y_CENTER + index_distance * 2))  # 5
                    if case(3):
                        setattr(node, "location", (wheel_center[0] + 250, Y_CENTER + index_distance * 3))  # 6
                    if case(4):
                        setattr(node, "location", (wheel_center[0] + 250, Y_CENTER - index_distance * 3))  # 1
                    if case(5):
                        setattr(node, "location", (wheel_center[0] + 250, Y_CENTER - index_distance * 2))  # 2


def display_modules(center, rotation, color, calc_midpoints=False):
    x_center = center[0]
    y_center = center[1]

    module_names = ["Main", "Display", "AI", "Database", "Email", "Habit"]

    midpoints = []

    last_x = 0
    last_y = 0
    last_small_x = 0
    last_small_y = 0

    for line_index in range(12):
        radar = (x_center, y_center)
        length = 175
        if line_index % 2 == 0:
            print_name = True
            name = module_names[int(line_index/2)]
            offset_mod = 6
        else:
            print_name = False
            offset_mod = 0

        x = radar[0] + math.cos(math.radians((360/12)*line_index - 6) + offset_mod + rotation) * length
        y = radar[1] + math.sin(math.radians((360/12)*line_index - 6) + offset_mod + rotation) * length
        small_x = radar[0] + math.cos(math.radians((360/12)*line_index - 6) + offset_mod + rotation) * 40
        small_y = radar[1] + math.sin(math.radians((360/12)*line_index - 6) + offset_mod + rotation) * 40

        pygame.draw.line(SCREEN, color, (x, y), (small_x, small_y), 5)
        if line_index % 2 != 0:

            # calculating the midpoints
            index_sum = 0
            if line_index > 2:
                index_sum = sum([midpoints[-1:][0][0]])

            midpoints.append([(line_index - 1 if line_index < 2 else line_index - index_sum - 2),
                              (x + last_x) / 2, (y + last_y) / 2])

            pygame.draw.line(SCREEN, color, (x, y), (last_x, last_y), 5)
            pygame.draw.line(SCREEN, color, (small_x, small_y), (last_small_x, last_small_y), 5)

        if print_name and color is BLUE:

            text = TextFont.render(name, False, color)

            with Switch(name) as case:
                if case("Main") or case("Database"):
                    text = pygame.transform.rotate(text, 0)
                elif case("AI") or case("Habit"):
                    text = pygame.transform.rotate(text, -30)
                    text_rect = text.get_rect()
                    text_rect.right = 150
                elif case("Display") or case("Email"):
                    text = pygame.transform.rotate(text, 30)
                    text_rect = text.get_rect()
                    text_rect.right = 150

                if case("Display"):
                    SCREEN.blit(text, (text_rect[0] + midpoints[-1][1:][0] - (y_center - midpoints[-1][1:][0]) * 3 - 5, text_rect[1] + midpoints[-1][1:][1]))
                elif case("AI"):
                    SCREEN.blit(text, (text_rect[0] + midpoints[-1][1:][0] - (y_center - midpoints[-1][1:][0]) * 3 - 5, text_rect[1] + midpoints[-1][1:][1] - 20))
                elif case("Email"):
                    SCREEN.blit(text, (midpoints[-1][1:][0] + 5, midpoints[-1][1:][1] - 40))
                elif case("Habit"):
                    SCREEN.blit(text, (midpoints[-1][1:][0] + 5, midpoints[-1][1:][1] + 5))
                elif case("Main"):
                    SCREEN.blit(text, (x_center - 22, y_center - 150))
                elif case("Database"):
                    SCREEN.blit(text, (x_center - 45, y_center + 135))

        last_x = x
        last_y = y
        last_small_x = small_x
        last_small_y = small_y

    if calc_midpoints:
        return midpoints
    return


if __name__ == "__main__":
    Queue = QueueHandler()
    '''# Sample Connections
    Queue.request_connection([1,2])
    Queue.request_connection([4])
    Queue.request_connection([3,5])
    Queue.request_connection([6])
    Queue.request_connection([4])
    Queue.request_connection([2,3])
    '''
    '''# Sample Connections
    Queue.request_connection(["Main"])
    Queue.request_connection(["AI"])
    Queue.request_connection(["Database"])
    Queue.request_connection(["Display"])
    Queue.request_connection(["Habit"])
    Queue.request_connection(["Email"])
    '''
    main(Queue)