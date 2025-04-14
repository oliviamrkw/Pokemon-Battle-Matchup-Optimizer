"""Main file for the Pokémon Battle Matchup Optimizer."""
import io
import random
import math
from typing import Optional, Dict, List, Tuple
import pygame
import requests
import pandas as pd
from pokemon_data_scraper import convert_pokemon_to_id
from pokemon_final_team import get_user_pokemon, get_pokemon
from pokemon_class import Pokemon

pygame.init()

WIDTH, HEIGHT = 800, 600
BLACK, WHITE, RED = (0, 0, 0), (255, 255, 255), (255, 0, 0)
ENEMY_TEAM_OFFSET, USER_TEAM_OFFSET = 250, 440
FONT = pygame.font.SysFont("consolas", 20)
BASE_URL = "https://img.pokemondb.net/sprites/"
ADD_ONS = ("scarlet-violet/normal/1x/", "x-y/normal/", "sun-moon/normal/1x/", "sword-shield/normal/", "home/normal/1x/")

START_SCREEN, INPUT_SCREEN, RESULT_SCREEN = range(3)


class Game:
    """A class to represent the game.

    Instance Attributes:
        - screen: the game screen
        - background: the background image
        - state: the current game state
        - enemy_team: the enemy team of Pokémon
        - user_team: the user team of Pokémon
        - running: whether the game is running
        - input_index: the current index for inputting Pokémon names
        - error_message: an error message to display
        - pokemon_sprites: a dictionary of Pokémon sprites
        - start_button: the start button rectangle
        - enter_button: the enter button rectangle
        - random_button: the random button rectangle
        - back_button: the back button rectangle
    """
    screen: pygame.Surface
    background: pygame.Surface
    state: int
    enemy_team: list[str]
    user_team: list[str]
    running: bool
    input_index: int
    error_message: Optional[str]
    pokemon_sprites: dict[str, pygame.Surface]
    start_button: Optional[pygame.Rect]
    enter_button: Optional[pygame.Rect]
    random_button: Optional[pygame.Rect]
    back_button: Optional[pygame.Rect]

    def __init__(self, screen: Optional[pygame.Surface] = None, background: Optional[pygame.Surface] = None,
                 state: int = START_SCREEN, enemy_team: Optional[List[str]] = None,
                 user_team: Optional[List[str]] = None, running: bool = True, input_index: int = 0,
                 error_message: Optional[str] = None, pokemon_sprites: Optional[Dict[str, pygame.Surface]] = None,
                 start_button: Optional[pygame.Rect] = None, enter_button: Optional[pygame.Rect] = None,
                 random_button: Optional[pygame.Rect] = None, back_button: Optional[pygame.Rect] = None) -> None:
        pygame.display.set_caption("Pokémon Battle Matchup Optimizer")

        self.state = state
        self.screen = screen if screen else pygame.display.set_mode((WIDTH, HEIGHT))
        self.background = background if background else pygame.transform.scale(
            pygame.image.load("images/background2.png"), (WIDTH, HEIGHT)
        )
        # Game state
        self.enemy_team = enemy_team if enemy_team else [""] * 6
        self.user_team = user_team if user_team else [""] * 6
        self.running = running
        self.input_index = input_index
        self.error_message = error_message
        self.pokemon_sprites = pokemon_sprites if pokemon_sprites else {}

        # UI elements
        self.start_button = start_button
        self.enter_button = enter_button
        self.random_button = random_button
        self.back_button = back_button

    def load_sprite(self, pokemon_name: str) -> Optional[pygame.Surface]:
        """Tries to load a Pokémon sprite from the web, handling variations in naming."""
        if pokemon_name in self.pokemon_sprites:
            return self.pokemon_sprites[pokemon_name]

        formatted_name = (
            pokemon_name.lower()
            .replace(" ", "-")
            .replace(".", "")
            .replace("'", "")
            .replace("♀", "-f")
            .replace("♂", "-m")
            .replace(": ", "-")
            .replace("é", "e")
        )

        for url in ADD_ONS:
            sprite = self.fetch_sprite(BASE_URL + url + formatted_name + ".png")
            if sprite:
                self.pokemon_sprites[pokemon_name] = sprite
                return self.adjust_sprite(sprite, url)
        return None

    def fetch_sprite(self, url: str) -> Optional[pygame.Surface]:
        """Helper function to fetch and scale a sprite from a given URL."""
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            sprite = pygame.image.load(io.BytesIO(response.content))
            return pygame.transform.scale(sprite, (80, 80))
        return None

    def adjust_sprite(self, sprite: pygame.Surface, url: str) -> pygame.Surface:
        """Adjusts the sprite if needed based on the source URL."""
        if url == ADD_ONS[0]:
            return sprite

        adjusted_sprite = pygame.Surface((80, 90), pygame.SRCALPHA)
        y_offset = 0
        if url == ADD_ONS[1]:
            y_offset = 20
        adjusted_sprite.blit(sprite, (0, y_offset))
        return adjusted_sprite

    def get_team_positions(self, vertical_offset: float) -> List[Tuple[int, int]]:
        """Returns a list of positions for the Pokémon sprites."""
        return [(WIDTH // 7 + i * 115, vertical_offset) for i in range(6)]

    def display_pokemon(self, pokemon_name: str, position: Tuple[int, int]) -> None:
        """Displays a Pokémon name and sprite at the given position."""
        x, y = position
        sprite = self.pokemon_sprites.get(pokemon_name)
        if sprite:
            self.screen.blit(sprite, (x - 40, y - 40))
        pokemon_name_text = FONT.render(pokemon_name.capitalize(), True, BLACK)
        self.screen.blit(pokemon_name_text, (x - pokemon_name_text.get_width() // 2, y - 40))

    def draw_button(self, text: str, x_pos: int, y_pos: int, width: int, height: int) -> pygame.Rect:
        """Draws a button on the screen."""
        rect = pygame.Rect(x_pos, y_pos, width, height)
        pygame.draw.rect(self.screen, WHITE, rect)
        pygame.draw.rect(self.screen, BLACK, rect, 2)
        text_surface = FONT.render(text, True, BLACK)
        self.screen.blit(text_surface, (x_pos + (width - text_surface.get_width()) // 2,
                                        y_pos + (height - text_surface.get_height()) // 2))
        return rect

    def draw_input_boxes(self) -> None:
        """Draws input boxes for entering the enemy team Pokémon names."""
        for i in range(6):
            x, y = WIDTH // 2 - 100, 250 + i * 30
            box_rect = pygame.Rect(x - 10, y - 5, 200, 25)

            pygame.draw.rect(self.screen, WHITE, box_rect)
            pygame.draw.rect(self.screen, BLACK, box_rect, 2)

            text_surface = FONT.render(f"{i + 1}. {self.enemy_team[i]}", True, BLACK)
            self.screen.blit(text_surface, (x, y))

            if i == self.input_index:
                pygame.draw.polygon(self.screen, BLACK, [
                    (x - 15, y + 5),
                    (x - 20, y),
                    (x - 20, y + 10)
                ])

    def check_game_state(self) -> None:
        """Updates screen based on current game state."""
        if self.state == START_SCREEN:
            self.start_button = self.draw_button("Start", WIDTH // 2 - 50, HEIGHT // 2 + 125, 100, 50)
            title_text = pygame.image.load("images/title_text.png")
            title_text_sized = pygame.transform.scale(title_text,
                                                      (title_text.get_width() // 1.5, title_text.get_height() // 1.5))
            self.screen.blit(title_text_sized, (WIDTH // 7, HEIGHT // 3 + 50))

        elif self.state == INPUT_SCREEN:
            input_text = FONT.render("Enter the Pokémon on the enemy team:", True, BLACK)
            self.screen.blit(input_text, (WIDTH // 2 - input_text.get_width() // 2, 200))
            self.draw_input_boxes()
            self.enter_button = self.draw_button("Enter Team", WIDTH // 2.3, HEIGHT - 100, 120, 50)
            self.draw_error_message()
            self.random_button = self.draw_button("Randomize Team", WIDTH // 10, HEIGHT // 2 + 20, 160, 50)

        elif self.state == RESULT_SCREEN:
            self.display_results()

    def display_results(self) -> None:
        """Displays results on screen."""
        enemy_team_positions = self.get_team_positions(ENEMY_TEAM_OFFSET)
        user_team_positions = self.get_team_positions(USER_TEAM_OFFSET)

        enemy_text = FONT.render("Enemy Team", True, BLACK)
        self.screen.blit(enemy_text, (WIDTH // 2 - enemy_text.get_width() // 2, ENEMY_TEAM_OFFSET - 80))

        for i in range(6):
            start_pos = user_team_positions[i]
            end_pos = enemy_team_positions[i]
            updated_start_pos = (start_pos[0], start_pos[1] - 50)
            updated_end_pos = (end_pos[0], end_pos[1] + 50)

            pygame.draw.line(self.screen, BLACK, updated_start_pos, updated_end_pos, 3)
            self.draw_arrowhead(updated_start_pos, updated_end_pos)
            self.draw_arrowhead(updated_end_pos, updated_start_pos)

        for i, name in enumerate(self.enemy_team):
            self.display_pokemon(name, enemy_team_positions[i])

        for i, name in enumerate(self.user_team):
            self.display_pokemon(name, user_team_positions[i])

        self.back_button = self.draw_button("Back", WIDTH // 2.3, HEIGHT - 100, 120, 50)

    def draw_arrowhead(self, start: Tuple[int, int], end: Tuple[int, int]) -> None:
        """Draws an arrowhead at the end of a line."""
        arrow_size = 10
        angle = math.atan2(end[1] - start[1], end[0] - start[0])

        # calculate arrowhead points
        point1 = (end[0] - arrow_size * math.cos(angle - math.pi / 6),
                  end[1] - arrow_size * math.sin(angle - math.pi / 6))
        point2 = (end[0] - arrow_size * math.cos(angle + math.pi / 6),
                  end[1] - arrow_size * math.sin(angle + math.pi / 6))

        # triangle arrowhead
        pygame.draw.polygon(self.screen, BLACK, [end, point1, point2])

    def handle_event(self, event: pygame.event.Event, mouse_position: Tuple[int, int]) -> None:
        """Handles events."""
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.state == START_SCREEN and self.start_button.collidepoint(mouse_position):
                self.state = INPUT_SCREEN
            elif self.state == INPUT_SCREEN and self.enter_button.collidepoint(mouse_position):
                self.check_team()
            elif self.state == INPUT_SCREEN and self.random_button.collidepoint(mouse_position):
                self.enemy_team = generate_random_team(pd.read_csv("pokemon_data.csv"))
                self.pokemon_sprites = {name: self.load_sprite(name) for name in self.enemy_team}
                self.error_message = None
                self.input_index = 0
                self.draw_input_boxes()
            elif self.state == RESULT_SCREEN and self.back_button.collidepoint(mouse_position):
                self.enemy_team = [""] * 6
                self.user_team = [""] * 6
                self.pokemon_sprites.clear()
                self.state = INPUT_SCREEN
        elif event.type == pygame.KEYDOWN and self.state == INPUT_SCREEN:
            self.enter_enemy_team(event)

    def check_team(self) -> None:
        """Checks if inputted enemy team is valid."""
        self.pokemon_sprites = {name: self.load_sprite(name) for name in set(self.enemy_team)}
        invalid_names = [name for name in self.enemy_team if not self.pokemon_sprites.get(name)]

        if invalid_names:
            self.error_message = "Invalid Pokémon names: " + ", ".join(invalid_names)
        else:
            enemy_team_to_id = [convert_pokemon_to_id(pkmn, "pokemon_data.csv") for pkmn in self.enemy_team]
            self.user_team, _ = get_user_pokemon(get_pokemon(enemy_team_to_id, "pokemon_data.csv"),
                                                 "pokemon_data.csv", "chart.csv")
            self.pokemon_sprites.update({name.lower(): self.load_sprite(name) for name in set(self.user_team)})
            self.state = RESULT_SCREEN
            self.error_message = None

    def draw_error_message(self) -> None:
        """Displays error message on screen."""
        if self.error_message:
            error_surface = FONT.render(self.error_message, True, RED)
            self.screen.blit(error_surface, (WIDTH // 2 - error_surface.get_width() // 2, HEIGHT - 130))

    def enter_enemy_team(self, event: pygame.event.Event) -> None:
        """Handles input for enemy team Pokémon names."""
        if event.key in (pygame.K_RETURN, pygame.K_DOWN):
            self.enemy_team[self.input_index] = self.enemy_team[self.input_index].strip()
            self.input_index = (self.input_index + 1) % 6  # down
        elif event.key == pygame.K_UP:
            self.input_index = (self.input_index - 1) % 6  # up
        elif event.key == pygame.K_BACKSPACE:
            self.enemy_team[self.input_index] = self.enemy_team[self.input_index][:-1]
        else:
            self.enemy_team[self.input_index] += event.unicode.lower()

    def run(self) -> None:
        """Runs the game loop."""
        while self.running:
            self.screen.blit(self.background, (0, 0))
            mouse_pos = pygame.mouse.get_pos()
            self.check_game_state()
            for event in pygame.event.get():
                self.handle_event(event, mouse_pos)
            pygame.display.flip()
        pygame.quit()


def generate_random_team(data: str) -> list[Pokemon]:
    """Generates a random Pokémon team."""
    return random.sample(data["Name"].tolist(), 6)


if __name__ == "__main__":
    # import python_ta

    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['E1136', 'W0221'],
    #     'max-nested-blocks': 4,
    #     'allowed_modules': ['pygame', 'requests', 'pandas',
    #                         'io', 'math', 'random', 'pokemon_data_scraper',
    #                         'graph_algorithm', 'pokemon_final_team']
    # })

    Game().run()
