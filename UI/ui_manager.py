from datetime import datetime
import datetime as dt
import logging
import pygame
import math
import time
import os

from CSUtils import Switch


# The interface for the rest of the program, its where connections are requested, changed, and closed.
class QueueHandler:
    data_fields = []  # modules, nodes, events, wheel_center, midpoints
    connections = []  # list of tuples; ([modules], event, priority, event_data)
    queue = []  # list of tuples; ([modules])

    modules = []
    nodes = []
    events = []

    # The events don't move, they are just changed. This means they are always in the same column
    columns = [1, 2, 3, 1, 2, 3]
    # increasing number, makes sure events requested earlier are connected first
    next_priority = 0

    # setup the data
    def __init__(self):
        self.data_fields = list(setup_display())
        self.modules = self.data_fields[0]
        self.nodes = self.data_fields[1]
        self.events = self.data_fields[2]

    # called by main, checks for connections that can be made and sets to relating attributes.
    def make_connections(self):
        self.__add_connections()
        # for every connection
        for connection in sorted(self.connections, key=lambda l: l[2], reverse=True):
            # for each module in that connection
            for module in connection[0]:
                # give the event index to that module
                setattr(self.nodes[module], "event", connection[1])
                # give the column index to that module, adjusted for 0 based indexing
                setattr(self.nodes[module], "column", self.columns[connection[1] - 1])
                # send the data from the request over to the event for display
                setattr(self.events[connection[1] - 1], "data", connection[3])

    # private function, looks for unconnected requests that can be connected and adds them to connetions[]
    def __add_connections(self):
        # for each request in the connections queue
        for request in self.queue:
            # collect all the connected_events indexes for checking
            try:
                connected_events = [[conn[1] - 1 for conn in self.connections]][0]
            # catches if there are no connected events
            except IndexError:
                connected_events = []
            # for each possible event
            for event_index in range(6):
                # if that event does not already have a connected module
                if event_index not in connected_events:
                    # add that event to the connections
                    self.connections.append((request[0], event_index + 1, self.next_priority, request[1]))
                    # remove the connection from the queue
                    self.queue.remove(request)
                    # iterate the priority
                    self.next_priority += 1
                    return

    # adds a possible connection to the requests queue
    def request_connection(self, modules, data):
        # for each module
        for index, module in enumerate(modules):
            # change module names to the corresponding index
            with Switch(module) as case:
                if case("Display"):
                    modules[index] = 3
                elif case("AI"):
                    modules[index] = 4
                elif case("Email"):
                    modules[index] = 6
                elif case("Schedule"):
                    modules[index] = 1
                elif case("Main"):
                    modules[index] = 2
                elif case("Database"):
                    modules[index] = 5
        # add the module index and its data to the connections queue
        self.queue.append(([module - 1 for module in modules], data))

    # close a connection given the event name
    def close_connection(self, event_name, unique_id=""):
        # check over existing connection
        for connection in self.connections:
            # if connection event title matches given name
            if connection[3]["title"] == event_name:
                if unique_id != "":
                    try:
                        if connection[3]["unique_id"] != unique_id:
                            return
                    except KeyError:
                        pass
                # reset the nodes so the connection is not displayed
                for module in connection[0]:
                    setattr(self.nodes[module], "event", 0)
                    setattr(self.nodes[module], "column", 0)
                # remove the connection from the existing connections list (this also deletes all tracked event data)
                self.connections.remove(connection)

    # update the data of an event given the event name and any new or changed data
    def update_data(self, event_name, new_dict, unique_id=""):
        # for every existing connection
        for connection in self.connections:
            # if connection event title matches given name
            if connection[3]["title"] == event_name:
                if unique_id != "":
                    try:
                        if connection[3]["unique_id"] != unique_id:
                            return
                    except KeyError:
                        pass
                try:
                    # for each item in the new/updated data
                    for key in new_dict:
                        # changed that data
                        connection[3][key] = new_dict[key]
                    # reset the connection time, will only change how long the event is displayed if lifespan is edited.
                    connection[3]["connection_time"] = datetime.now()
                # only catches if bad dictionary data is given.
                except KeyError:
                    return 1


# One of 6 modules (Main, Email, AI, Database, Habit, Display)
class Module:
    # the name of the module
    name = ""
    # the public key - is also the index of the module in almost every list
    public_key = 0
    # only shared with an event that is being connected to this module
    event_private_key = 0

    def __init__(self, name, public_key):
        self.name = name
        self.public_key = public_key

    # used for debugging, prints out the module name and index.
    def __str__(self):
        return str(self.public_key) + ": " + str(self.name)


