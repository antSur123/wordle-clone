import pygame
import pygame.gfxdraw
import random

pygame.init()

# Colors
BACKGROUND_COLOR = 250, 250, 250
BLACK = 0, 0, 0
BUTTON_BORDER_COLOR = 224, 224, 224
BUTTON_DEFAULT_COLOR = 228, 240, 254
BUTTON_SELECTED_COLOR = 49, 125, 238
BUTTON_TEXT_DEFAULT_COLOR = 53, 123, 247
BUTTON_TEXT_SELECTED_COLOR = 255, 255, 255
MENU_TEXT_COLOR = 112, 112, 112
MENU_TITLE_COLOR = 49, 125, 238
TILE_GRAY = 127, 127, 127
TILE_GREEN = 132, 169, 18
TILE_YELLOW = 255, 127, 39
WHITE = 255, 255, 255

# Title and icon
pygame.display.set_caption("Wordle clone")
icon = pygame.image.load("sprites/icon.png")
pygame.display.set_icon(icon)

# Create screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Create tiles and their text
default_tile_img = pygame.image.load("sprites/default_tile.png")
green_tile_img = pygame.image.load("sprites/green_tile.png")
yellow_tile_img = pygame.image.load("sprites/yellow_tile.png")
gray_tile_img = pygame.image.load("sprites/gray_tile.png")
tile_font = pygame.font.SysFont('Consolas', 64)

tile_color_index = []
submitted_word_list = [""]
written_word = ""

# Game init
guesses = num_of_rows = 7
num_of_letters = num_of_tiles_in_row = 5
chosen_word = ""
all_word_list = []

# Error message
error_font = pygame.font.SysFont('Arial', 24)
error_message = None
error_msg_too_short = "The word is too short!"
error_msg_max_length = "Max word length reached!"
error_msg_not_a_word = "The word wasn't recognized!"
error_msg_same_word = "The word has already been guessed on!"

MESSAGE_TIME_LIMIT = 2000
timestamp = 0
alpha = 255

# Menu's
menu_background = pygame.image.load("sprites/menu.png")
menu_title_font = pygame.font.SysFont('dejavusans', 42, True)
menu_text_font = pygame.font.SysFont('dejavusans', 20)
button_font = pygame.font.SysFont('Consolas', 42)
menu_title = menu_title_font.render("Wordle Clone", True, MENU_TITLE_COLOR)
length_text = menu_text_font.render("Letters in word:", True, MENU_TEXT_COLOR)
guesses_text = menu_text_font.render("Amount of guesses:", True, MENU_TEXT_COLOR)
game_over_text = menu_text_font.render("Game over", True, MENU_TEXT_COLOR)
score_text = menu_text_font.render("Score:", True, MENU_TEXT_COLOR)
is_application_running = False
menu_screen = None
word_length_buttons = []
amt_of_guesses_buttons = []
start_button = ""
main_menu_button = ""
end_score = 0

# Keyboard
keyboard_font = pygame.font.SysFont('Consolas Bold', 64)
keyboard_list = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"], ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
                 ["Z", "X", "C", "V", "B", "N", "M"]]
alphabet_row_lengths = [0, 0, 0, 0]  # There's 1 extra zero to compensate for the next row start.
keyboard_letter_color_list = [[], [], []]  # [[green letters], [yellow letters], [gray letters]]
has_rendered_all_rows_once = False


class MenuButton:
    # Creates a button which can draw itself at its coordinates.
    def __init__(self, text, x, y):
        self.x = x
        self.y = y
        self.text = text
        self.rendered_text = button_font.render(self.text, True, BUTTON_TEXT_DEFAULT_COLOR)
        self.width = self.rendered_text.get_width()
        self.height = self.rendered_text.get_height()
        self.background = None
        self.border = None
        self.is_selected = False

    def blit_self(self):
        padding_x = 14
        padding_y = 7

        if self.is_selected:
            button_color = BUTTON_SELECTED_COLOR
            text_color = BUTTON_TEXT_SELECTED_COLOR
        else:
            button_color = BUTTON_DEFAULT_COLOR
            text_color = BUTTON_TEXT_DEFAULT_COLOR

        self.border = pygame.draw.rect(screen, BUTTON_BORDER_COLOR, (self.x - padding_x - 1,
                                                                     self.y - padding_y - 1,
                                                                     self.width + 2 * padding_x + 2,
                                                                     self.height + 1.5 * padding_y + 2), 0, 2)
        self.background = pygame.draw.rect(screen, button_color, (self.x - padding_x,
                                                                  self.y - padding_y,
                                                                  self.width + 2 * padding_x,
                                                                  self.height + 1.5 * padding_y), 0, 2)

        self.rendered_text = button_font.render(self.text, True, text_color)
        screen.blit(self.rendered_text, (self.x, self.y))


