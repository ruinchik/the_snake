"""
Классическая игра "Змейка"
Управление: стрелки ← ↑ → ↓
Перезапуск игры: клавиша R
Выход: ESC или закрытие окна
"""

import pygame
import sys
from random import randint


# Константы для размеров поля и сетки
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета
BOARD_BACKGROUND_COLOR = (0, 0, 0)      # Черный фон
BORDER_COLOR = (93, 216, 228)           # Голубая граница
APPLE_COLOR = (255, 0, 0)               # Красное яблоко
SNAKE_COLOR = (0, 255, 0)               # Зеленая змейка
SNAKE_HEAD_COLOR = (0, 200, 0)          # Более темная голова

# Скорость движения (кадров в секунду)
SPEED = 10


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, position=None, body_color=None):
        """
        Инициализирует игровой объект.
        
        Args:
            position (tuple): Координаты объекта (x, y)
            body_color (tuple): Цвет объекта в формате RGB
        """
        self.position = position if position else (
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        )
        self.body_color = body_color

    def draw(self):
        """Абстрактный метод для отрисовки объекта."""
        pass


class Apple(GameObject):
    """Класс для яблока."""

    def __init__(self, snake_positions=None):
        """
        Инициализирует яблоко.
        
        Args:
            snake_positions (list): Позиции змейки, чтобы яблоко не появилось на ней
        """
        super().__init__(body_color=APPLE_COLOR)
        self.snake_positions = snake_positions or []
        self.randomize_position()

    def randomize_position(self):
        """Устанавливает случайные координаты для яблока."""
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            # Проверяем, чтобы яблоко не появилось на змейке
            if self.position not in self.snake_positions:
                break

    def draw(self, surface):
        """
        Отрисовывает яблоко на экране.
        
        Args:
            surface: Поверхность для отрисовки
        """
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс для змейки."""

    def __init__(self):
        """Инициализирует змейку."""
        super().__init__(body_color=SNAKE_COLOR)
        self.reset()

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.last = None
        self.score = 0
        print("Змейка сброшена. Начинаем новую игру!")

    def update_direction(self):
        """Обновляет направление движения змейки."""
        if self.next_direction:
            # Запрещаем движение в противоположном направлении
            if (self.next_direction[0] * -1, self.next_direction[1] * -1) != self.direction:
                self.direction = self.next_direction

    def get_head_position(self):
        """
        Возвращает позицию головы змейки.
        
        Returns:
            tuple: Координаты головы (x, y)
        """
        return self.positions[0]

    def move(self):
        """Перемещает змейку на одну клетку в текущем направлении."""
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction
        
        # Движение с переходом через границы
        new_x = (head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT
        new_position = (new_x, new_y)

        # Добавляем новую голову
        self.positions.insert(0, new_position)
        
        # Удаляем хвост, если не выросли
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self, surface):
        """
        Отрисовывает змейку на экране.
        
        Args:
            surface: Поверхность для отрисовки
        """
        # Рисуем тело змейки
        for i, position in enumerate(self.positions):
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            
            # Голова другого цвета
            if i == 0:
                pygame.draw.rect(surface, SNAKE_HEAD_COLOR, rect)
            else:
                pygame.draw.rect(surface, self.body_color, rect)
            
            pygame.draw.rect(surface, BORDER_COLOR, rect, 1)

        # Затираем последний сегмент
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)


def handle_keys(snake):
    """
    Обрабатывает нажатия клавиш для управления змейкой.
    
    Args:
        snake (Snake): Объект змейки для управления
    
    Returns:
        bool: False если нужно выйти из игры, True если продолжать
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            elif event.key == pygame.K_UP and snake.direction != DOWN:
                snake.next_direction = UP
            elif event.key == pygame.K_DOWN and snake.direction != UP:
                snake.next_direction = DOWN
            elif event.key == pygame.K_LEFT and snake.direction != RIGHT:
                snake.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                snake.next_direction = RIGHT
    
    # Также обрабатываем зажатые клавиши для более отзывчивого управления
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and snake.direction != DOWN:
        snake.next_direction = UP
    elif keys[pygame.K_DOWN] and snake.direction != UP:
        snake.next_direction = DOWN
    elif keys[pygame.K_LEFT] and snake.direction != RIGHT:
        snake.next_direction = LEFT
    elif keys[pygame.K_RIGHT] and snake.direction != LEFT:
        snake.next_direction = RIGHT
    
    return True