# One of 6 customizable events
class Event:
    # the public key - is also the index of the event in almost every list
    public_key = 0
    # the location of the final node that connects the event
    node_loc = (0, 0)
    # the width of the event, height is set every time the event is draw.
    width = 0
    # the data the event needs to display
    data = {}

    # required attributes collected from the data dictionary
    color = ()
    title = ""
    unique_id = ""

    def __init__(self, public_key, node_loc, width):
        self.public_key = public_key
        self.node_loc = node_loc
        self.width = width
        self.referenced = False

    # called as part of the main loop - displays the event
    def draw(self):

        # 1 = up, -1 = down (from the connecting node)
        direction = 1
        if self.node_loc[1] > Y_CENTER:
            direction = -1

        # try to build the required attributes into the attributes from the dictionary
        try:
            if isinstance(self.data["color"], tuple) and len(self.data["color"]) == 3:
                self.color = self.data["color"]
            else:
                return 1
            if isinstance(self.data["title"], str):
                self.title = self.data["title"]
            else:
                return 1
        except (BaseException, Exception):
            return 1

        # check if there is a notset attached to this event
        for node_set in DisplayQueueManager.nodes:
            # if there is...
            if getattr(node_set, "event") == self.public_key:
                # test to see if there is a connection_time data index
                try:
                    self.data["connection_time"]
                # if there is not, set the connection_time to now
                except KeyError:
                    self.data["connection_time"] = datetime.now()

        # try to see if the lifespan of the event has completed
        try:
            if self.data["connection_time"] + dt.timedelta(seconds=self.data["lifespan"]) < datetime.now():
                # if it has, raise a TypeError so the event is closed
                raise TypeError
        except KeyError:
            pass

        # try to get a unique_id, this is only used for events that may need duplicate titles
        try:
            self.unique_id = self.data["unique_id"]
        except KeyError:
            pass

        # if this event is in the QueueHandler's connections list, draw it
        if self.public_key in [conn[1] for conn in getattr(QueueHandler, "connections")]:
            ''' body '''
            body = pygame.Rect((self.node_loc[0] - self.width / 4) + self.width / 16,
                               (Y_CENTER - (Y_CENTER * direction) + (15 * direction)) if direction > 0 else
                               self.node_loc[1],
                               ((self.node_loc[0] + self.width / 4) - self.width / 16) - (
                                           (self.node_loc[0] - self.width / 4) + self.width / 16),
                               (Y_CENTER - (Y_CENTER - self.node_loc[1]) - 15) if direction > 0 else
                               SIZE[1] - self.node_loc[1] - 15)
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
            ''' title '''
            text = TextFont.render(self.title, False, self.color)
            SCREEN.blit(text, (((self.node_loc[0] - self.width / 4) + self.width / 16 + 15,
                        Y_CENTER - (Y_CENTER * direction) + (15 * direction) + 15) if direction > 0 else
                        ((self.node_loc[0] - self.width / 4) + self.width / 16 + 15, self.node_loc[1] + 15)))

            ''' Text Box '''
            try:
                for row, line_text in enumerate(self.data["TextBox"]):
                    text = TextFont.render(line_text, False, self.color)
                    SCREEN.blit(text, (((self.node_loc[0] - self.width / 4) + self.width / 16 + 15,
                                        Y_CENTER - (Y_CENTER * direction) + (15 * direction) + 45 + (row * 20))
                                       if direction > 0 else
                                       ((self.node_loc[0] - self.width / 4) + self.width / 16 + 15,
                                        self.node_loc[1] + 45 + (row * 20))))
            except KeyError:
                pass
        return 0


# Individual nodes used for connecting modules to events
class Node:
    # private key, only used for placement
    private_key = 0
    # its place in its nodeset path
    path_index = 0
    # its (x,y) location
    location = (0, 0)

    def __init__(self, private_key, path_index):
        self.private_key = private_key
        self.path_index = path_index

    # prints the node for debugging
    def __str__(self):
        return str(self.private_key) + ": " + str(self.path_index) + ". " + str(self.location)


# A set of Nodes for easy interfacing.
class NodeSet:
    # list of node objects in this set
    nodes = []
    column = 0  # 1 - 3
    event = 0  # 1 - 6

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


# All of the color constants used by the display.
BACKGROUND = (9, 17, 27)
LIGHT_BACK = (16, 28, 43)
GREEN = (17, 180, 147)
RED = (194, 68, 78)
BLUE = (56, 165, 205)
DARK_BLUE = (33, 102, 127)
YELLOW = (232, 229, 48)

# set the starting position of the window.
# Thank you to https://stackoverflow.com/users/142637/sloth for the borderless window code
os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
pygame.init()
pygame.font.init()

# Window size variables
infoObject = pygame.display.Info()
SIZE = (infoObject.current_w, infoObject.current_h)
X_CENTER = SIZE[0]/2
Y_CENTER = SIZE[1]/2