def center(axis, item):
    '''
    Takes in an item and an axis, and aligns the item to the center of the screen in the axis.

    Should only be used with rendered text and images
    '''
    if axis == "x":
        return SCREEN_WIDTH / 2 - item.get_width() / 2
    if axis == "y":
        return SCREEN_HEIGHT / 2 - item.get_height() / 2


def draw_menu_screen(type_of_menu):
    '''Draws different menus depending on the current menu screen is.'''
    global end_score
    # Draws the default menu background and title.
    to_side_of_menu = center("x", menu_background) + 25
    title_text_coords = center("x", menu_title), 240

    menu_background_coords = center("x", menu_background), center("y", menu_background) + 15
    screen.blit(menu_background, menu_background_coords)

    screen.blit(menu_title, title_text_coords)

    # Draws all main menu buttons and texts.
    if type_of_menu == "main":
        for button in word_length_buttons:
            button.blit_self()
        length_text_coords = to_side_of_menu, word_length_buttons[0].y - 40
        screen.blit(length_text, length_text_coords)

        for button in amt_of_guesses_buttons:
            button.blit_self()

        guesses_text_coords = to_side_of_menu, amt_of_guesses_buttons[0].y - 40
        screen.blit(guesses_text, guesses_text_coords)
        start_button.blit_self()

    # Draws all won or lost buttons and relevant text.
    elif type_of_menu in ["won", "lost"]:
        game_over_text_coords = center("x", game_over_text), 300
        screen.blit(game_over_text, game_over_text_coords)

        if type_of_menu == "lost":
            result_text = menu_text_font.render("You failed to guess the right word!", True, MENU_TEXT_COLOR)
            right_word_text = menu_text_font.render(f"The right word was: {chosen_word}", True, MENU_TEXT_COLOR)

            right_word_text_coords = center("x", right_word_text), 380
            screen.blit(right_word_text, right_word_text_coords)
            score_text_y = 440

        else:
            result_text = menu_text_font.render("You've guessed the right word!", True, MENU_TEXT_COLOR)
            score_text_y = 400

        result_text_coords = center("x", result_text), 340
        screen.blit(result_text, result_text_coords)

        # The y value will be different depending on what menu screen is drawn due to different amount of text.
        score_text_coords = center("x", score_text) - 100, score_text_y
        screen.blit(score_text, score_text_coords)

        # Calculates the current game score.
        if end_score == 0:
            green_letters = 0
            yellow_letters = 0

            for row in tile_color_index:
                row.count("green")
                row.count("yellow")
                green_letters += row.count("green")
                yellow_letters += row.count("yellow")

            made_guesses = len(submitted_word_list) - 1
            end_score = (green_letters * num_of_letters * 50) + (yellow_letters * (num_of_letters * 40)) - (
                    made_guesses * (guesses - made_guesses) * 30)

        end_score_text = menu_title_font.render(f"{end_score}", True, MENU_TITLE_COLOR)
        end_score_text_coords = center("x", end_score_text), score_text_y - 10
        screen.blit(end_score_text, end_score_text_coords)
        main_menu_button.blit_self()


