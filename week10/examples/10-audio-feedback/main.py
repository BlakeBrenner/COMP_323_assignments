import pygame

from audio_feedback.game import Game


def main() -> None:
    pygame.mixer.pre_init(44100, -16, 2, 256)
    pygame.init()
    pygame.display.set_caption("Week 10 Audio + Feedback (Pygame)")

    game = Game()
    clock = pygame.time.Clock()

    running = True
    while running:
        dt = clock.tick(game.fps) / 1000.0
        dt = min(dt, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game.handle_event(event)

        game.update(dt)
        game.draw()
        pygame.display.flip()

    game.shutdown()
    pygame.quit()


if __name__ == "__main__":
    main()