# create a borderless window that's as big as the entire screen
SCREEN = pygame.display.set_mode((SIZE[0], SIZE[1]), pygame.NOFRAME)
clock = pygame.time.Clock()

# The font for the display
TextFont = pygame.font.SysFont('Courant', 30)


# Run once, sets the location for a the modules, nodes, and events
def setup_display():
    modules = []
    nodes = []
    events = []

    wheel_center = (SIZE[0] / 7, Y_CENTER)

    for index, module_name in enumerate(["Global Manager", "Email Connection", "Database Management",
                                         "Schedule Management", "Schedule Management", "AI Elements"]):
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


# The main loop, keeps the display running
def main(display_state_object):

    modules, nodes, events, wheel_center, midpoints = getattr(DisplayQueueManager, "data_fields")
    errors = 0
    loop_count = 0

    running = True

    while running:

        pygame.event.pump()

        if display_state_object.get_state():

            loop_count += 1
            if loop_count == 1:
                DisplayQueueManager.make_connections()
            elif loop_count == 100:
                loop_count = 0

            SCREEN.fill(BACKGROUND)

            # draw_guidelines()

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
                if getattr(event, "data"):
                    try:
                        errors += event.draw()
                    except TypeError:
                        try:
                            DisplayQueueManager.close_connection(getattr(event, "data")["title"],
                                                                 unique_id=getattr(event, "data")["unique_id"])
                        except KeyError:
                            DisplayQueueManager.close_connection(getattr(event, "data")["title"])

            pygame.display.flip()

            if errors != 0:
                logging.exception("A display error has occurred, the display has been closed to prevent program exit.")
                time.sleep(0.1)
                return "DisplayError"
        else:
            return 1


# Closing the display, in its own function so that manager.py can call it
def close_display():
    pygame.quit()


# A function for drawing sections on the screen, only used for debugging
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


# given a nodeset and a color, connection modules to the corresponding event
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
        # if the event the module is linked to has data. If it does not do not draw the event.
        if getattr(connection_event, "data"):
            for index in range(len(node_set)):
                try:
                    pygame.draw.line(SCREEN, color,
                                     getattr(node_set[index], "location"), getattr(node_set[index + 1], "location"), 4)
                except AttributeError:
                    try:
                        if getattr(node_set[index], "location")[1] < Y_CENTER < node_set[index + 1][1]:  # going down
                            node_set.insert(-1, (getattr(node_set[-2], "location")[0] + 15,
                                                 Y_CENTER + (Y_CENTER - getattr(node_set[4], "location")[1]) -
                                                 vertical_offset_dist))

                            pygame.draw.line(SCREEN, color, node_set[-2], node_set[-1], 4)
                        elif getattr(node_set[index], "location")[1] > Y_CENTER > node_set[index + 1][1]:  # going up
                            node_set.insert(-1, (getattr(node_set[-2], "location")[0] + 15,
                                                 Y_CENTER - (getattr(node_set[4], "location")[1] - Y_CENTER) +
                                                 vertical_offset_dist))

                            pygame.draw.line(SCREEN, color, node_set[-2], node_set[-1], 4)

                        pygame.draw.line(SCREEN, color,
                                         getattr(node_set[index], "location"), node_set[index + 1], 4)

                    except (IndexError, AttributeError):
                        return node_set
                except IndexError:
                    return node_set
            return node_set


# Places down all of the nodes based on the window size
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


# draw the modules, calc_midpoints is only ever set to True in one call
def display_modules(center, rotation, color, calc_midpoints=False):
    x_center = center[0]
    y_center = center[1]

    module_names = ["Main", "Display", "AI", "Database", "Email", "Schedule"]

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
                elif case("AI") or case("Schedule"):
                    text = pygame.transform.rotate(text, -30)
                    text_rect = text.get_rect()
                    text_rect.right = 150
                elif case("Display") or case("Email"):
                    text = pygame.transform.rotate(text, 30)
                    text_rect = text.get_rect()
                    text_rect.right = 150

                if case("Display"):
                    SCREEN.blit(text, (text_rect[0] + midpoints[-1][1:][0] - (midpoints[-1][1:][0] - x_center) - 10,
                                       text_rect[1] + midpoints[-1][1:][1]))
                elif case("AI"):
                    SCREEN.blit(text, (text_rect[0] + midpoints[-1][1:][0] - (midpoints[-1][1:][0] - x_center) - 15,
                                       text_rect[1] + midpoints[-1][1:][1] - 20))
                elif case("Email"):
                    SCREEN.blit(text, (midpoints[-1][1:][0] + 5, midpoints[-1][1:][1] - 40))
                elif case("Schedule"):
                    SCREEN.blit(text, (midpoints[-1][1:][0] + 5, midpoints[-1][1:][1]))
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


# This global is at the bottom so that it is the last thing compiled by the initial import statement.
DisplayQueueManager = QueueHandler()