def draw_keyboard():
    '''
    Draws the keyboard once to calculate the center of the screen depending on each rows' width,
    then it uses the result as the coordinates for each row.
    '''
    global has_rendered_all_rows_once
    text_x_start = SCREEN_WIDTH / 2 - alphabet_row_lengths[0] / 2
    text_y_start = 600
    text_x = text_x_start
    text_y = text_y_start
    spacing_x = 20
    spacing_y = 50

    # Renders each letter in each row.
    for row in range(len(keyboard_list)):
        row_length = 0

        # Changes the color of the letter depending on what nested list in keyboard_letter_color_list it is in.
        for letter in range(len(keyboard_list[row])):
            if keyboard_list[row][letter] in keyboard_letter_color_list[0]:
                color = TILE_GREEN

            elif keyboard_list[row][letter] in keyboard_letter_color_list[1]:
                color = TILE_YELLOW

            elif keyboard_list[row][letter] in keyboard_letter_color_list[2]:
                color = TILE_GRAY

            else:
                color = BLACK

            if not has_rendered_all_rows_once:
                color = WHITE

            render_letter = keyboard_font.render(keyboard_list[row][letter], True, color)
            screen.blit(render_letter, (text_x, text_y))
            # Prepares the x value for the next letter.
            text_x += render_letter.get_width() + spacing_x

            # Counts the widths of each row and saves them in alphabet_row_lengths only the first time running.
            if not has_rendered_all_rows_once:
                row_length += render_letter.get_width() + spacing_x

        if not has_rendered_all_rows_once:
            row_length -= 20
            alphabet_row_lengths[row] = row_length

        text_y += spacing_y
        # Sets the next x value based on the next rows own width, this requires an extra item in the list.
        text_x = SCREEN_WIDTH / 2 - alphabet_row_lengths[row + 1] / 2
    has_rendered_all_rows_once = True


def words_init():
    '''Reads words from word library to all_word_list.'''
    global all_word_list
    all_word_list = []

    with open(f"word_libraries/check_words/{num_of_letters}_letter_words.txt", "r") as word_file:
        for word in word_file:
            all_word_list.append(word.rstrip().upper())


def choose_word():
    '''Chooses a random word from a file, removes the newline and uppers it.'''
    word_list = []
    with open(f"word_libraries/pick_words/{num_of_letters}_letter_words.txt", "r") as word_file:
        for word in word_file:
            word_list.append(word.rstrip().upper())

    word = random.choice(word_list)
    print(f"chosen_word: {word}")
    return word


def draw_error_message(message):
    '''
    Takes the message string and draws it as a message on the screen.
    There can only be up to one message present at all times.
    '''
    global timestamp, alpha, error_message
    error_message = message
    render_text = error_font.render(message, True, WHITE)
    text_x = center("x", render_text)
    text_y = 50
    box_x = text_x - 8
    box_y = text_y - 5
    box_w = render_text.get_width() + 15
    box_h = render_text.get_height() + 10

    # Fades away the error message after MESSAGE_TIME_LIMIT ticks.
    if message is not None:
        if timestamp == 0:
            timestamp = pygame.time.get_ticks()

        if alpha > 0:
            if pygame.time.get_ticks() > timestamp + 5000:
                alpha -= 5

            pygame.gfxdraw.filled_polygon(screen,
                                          ((box_x, box_y), (box_x, box_y + box_h), (box_x + box_w, box_y + box_h),
                                           (box_x + box_w, box_y)), (0, 0, 0, alpha))
            if alpha > 10:
                screen.blit(render_text, (text_x, text_y))

        else:
            error_message = None
            alpha = 255
            timestamp = 0


def draw_tile(x, y, letter, tile_color):
    '''Draws a colored tile at x and y, then draws the text in the tile.'''
    if tile_color == "green":
        screen.blit(green_tile_img, (x, y))

    elif tile_color == "yellow":
        screen.blit(yellow_tile_img, (x, y))

    elif tile_color == "gray":
        screen.blit(gray_tile_img, (x, y))

    else:
        screen.blit(default_tile_img, (x, y))

    render_text = tile_font.render(letter, True, BLACK)
    text_coords = x + (default_tile_img.get_width() - render_text.get_width()) / 2, y + 5
    screen.blit(render_text, text_coords)


def draw_all_tiles(list_of_words):
    '''Draws the grid of all tiles and puts the written words in the tiles.'''
    spacing = default_tile_img.get_width() + 6
    start_x = SCREEN_WIDTH / 2 - (num_of_tiles_in_row * spacing - 8) / 2
    start_y = 70
    x = start_x
    y = start_y

    # For each row select a word to draw if there is one, else leave empty.
    for row in range(num_of_rows):
        if len(list_of_words) > row:
            word = list_of_words[row]

        else:
            word = ""

        # Draw letter in tiles if there is one, else draw nothing
        for column in range(num_of_letters):
            if len(word) > column:
                letter = word[column]

            else:
                letter = ""

            color = tile_color_index[row][column]
            draw_tile(x, y, letter, color)
            x += spacing

        x = start_x
        y += spacing