def draw_score(surface, score, font):
    """
    Отрисовывает счет на экране.
    
    Args:
        surface: Поверхность для отрисовки
        score (int): Текущий счет
        font: Шрифт для отображения текста
    """
    score_text = font.render(f"Счет: {score}", True, (255, 255, 255))
    surface.blit(score_text, (10, 10))


def draw_game_over(surface, font):
    """
    Отрисовывает сообщение о завершении игры.
    
    Args:
        surface: Поверхность для отрисовки
        font: Шрифт для отображения текста
    """
    game_over_text = font.render("ИГРА ОКОНЧЕНА!", True, (255, 50, 50))
    restart_text = font.render("Нажмите R для перезапуска", True, (255, 255, 255))
    exit_text = font.render("Нажмите ESC для выхода", True, (255, 255, 255))
    
    surface.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 
                                  SCREEN_HEIGHT // 2 - 50))
    surface.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 
                                SCREEN_HEIGHT // 2))
    surface.blit(exit_text, (SCREEN_WIDTH // 2 - exit_text.get_width() // 2, 
                             SCREEN_HEIGHT // 2 + 40))


def main():
    """Основная функция игры."""
    # Инициализация Pygame
    pygame.init()
    
    # Создание игрового окна
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Змейка | Управление: стрелки, R - рестарт, ESC - выход')
    
    # Настройка шрифта для текста
    font = pygame.font.SysFont('Arial', 24)
    
    # Создание объектов игры
    snake = Snake()
    apple = Apple(snake.positions)
    
    # Настройка времени
    clock = pygame.time.Clock()
    
    # Флаг работы игры
    running = True
    game_over = False
    
    print("=" * 50)
    print("Игра 'Змейка' запущена!")
    print("Управление: стрелки ← ↑ → ↓")
    print("Перезапуск: R")
    print("Выход: ESC или закрытие окна")
    print("=" * 50)
    
    # Основной игровой цикл
    while running:
        # Обработка событий
        running = handle_keys(snake)
        
        # Проверка на перезапуск игры
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            print("\n" + "=" * 30)
            print("Перезапуск игры по нажатию R...")
            print("=" * 30 + "\n")
            snake.reset()
            apple = Apple(snake.positions)
            game_over = False
        
        # Если игра не окончена, обновляем состояние
        if not game_over and running:
            # Обновление направления движения
            snake.update_direction()
            
            # Движение змейки
            snake.move()
            
            # Проверка на съедание яблока
            if snake.get_head_position() == apple.position:
                snake.length += 1
                snake.score += 10
                apple = Apple(snake.positions)
                print(f"Яблоко съедено! Длина: {snake.length}, Счет: {snake.score}")
            
            # Проверка на столкновение с собой
            if snake.get_head_position() in snake.positions[1:]:
                print(f"Столкновение с собой! Игра окончена. Финальный счет: {snake.score}")
                game_over = True
        
        # Отрисовка
        screen.fill(BOARD_BACKGROUND_COLOR)
        
        if not game_over:
            # Отрисовка игровых объектов
            snake.draw(screen)
            apple.draw(screen)
            draw_score(screen, snake.score, font)
        else:
            # Отрисовка экрана завершения игры
            draw_game_over(screen, font)
            draw_score(screen, snake.score, font)
        
        # Обновление экрана
        pygame.display.flip()
        
        # Ограничение FPS
        clock.tick(SPEED)
    
    # Завершение Pygame
    pygame.quit()
    print("\nСпасибо за игру!")
    sys.exit()


if __name__ == '__main__':
    main()