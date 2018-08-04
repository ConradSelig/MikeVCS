import pygame
import math

BACKGROUND = (9, 17, 27)
GREEN = (17, 180, 147)
RED = (194, 68, 78)
BLUE = (56, 165, 205)


def main():

    pygame.init()

    infoObject = pygame.display.Info()
    size = (infoObject.current_w, infoObject.current_h)

    x_center = size[0] / 2
    y_center = size[1] / 2

    box_connections = [[0, (100, 250), False], [1, (300, 250), False], [2, (500, 250), False]]
    module_connections = [[index, "midpoint", name, "no_connection"] for index, name in enumerate(
        ["tester1", "tester2", "tester3", "tester4", "tester5", "tester6"])]

    screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
    pygame.display.set_caption("Mike Diagnostics")
    pygame.display.set_icon(pygame.image.load("tray_icon.jpg"))
    clock = pygame.time.Clock()

    running = True

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        screen.fill(BACKGROUND)

        midpoints = background_display(screen, (500, size[1] * 2 - 450), 12.03)

        for index, module_connection in enumerate(module_connections):
            for midpoint in midpoints:
                if midpoint[0] == module_connection[0]:
                    module_connections[index][1] = midpoint[1:]

        for module_connection in module_connections:
            pygame.draw.ellipse(screen, BLUE, (module_connection[1][0] - 8, module_connection[1][1] - 8, 16, 16), 4)

        for index, module_connection in enumerate(module_connections):
            if module_connection[1][-1] == "TOP-LEFT" or module_connection[1][-1] == "TOP-RIGHT":
                print(module_connection)
                for box_index, box_connection in enumerate(box_connections):
                    if box_connection[2] is False and module_connection[3] == "no_connection":
                        module_connections[index][3] = box_connection[0]
                        box_connections[box_index][2] = True
                        print("adding connection:", module_connections[index])
                        break
            else:
                if module_connection[3] != "no_connection":
                    box_connections[module_connection[3]][2] = False
                    module_connections[index][3] = "no_connection"

            print(box_connections)

            if module_connection[3] != "no_connection":
                print("connecting:", index, "to", box_connections[module_connection[3]][0])
                pygame.draw.line(screen, RED, (module_connection[1][0], module_connection[1][1]), (box_connections[module_connection[3]][1][0], box_connections[module_connection[3]][1][1]), 5)

        for module_connection in box_connections:
            pygame.draw.ellipse(screen, RED, (module_connection[1][0] - 8, module_connection[1][1] - 8, 16, 16), 4)

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()

    return 0


def background_display(screen, size, rotation):
    x_center = size[0]/2
    y_center = size[1]/2

    midpoints = []

    last_x = 0
    last_y = 0
    last_small_x = 0
    last_small_y = 0

    for line_index in range(12):
        radar = (x_center, y_center)
        length = 175
        if line_index % 2 == 0:
            offset_mod = 6
        else:
            offset_mod = 0

        x = radar[0] + math.cos(math.radians((360/12)*line_index - 6) + offset_mod + rotation) * length
        y = radar[1] + math.sin(math.radians((360/12)*line_index - 6) + offset_mod + rotation) * length
        small_x = radar[0] + math.cos(math.radians((360/12)*line_index - 6) + offset_mod + rotation) * 40
        small_y = radar[1] + math.sin(math.radians((360/12)*line_index - 6) + offset_mod + rotation) * 40

        pygame.draw.line(screen, BLUE, (x, y), (small_x, small_y), 5)
        #pygame.draw.line(screen, BACKGROUND, (small_x, small_y), (x_center, y_center), 8)
        if line_index % 2 != 0:

            index_sum = 0
            if line_index > 2:
                index_sum = sum([midpoints[-1:][0][0]])

            midpoints.append([(line_index - 1 if line_index < 2 else line_index - index_sum - 2), (x + last_x) / 2, (y + last_y) / 2, ""])
            pygame.draw.line(screen, BLUE, (x, y), (last_x, last_y), 5)
            pygame.draw.line(screen, BLUE, (small_x, small_y), (last_small_x, last_small_y), 5)

        last_x = x
        last_y = y
        last_small_x = small_x
        last_small_y = small_y

    for index, midpoint in enumerate(midpoints):
        if midpoint[1] >= x_center:
            if midpoint[2] >= y_center:
                midpoints[index][3] = "BOTTOM-RIGHT"
            else:
                midpoints[index][3] = "TOP-RIGHT"
        else:
            if midpoint[2] >= y_center:
                midpoints[index][3] = "BOTTOM-LEFT"
            else:
                midpoints[index][3] = "TOP-LEFT"

    return midpoints


if __name__ == "__main__":
    main = main()
    if main == 0:
        print("\n\nProgram Complete")
    else:
        print("\n\n", str(main))