def word_submit_request(word):
    '''
    Checks if the word is a real word and if it's the right word.
    Ends the game if it is the right word, or if it was the last guess.
    '''
    global all_word_list, written_word, menu_screen
    print(f"Submitted word: {word}")

    # Checks if submitted word is long enough
    if len(written_word) != num_of_tiles_in_row:
        draw_error_message(error_msg_too_short)
        print(f"{word} is too short")

    else:
        if word in all_word_list:
            # Checks if word already guessed on.
            num_of_times_in_list = submitted_word_list.count(word)
            if num_of_times_in_list > 1:
                draw_error_message(error_msg_same_word)
                print(f"{word} is already submitted")

            # Saves the written word
            else:
                submitted_word_list.append(word)
                submitted_word_list[-1] = ""  # This line resets the editable row.
                written_word = ""  # This line resets the editable list.
                index_of_submitted_word = submitted_word_list.index(submitted_word_list[-2])
                print(f"{word} was accepted")

                # Updates the tile_color_index and the keyboard_letter_color_list depending on if each letter
                # in the submitted word is on the right spot in the word or not.
                for letter in range(num_of_letters):
                    if word[letter] == chosen_word[letter]:
                        tile_color_index[index_of_submitted_word][letter] = "green"
                        # Checks if the letter is not present in the nested lists in the keyboard_letter_color_list.
                        if not any(word[letter] in nested_list for nested_list in keyboard_letter_color_list[0]):
                            keyboard_letter_color_list[0].append(word[letter])

                    elif word[letter] in chosen_word:
                        tile_color_index[index_of_submitted_word][letter] = "yellow"
                        if not any(word[letter] in nested_list for nested_list in keyboard_letter_color_list[1]):
                            keyboard_letter_color_list[1].append(word[letter])

                    else:
                        tile_color_index[index_of_submitted_word][letter] = "gray"
                        if not any(word[letter] in nested_list for nested_list in keyboard_letter_color_list):
                            keyboard_letter_color_list[2].append(word[letter])
                print(f"submitted_word_list: {submitted_word_list}")

                # End game if it was the last guess.
                if len(submitted_word_list) > guesses:
                    print("Game Lost")
                    menu_screen = "lost"

                # End game if it was the right word.
                if submitted_word_list[-2] == chosen_word:
                    print("Game Won")
                    menu_screen = "won"
                print(f"tile_color_index {tile_color_index}")

        else:
            draw_error_message(error_msg_not_a_word)
            print(f"{word} wasn't recognized")
        print(f"keyboard_letter_color_list: {keyboard_letter_color_list}")


def start():
    '''Readies all necessary variables to start a new game.'''
    print("Start game")
    global chosen_word, menu_screen, end_score
    menu_screen = None
    words_init()
    chosen_word = choose_word()
    end_score = 0

    # Generate color indexes for all tiles
    for row_number in range(num_of_rows):
        tile_color_index.append([])
        for i in range(num_of_tiles_in_row):
            tile_color_index[row_number].append("")


def buttons_init():
    '''Sets up all buttons.'''
    global start_button, main_menu_button
    # Generates word length buttons
    to_side_of_menu = center("x", menu_background) + 40
    spacing = 0
    for i in range(4):
        word_length_buttons.append(MenuButton(f"{4 + i}", to_side_of_menu + spacing, 350))
        word_length_buttons[i].blit_self()
        spacing += 60

    # Generates amount of guesses buttons
    spacing = 0
    for i in range(6):
        amt_of_guesses_buttons.append(MenuButton(f"{2 + i}", to_side_of_menu + spacing, 450))
        spacing += 60

    # Selects two default options
    default_guesses = guesses - int(amt_of_guesses_buttons[0].text)
    default_length = num_of_letters - int(word_length_buttons[0].text)
    amt_of_guesses_buttons[default_guesses].is_selected = True
    word_length_buttons[default_length].is_selected = True

    # Generates start button
    start_button = MenuButton("Start", 0, 535)
    start_button.blit_self()
    start_button.x = SCREEN_WIDTH / 2 - start_button.width / 2

    # Generates main menu button
    main_menu_button = MenuButton("Main menu", 0, 530)
    main_menu_button.blit_self()
    main_menu_button.x = SCREEN_WIDTH / 2 - main_menu_button.width / 2


