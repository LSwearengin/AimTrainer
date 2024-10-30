import pygame
import sys
import gameloop
import tasks

pygame.init()
pygame.font.init()

# Screen information
WIDTH = 1920
HEIGHT = 1080
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2.5D Aim Trainer")

class Game:
    def __init__(self):
        self.window = window
        self.font = pygame.font.Font(None, 74)
        self.state = "main_menu"
        self.selected_item = 0
        self.menu_items = ["Tasks", "Leaderboard", "Settings"]
        self.tasks = tasks.tasks
        self.selected_task_index = 0

    def draw_menu(self):
        self.window.fill((255, 255, 255))
        title_text = self.font.render("Main Menu", True, (128, 0, 128))
        self.window.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))
        for i, item in enumerate(self.menu_items):
            color = (128, 0, 128) if i == self.selected_item else (0, 0, 0)
            menu_text = self.font.render(item, True, color)
            self.window.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, HEIGHT // 2 + i * 100))
        pygame.display.update()

    def draw_tasks_menu(self):
        self.window.fill((255, 255, 255))
        title_text = self.font.render("Select Task", True, (128, 0, 128))
        self.window.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))
        for i, task in enumerate(self.tasks):
            color = (128, 0, 128) if i == self.selected_task_index else (0, 0, 0)
            task_text = self.font.render(task['name'], True, color)
            self.window.blit(task_text, (WIDTH // 2 - task_text.get_width() // 2, HEIGHT // 2 + i * 100))
        pygame.display.update()

    def main_menu(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.selected_item = (self.selected_item + 1) % len(self.menu_items)
                    elif event.key == pygame.K_UP:
                        self.selected_item = (self.selected_item - 1) % len(self.menu_items)
                    elif event.key == pygame.K_RETURN:
                        if self.menu_items[self.selected_item] == "Tasks":
                            self.state = "tasks_menu"
                            running = False
                        elif self.menu_items[self.selected_item] == "Leaderboard":
                            self.state = "leaderboard"
                        elif self.menu_items[self.selected_item] == "Settings":
                            self.state = "settings"
            self.draw_menu()

    def tasks_menu(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.selected_task_index = (self.selected_task_index + 1) % len(self.tasks)
                    elif event.key == pygame.K_UP:
                        self.selected_task_index = (self.selected_task_index - 1) % len(self.tasks)
                    elif event.key == pygame.K_RETURN:
                        #start game with specific task
                        selected_task = self.tasks[self.selected_task_index]
                        gameloop.gameLoop(selected_task)
            self.draw_tasks_menu()

    def run(self):
        while True:
            if self.state == "main_menu":
                self.main_menu()
            elif self.state == "tasks_menu":
                self.tasks_menu()

if __name__ == "__main__":
    game = Game()
    game.run()
