import pygame
from ants.pygame_adapter import FieldHandler


FPS = 100

LEFT = 1  # left mouse button
MIDDLE = 2
RIGHT = 3  # ...
WHEELUP = 4
WHEELDOWN = 5

RESOLUTION = (1000, 1000)


def main(args):

    fieldhandler_args = {
        'grid_size': args.gridsize,
        'food_quant': args.food,
        'spawn_ants': not args.nospawn,
        'startants': args.startants,
        'resolution': RESOLUTION,
        'colony_count': args.colonys,
    }

    pygame.init()

    screen = pygame.display.set_mode(RESOLUTION)

    pygame.display.set_caption("Ants")
    pygame.mouse.set_visible(1)

    # frame limiter
    clock = pygame.time.Clock()

    fieldhandler = FieldHandler(**fieldhandler_args)

    running = True
    while running:

        clock.tick(FPS)
        background = pygame.Surface(RESOLUTION)
        background.fill((0, 0, 0))
        background = background.convert()

        # temporary surface to draw things to
        display = pygame.Surface(RESOLUTION)
        display.fill((0, 0, 0))
        display = display.convert()

        display.blit(background, (0, 0))

        # put display to draw method
        display = fieldhandler.draw_fields(display)

        screen.blit(display, (0, 0))

        # look for events
        for event in pygame.event.get():

            # quit game
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
                fieldhandler.click(event.pos)
                print('left mouse button')

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == RIGHT:
                fieldhandler.right_click(event.pos)
                print('right mouse button')

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    fieldhandler.run_engine = True

                if event.key == pygame.K_DOWN:
                    fieldhandler.run_engine = False

        pygame.display.flip()


if __name__ == '__main__':
    # run main programm
    main()