def main_menu():
    '''Resets all variables for a new round.'''
    print("Opened main menu")
    global tile_color_index, submitted_word_list, written_word, is_application_running, menu_screen,\
        keyboard_letter_color_list
    tile_color_index = []
    submitted_word_list = [""]
    written_word = ""
    keyboard_letter_color_list = [[], [], []]  # [[green_letters], [yellow_letters], [gray_letters]]
    is_application_running = True
    menu_screen = "main"


def word_edit_control(input):
    '''Checks how the player wants to edit the word.'''
    global written_word
    if input == pygame.K_RETURN:
        word_submit_request(written_word)

    # Remove the last letter in the written word
    elif input == pygame.K_BACKSPACE:
        written_word = written_word[:-1]
        submitted_word_list[-1] = written_word  # Updates the word on display

    # Uppers and saves the written word if it's a letter an if it's the right length
    if len(written_word) < num_of_tiles_in_row:
        if event.unicode.isalpha():
            written_word += event.unicode.upper()
            submitted_word_list[-1] = written_word

    else:
        draw_error_message(error_msg_max_length)
        print(f"Max word length reached")


def menu_button_functionality():
    '''Triggers button and changes its color if activated depending on what menu is active.'''
    global num_of_letters, num_of_tiles_in_row, guesses, num_of_rows
    # Changes color of pressed down button
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        active_mouse_coords = pygame.mouse.get_pos()

        if menu_screen == "main":
            # Checks if player selected a word length.
            for button in word_length_buttons:
                if button.background.collidepoint(active_mouse_coords):
                    num_of_letters = num_of_tiles_in_row = int(button.text)
                    print(f"length {button.text}")
                button.is_selected = False

            offset = int(word_length_buttons[0].text)
            word_length_buttons[num_of_letters - offset].is_selected = True

            # Checks if player selected the amount of guesses.
            for button in amt_of_guesses_buttons:
                if button.background.collidepoint(active_mouse_coords):
                    guesses = num_of_rows = int(button.text)
                    print(f"guesses {button.text}")
                button.is_selected = False

            offset = int(amt_of_guesses_buttons[0].text)
            amt_of_guesses_buttons[guesses - offset].is_selected = True

            # Changes color on start button if clicked.
            if start_button.background.collidepoint(active_mouse_coords):
                start_button.is_selected = True

        # Changes color on menu button if clicked.
        if menu_screen in ["won", "lost"]:
            if main_menu_button.background.collidepoint(active_mouse_coords):
                main_menu_button.is_selected = True

    # Changes the color of all not-clicked buttons and starts game or goes to menu depending on what button was clicked.
    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        active_mouse_coords = pygame.mouse.get_pos()
        if menu_screen == "main":
            if start_button.background.collidepoint(active_mouse_coords):
                start()
        if menu_screen in ["won", "lost"]:
            if main_menu_button.background.collidepoint(active_mouse_coords):
                main_menu()

        main_menu_button.is_selected = False
        start_button.is_selected = False


# ======= Game Starts Here =======
main_menu()
buttons_init()


# Main game loop
while is_application_running:
    screen.fill(BACKGROUND_COLOR)

    # Draws all items on screen depending on if a menu is open or not.
    if menu_screen != "main":
        draw_all_tiles(submitted_word_list)
        draw_keyboard()
        draw_error_message(error_message)

    if menu_screen is not None:
        draw_menu_screen(menu_screen)

    for event in pygame.event.get():
        # Closes the app if clicked on exit.
        if event.type == pygame.QUIT:
            is_application_running = False

        if event.type == pygame.KEYDOWN:
            # Stops the app.
            if event.key == pygame.K_DELETE or event.key == pygame.K_ESCAPE:
                is_application_running = False

            if menu_screen is None:
                word_edit_control(event.key)

        menu_button_functionality()

    # Updates screen
    pygame.display.flip()
    # Limit game loop to 60 times a second
    pygame.time.Clock().tick(60)
