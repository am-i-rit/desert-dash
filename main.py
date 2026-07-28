"""Dino Game in Python
A game similar to the famous Chrome Dino Game, built using pygame-ce.
Made by Amrit Bhasin (@am-i-rit)
506934a4767bf8a57212d379c311f01f09cb2710
"""
import pygame
import random

# Initialize Pygame and create a window
pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption("Desert Dash: Amrit Bhasin")
clock = pygame.time.Clock()
running = True  # Pygame main loop, kills pygame when False
start_time = 0
score = 0
score_received = False
current_spawn_delay = 1000  # Initial spawn delay in ms
MIN_OBSTACLE_SPACING = 160

def score_printer() -> int:
    """
    Updates and displays the player's score.

    Adds 1 to the score every 300 milliseconds and applies multipliers.

    Returns:
        score (int): The current score.
    """

    global score, last_score_update_time, score_multiplier, multiplier_end_time

    time = pygame.time.get_ticks()

    if time - last_score_update_time >= 300:
        score += 1 * score_multiplier
        last_score_update_time = time

    if score_multiplier > 1 and time > multiplier_end_time:
        score_multiplier = 1

    if score_multiplier == 1:
        score_surf = score_font.render(f"{score}", False, (0,0,0))
    else:
        score_surf = score_font.render(f"{score}", False, (255,255,0))
    score_rect = score_surf.get_rect(center=(400, 60))
    screen.blit(score_surf, score_rect)
    
    return score

def obstacle_move(obstacle_list: list[tuple[str, pygame.Surface, pygame.Rect]], speed: int
                  ) -> list[tuple[str, pygame.Surface, pygame.Rect]]:
    """
    Moves all the obstacles to the left and blits them to the screen.

    Args:
        obstacle_list (list): List of obstacles as tuples of (kind, surface, rect).
        speed (int): Speed at which obstacles move left.

    Returns:
        list: Updated list of obstacles still on screen.
    """

    if obstacle_list: # if the list has something in it 
        for kind, surface, rect in obstacle_list: 
            rect.x -= speed

            if kind == "bat":
                surface = bat_surf
            
            elif kind == "cactus1": 
                surface = cactus1_surf
            elif kind == "cactus2":
                surface = cactus2_surf
            
            else: # kind = 'tumbleweed'
                surface = tumbleweed_surf

            screen.blit(surface, rect)
            
            # deletes obstacles that are off-screen
            obstacle_list = [(kind, surface, rect) for (kind, surface, rect) in obstacle_list if rect.x > -80]

        return obstacle_list
    else: # if the list is empty
        return []

def powerup_move(powerup_list: list[tuple[str, pygame.Surface, pygame.Rect]]
                 ) -> list[tuple[str, pygame.Surface, pygame.Rect]]:
    """
    Moves power-ups to the left and blits them to the screen.

    Args:
        powerup_list (list): List of power-ups as tuples of (kind, surface, rect).

    Returns:
        list: Updated list of power-ups still on screen.
    """

    if powerup_list:
        for kind, surface, rect in powerup_list:
            rect.x -= current_game_speed

            if kind == 'heart':
                surface = heart_surf
            elif kind == 'multiplier':
                surface = multiplier_surf
            elif kind == "laser":
                surface = powerup_laser_surf

            screen.blit(surface, rect)

            powerup_list = [(kind, surface, rect) for (kind, surface, rect) in powerup_list if rect.x > -80]
        return powerup_list
    
    else: return []

def powerup_collision() -> None:
    """
    Detects and handles collisions between the player and power-ups.

    Updates lives, score multiplier, or laser count depending on
    which power-up was collided with.
    """

    global lives, too_many_lives_frame_counter, score_multiplier, multiplier_end_time, laser_count
    
    for kind, _, rect in powerup_list:
        if rect.colliderect(player_rect):
            if kind == 'heart' and lives <= 2:
                lives += 1
            elif kind == 'heart':
                screen.blit(maxlives_message, (35 + (35 * (lives - 1)), 65))
                too_many_lives_frame_counter = 60
            elif kind == 'multiplier':
                score_multiplier = 2
                multiplier_end_time = pygame.time.get_ticks() + 6000  # 3 seconds from now
            elif kind == "laser" and laser_count < 4:
                laser_count += 1
                

            rect.x = -100 # teleports powerup away so collision only occurs once

def animate(frames: list[pygame.Surface], index: float, fps: float
            ) -> tuple[pygame.Surface, float]:
    """
    Animates a list of frames based on the desired frames per second.

    Args:
        frames (list): List of frame surfaces to animate.
        index (float): Current frame index.
        fps (float): Desired animation speed (frames per second).

    Returns:
        tuple: (Current surface to display, updated index)
    """

    index += (fps / 60)
    if index >= len(frames) - 0.1:
        index = 0
    surface = frames[int(index)]
    return surface, index

def animate_player() -> None:
    """
    Animates the player's sprite depending on whether the player is in the air or on the ground.

    If the player is jumping, the jump frame is shown. Otherwise, a walking animation plays.
    """

    global player_surf, player_index

    if player_rect.bottom < GROUND_Y: # display jump frame if in air
        player_surf = player_jump
    else: # display walking animation if on ground
        player_index += 0.1
        player_surf = player_walk[int(player_index)]
        if player_index >= len(player_walk) - 0.1:
            player_index = 0

    screen.blit(player_surf, player_rect)
    # pygame.draw.rect(screen, (255, 0, 0), player_rect, 2) # hitboxes for troubleshooting

def animate_heart() -> None:
    """
    Animates the heart and displays a message if the player has max lives.
    """

    global heart_surf
    global heart_index
    global too_many_lives_frame_counter

    heart_index += 0.10
    if heart_index >= len(heart_animation) - 0.1:
        heart_index = 0

    heart_surf = heart_animation[int(heart_index)]

    # display message if max lives
    if too_many_lives_frame_counter > 0:
        screen.blit(maxlives_message, (40, 65))
        too_many_lives_frame_counter -= 1

def display_leaderboard() -> None:
    """
    Displays the leaderboard on the screen.

    Takes the top scores from the 'highscores' list and displays them.
    Each entry is shown with its rank number and score.
    """

    highscore_surf = score_font.render(f"Leaderboard:", False, (0,0,0))
    highscore_rect = highscore_surf.get_rect(center=(600, 120))
    screen.blit(highscore_surf, highscore_rect)

    # blits each entry in highscores
    for i, highscore in enumerate(highscores):
        hs_surf = score_font.render(f"#{i+1}: {highscore}", False, (0, 0, 0))
        hs_rect = hs_surf.get_rect(center=(600, 155 + i * 30))
        screen.blit(hs_surf, hs_rect)

def update_difficulty() -> int:
    """
    Updates game speed and obstacle spawn delay based on current time.

    Returns:
    game_speed (int): The current game speed
    """
    global current_spawn_delay

    # Recalculate time using start_time
    current_time = pygame.time.get_ticks() - start_time
    difficulty_level = max(0, current_time // 5000)

    new_spawn_delay = max(400, 1000 - difficulty_level * 50)

    if new_spawn_delay != current_spawn_delay:
        pygame.time.set_timer(obstacle_timer, new_spawn_delay)
        current_spawn_delay = new_spawn_delay

    potential_speed = int(5 + (current_time / 12000))
    game_speed = min(potential_speed, 19)
    # print(game_speed) # for troubleshooting
    return game_speed

def find_distance(obstacle, player_rect) -> int:
    """
    Finds the horizontal distance between the player and an obstacle.

    Args:
        obstacle (tuple): Obstacle tuple of (kind, surface, rect).
        player_rect (pygame.Rect): Player's rectangle.

    Returns:
        int: Horizontal distance in pixels.
    """

    return obstacle[2].x - player_rect.x

def shoot_laser(player_rect: pygame.Rect, laser_surf: pygame.Surface, 
            obstacle_list: list[tuple[str, pygame.Surface, pygame.Rect]]
) -> list[tuple[pygame.Rect, pygame.Rect]]:
    """
    Shoots a laser at the nearest obstacle that is ahead of the player.

    Filters obstacles ahead of the player, selects the closest one,
    creates a laser rect aimed at it, and stores the target.

    Args:
        player_rect (pygame.Rect): The rectangle representing the player.
        laser_surf (pygame.Surface): Surface used to draw the laser.
        obstacle_list (list): List of obstacles as (kind, surface, rect).

    Returns:
        list: List of (laser_rect, target_rect) tuples
    """

    global targeted_obstacles
    forward_obstacles = []
    laser_list = []

    for obstacle in obstacle_list:
        if find_distance(obstacle, player_rect) > 0 and obstacle not in targeted_obstacles:
            forward_obstacles.append(obstacle)
    
    def key_func(obstacle):
        return find_distance(obstacle, player_rect)
    
    forward_obstacles = sorted(forward_obstacles, key=key_func)

    
    for i in range(min(1, len(forward_obstacles))):
        target_obstacle = forward_obstacles[i][2]
        laser_rect = laser_surf.get_rect(midleft=(player_rect.right, player_rect.centery))
        laser_list.append((laser_rect, target_obstacle))
        targeted_obstacles.append(forward_obstacles[i]) 

    return laser_list

def auto_shoot(player_rect: pygame.Rect, laser_surf: pygame.Surface, 
            obstacle_list: list[tuple[str, pygame.Surface, pygame.Rect]], 
        lasers: list[tuple[pygame.Rect, pygame.Rect]]) -> list[tuple[pygame.Rect, pygame.Rect]]:
    """
    Automatically fires lasers at obstacles while the laser power-up is active.
    Ensures a cooldown between shots and stops shooting when the duration ends.

    Args:
        player_rect (pygame.Rect): The rectangle representing the player.
        laser_surf (pygame.Surface): Surface used to draw the laser.
        obstacle_list (list): List of obstacles as (kind, surface, rect).
        lasers (list): Current list of active lasers.

    Returns:
        list: Updated list of lasers with new ones added if fired.
    """

    global auto_shoot_active, auto_shoot_start_time, last_shot_time, current_time

    current_time = pygame.time.get_ticks() - start_time

    if not auto_shoot_active:
        return lasers
    
    if current_time - auto_shoot_start_time > auto_shoot_duration:
        auto_shoot_active = False
        return lasers

    if current_time - last_shot_time >= shoot_cooldown:
        lasers.extend(shoot_laser(player_rect, laser_surf, obstacle_list))
        last_shot_time = current_time
    
    return lasers

def move_lasers(laser_list: list[tuple[pygame.Rect, pygame.Rect]], 
                laser_surface: pygame.surface, speed: int
                ) -> list[tuple[pygame.Rect, pygame.Rect]]:
    """
    Moves each laser toward its target and displays it on the screen.

    Each laser homes in on its target obstacle with a direction vector.

    Args:
        laser_list (list): List of (laser_rect, target_rect) tuples, representing active lasers and their targets.
        laser_surface (pygame.Surface): The surface (image) used to draw the laser.
        speed (int): The pixel speed at which the laser moves.

    Returns:
        list: Updated list of (laser_rect, target_rect) tuples still on screen.
    """

    updated_lasers = []

    for laser_rect, target_rect in laser_list:
        x_distance = target_rect.centerx - laser_rect.centerx
        y_distance = target_rect.centery - laser_rect.centery

        dist = (x_distance**2 + y_distance**2) ** 0.5 # pythagorean theorem

        if dist != 0:
            # calculates how much of the distance is horizontal and how much is vertical
            x_distance_proportion = x_distance / dist
            y_distance_proportion = y_distance / dist

            # so that both horizontal and vertical movements finish simultaneously
            laser_rect.x += x_distance_proportion * speed
            laser_rect.y += y_distance_proportion * speed
        
        screen.blit(laser_surface, laser_rect) 

        if laser_rect.x < 800: 
            updated_lasers.append((laser_rect, target_rect))

    return updated_lasers

def laser_collision(laser_list: list[tuple[pygame.Rect, pygame.Rect]]
                    ) -> list[tuple[pygame.Rect, pygame.Rect]]:
    """
    Detects and handles collisions between lasers and their target obstacles.
    Removes both the obstacle and the laser when a collision occurs.

    Args:
        laser_list (list): List of (laser_rect, target_rect) tuples.

    Returns:
        list: Updated laser list with only un-collided lasers.
    """

    updated_lasers = []

    for laser_rect, target_rect in laser_list:
        if laser_rect.colliderect(target_rect):
            target_rect.x = -80  # this will remove it from the list elsewhere
        else:
            updated_lasers.append((laser_rect, target_rect))

    return updated_lasers

def display_lasermeter() -> None:
    """
    Displays the player's current laser charge/meter, for the laser power-up.
    Draws a frame from 'lasermeter_frames' based on the current laser count.
    """
    lasermeter_index = min(laser_count, 4)
    screen.blit(lasermeter_frames[lasermeter_index], (650, 30))
    if lasermeter_index == 4:
        screen.blit(meter_full, meter_full_rect) 


def reset_variables() -> None:
    """
    Resets all game state variables back to their default values.
    """

    global game_state, score, score_multiplier, multiplier_end_time, score_received
    global last_score_update_time, obstacle_list, powerup_list, lives, start_time, current_time
    global players_gravity_speed, player_index, sky_x, ground_x, auto_shoot_active
    global auto_shoot_start_time, last_shot_time, targeted_obstacles, lasers, laser_count

    game_state = 'playing'
    score = 0
    score_multiplier = 1
    multiplier_end_time = 0
    score_received = False
    last_score_update_time = 0
    obstacle_list = []
    powerup_list = []
    lives = 1
    start_time = pygame.time.get_ticks()
    players_gravity_speed = 0
    player_rect.bottom = GROUND_Y
    player_index = 0
    current_spawn_delay = 1000
    sky_x = 0
    ground_x = 0
    auto_shoot_active = False
    auto_shoot_start_time = 0
    last_shot_time = 0
    targeted_obstacles = []
    lasers = []
    laser_count = 0
    current_time = 0

    pygame.time.set_timer(obstacle_timer, current_spawn_delay)
    pygame.time.set_timer(heart_timer, random.randint(10000, 15000))
    pygame.time.set_timer(multiplier_timer, random.randint(20000, 25000))
    pygame.time.set_timer(laser_timer, random.randint(16000, 19000)) 

# Game state variables
is_playing = False  # Whether in game or in menu
game_state = 'main_menu'
GROUND_Y = 300  # The Y-coordinate of the ground level
JUMP_GRAVITY_START_SPEED = -18 # The speed at which the player jumps
players_gravity_speed = 0  # The current speed at which the player falls
lives = 1
last_score_update_time = 0
score = 0
score_multiplier = 1
multiplier_end_time = 0
sky_x = 0
ground_x = 0
closest_obstacles = []
auto_shoot_active = False
auto_shoot_start_time = 0
auto_shoot_duration = 5000  
last_shot_time = 0
shoot_cooldown = 250 
targeted_obstacles = []
laser_count = 0
too_many_lives_frame_counter = 0

# Load level assets
SKY_SURF = pygame.image.load('graphics/level/gamesky.png')
GROUND_SURF = pygame.image.load("graphics/level/Ground-2.png").convert() 

# fonts
# downloaded from https://www.1001fonts.com/marlboro-font.html
game_font = pygame.font.Font("graphics/marlboro/Marlboro/Marlboro.ttf", 50)
score_font = pygame.font.Font("graphics/marlboro/Marlboro/Marlboro.ttf", 35)
small_font = pygame.font.Font("graphics/marlboro/Marlboro/Marlboro.ttf", 20)

lives_surf = pygame.image.load('graphics/heart/heart5.png').convert_alpha()
lives_surf = pygame.transform.rotozoom(lives_surf, 0, 2.3)

maxlives_message = small_font.render(f"Max lives reached!", False, (0,0,0))

# Load player assets
laser_surf = pygame.transform.rotozoom(pygame.image.load('graphics/level/laser.png'),0,0.8)
lasers = []

player_walk1 = pygame.image.load("graphics/player/player_walk_1.png").convert_alpha()
player_walk2 = pygame.image.load("graphics/player/player_walk_2.png").convert_alpha()
player_walk3 = pygame.image.load("graphics/player/player_walk_3.png").convert_alpha()
player_walk4 = pygame.image.load("graphics/player/player_walk_4.png").convert_alpha()
player_walk = [pygame.transform.rotozoom(frame, 0, 1.3) for frame in [player_walk1, player_walk2, player_walk3, player_walk4]]
player_index = 0

player_surf = player_walk[player_index]
player_jump = pygame.transform.rotozoom(pygame.image.load("graphics/player/player_jump.png").convert_alpha(), 0, 0.26)
player_rect = player_surf.get_rect(bottomleft=(35, GROUND_Y))

# Load assets for Obstacles
cactus_1a_surf = pygame.image.load("graphics/cactus/cactus1a.png").convert_alpha()
cactus_1b_surf = pygame.image.load("graphics/cactus/cactus1b.png").convert_alpha()
cactus1_frames = [cactus_1a_surf, cactus_1b_surf]
cactus1_index = 0
cactus1_surf = cactus1_frames[cactus1_index]

cactus_2a_surf = pygame.image.load("graphics/cactus/cactus2a.png").convert_alpha()
cactus_2b_surf = pygame.image.load("graphics/cactus/cactus2b.png").convert_alpha()
cactus2_frames = [cactus_2a_surf, cactus_2b_surf]
cactus2_index = 0
cactus2_surf = cactus2_frames[cactus2_index]

tumbleweed_base = pygame.image.load("graphics/tumbleweed.png").convert_alpha()
tumbleweed_frames = [
    tumbleweed_base,
    pygame.transform.rotate(tumbleweed_base, 120),  # 120° rotation
    pygame.transform.rotate(tumbleweed_base, 240)   # 240° rotation
]

tumbleweed_index = 0
tumbleweed_surf = tumbleweed_frames[tumbleweed_index]

bat1_surf = pygame.image.load("graphics/bat/bat_1.png").convert_alpha()
bat2_surf = pygame.image.load("graphics/bat/bat_2.png").convert_alpha()

bat1_surf = pygame.transform.rotozoom(bat1_surf, 0, 0.35) 
bat2_surf = pygame.transform.rotozoom(bat2_surf, 0, 0.35)

bat_animation = [bat1_surf, bat2_surf]
bat_index = 0
bat_surf = bat_animation[bat_index]

obstacle_list = []

# load assets for powerups
heart1_surf = pygame.image.load("graphics/heart/heart1.png").convert_alpha()
heart2_surf = pygame.image.load("graphics/heart/heart2.png").convert_alpha()
heart3_surf = pygame.image.load("graphics/heart/heart3.png").convert_alpha()
heart4_surf = pygame.image.load("graphics/heart/heart4.png").convert_alpha()
heart5_surf = pygame.image.load("graphics/heart/heart5.png").convert_alpha()

multiplier_surf = pygame.image.load("graphics/star/2x_multiplier.png").convert_alpha()
multiplier_surf = pygame.transform.rotozoom(multiplier_surf, 0, 1.3)

laser1_surf = pygame.image.load("graphics/laser/laser1.png").convert_alpha()
laser2_surf = pygame.image.load("graphics/laser/laser2.png").convert_alpha()
powerup_laser_frames = [pygame.transform.rotozoom(img, 0, 1.3) for img in [laser1_surf, laser2_surf]]
laser_index = 0
powerup_laser_surf = powerup_laser_frames[laser_index]

lasermeter0_surf = pygame.image.load("graphics/laser/lasermeter0.png").convert_alpha()
lasermeter1_surf = pygame.image.load("graphics/laser/lasermeter1.png").convert_alpha()
lasermeter2_surf = pygame.image.load("graphics/laser/lasermeter2.png").convert_alpha()
lasermeter3_surf = pygame.image.load("graphics/laser/lasermeter3.png").convert_alpha()
lasermeter4_surf = pygame.image.load("graphics/laser/lasermeter4.png").convert_alpha()
lasermeter_frames = [pygame.transform.rotozoom(img, 0, 1.3) for img in [lasermeter0_surf, 
                lasermeter1_surf, lasermeter2_surf, lasermeter3_surf, lasermeter4_surf]]
meter_full = small_font.render("Press 'L' to activate!", True, (0,0,0))
meter_full_rect = meter_full.get_rect(center = (700, 100))

lasermeter_surf = lasermeter_frames[laser_count]

powerup_list = []

heart_animation = [pygame.transform.rotozoom(img, 0, 2.3) for img in [heart1_surf,heart2_surf,heart3_surf,heart4_surf,heart5_surf]]
heart_index = 0
heart_surf = heart_animation[heart_index]

# stuff for main menu
cactus_scaled1 = pygame.transform.rotozoom(cactus1_surf, 5, 2.5)
cactus_scaled1_rect = cactus_scaled1.get_rect(center =(600,200))

cactus_scaled2 = pygame.transform.rotozoom(cactus2_surf, -5, 2.5)
cactus_scaled2_rect = cactus_scaled2.get_rect(center =(200,200))

player_menu = pygame.transform.rotozoom(player_jump, 0, 2)
player_menu_rect = player_menu.get_rect(center = (400, 200))

play_menu = score_font.render("Press space to play       Press 'I' for instructions", False, (0,0,0))
play_menu_rect = play_menu.get_rect(midbottom = (400, 350))

game_name = game_font.render("Desert Dash", True, (0,0,0))
game_name_rect = game_name.get_rect(center = (400, 50))
# list of stuff to blit
main_menu_stuff = [(cactus_scaled1, cactus_scaled1_rect), (play_menu, play_menu_rect), (game_name, game_name_rect),
    (cactus_scaled2, cactus_scaled2_rect), (player_menu, player_menu_rect)]

# stuff for instructions screen

how_to_play = game_font.render("Instructions", True, (0,0,0))
how_to_play_rect = how_to_play.get_rect(center = (400,50))

controls = score_font.render("Controls", True, (0,0,0))
controls_rect = controls.get_rect(center = (133, 100))

# Jump text
jump_line1 = small_font.render("Press the up arrow", True, (0,0,0))
jump_line2 = small_font.render("or space to jump", True, (0,0,0))
jump_text = [jump_line1, jump_line2]

jump_line1_rect = jump_line1.get_rect(center=(133,150))
jump_line2_rect = jump_line2.get_rect(center=(133,170))
jump_text_rect = [jump_line1_rect, jump_line2_rect]

fallfaster1 = small_font.render("Hold the down arrow", True, (0,0,0))
fallfaster2 = small_font.render("while mid-air to", True, (0,0,0))
fallfaster3 = small_font.render("fall faster", True, (0,0,0))
fall_faster_text = [fallfaster1, fallfaster2, fallfaster3]

fallfaster1_rect = fallfaster1.get_rect(center=(133, 220))
fallfaster2_rect = fallfaster2.get_rect(center=(133, 240))
fallfaster3_rect = fallfaster3.get_rect(center=(133, 260))
fall_faster_rect = [fallfaster1_rect, fallfaster2_rect, fallfaster3_rect]

activatelaser1 = small_font.render("When the laser meter is", True, (0,0,0))
activatelaser2 = small_font.render("fully charged, press", True, (0,0,0))
activatelaser3 = small_font.render("'L' to activate it", True, (0,0,0))
activate_laser_text = [activatelaser1, activatelaser2, activatelaser3]

activatelaser1_rect = activatelaser1.get_rect(center=(133, 295))
activatelaser2_rect = activatelaser2.get_rect(center=(133, 315))
activatelaser3_rect = activatelaser3.get_rect(center=(133, 335))
activate_laser_rect = [activatelaser1_rect, activatelaser2_rect, activatelaser3_rect]


#activate_laser_text = small_font.render("When the laser meter\nis fully charged, press\n'L' to activate it", True, (0,0,0))
#activate_laser_rect = activate_laser_text.get_rect(center=(133, 315))

obstacles_text = score_font.render("Obstacles", True, (0,0,0))
obstacles_text_rect = obstacles_text.get_rect(center = (400, 100))

avoidtext1 = small_font.render("Below are the", True, (0,0,0))
avoidtext2 = small_font.render("obstacles, try", True, (0,0,0))
avoidtext3 = small_font.render("to avoid them!", True, (0,0,0))
avoid_text = [avoidtext1, avoidtext2, avoidtext3]
avoidtext1_rect = avoidtext1.get_rect(center = (400, 140))
avoidtext2_rect = avoidtext2.get_rect(center = (400, 160))
avoidtext3_rect = avoidtext3.get_rect(center = (400, 180))
avoid_text_rect = [avoidtext1_rect, avoidtext2_rect, avoidtext3_rect]

#avoid_text = small_font.render("Below are the\nobstacles, try\n to avoid them!", True, (0,0,0))
#avoid_text_rect = avoid_text.get_rect(center = (400, 160))

cactus_shrunk_rect = cactus1_surf.get_rect(center = (350, 235))

tumbleweed_rect_menu = tumbleweed_surf.get_rect(center = (430, 235))

bat_scaled = pygame.transform.rotozoom(bat2_surf, 0, 0.8)
bat_scaled_rect = bat_scaled.get_rect(center = (400, 300))

powerup_text = score_font.render("Power-ups", True, (0,0,0))
powerup_text_rect = powerup_text.get_rect(center = (667, 100))

heartstar1 = small_font.render("Heart: Adds another life", True, (0,0,0))
heartstar2 = small_font.render("Star: Gives 2x score boost", True, (0,0,0))
heartstar3 = small_font.render("Laser: Fills up meter", True, (0,0,0))
heart_star_text = [heartstar1, heartstar2, heartstar3]
heartstar1_rect = heartstar1.get_rect(center = (667, 140))
heartstar2_rect = heartstar2.get_rect(center = (667, 160))
heartstar3_rect = heartstar3.get_rect(center = (667, 180))
heart_star_text_rect = [heartstar1_rect, heartstar2_rect, heartstar3_rect]

#heart_star_text = small_font.render("Heart: Adds another life\nStar: Gives 2x score boost\nLaser: Fills up meter", True, (0,0,0))
#heart_star_text_rect = heart_star_text.get_rect(center = (667, 160))

back_from_instructions = score_font.render("Press 'B' to go back", True, (0,0,0))
back_from_instructions_rect = back_from_instructions.get_rect(midbottom = (400, 390))

menu_laser_rect = laser1_surf.get_rect(center = (600, 220))
menu_laser_meter = lasermeter4_surf.get_rect(center = (700, 220))

pressL_1 = small_font.render("When meter is full,", True, (0,0,0))
pressL_2 = small_font.render("press 'L' to shoot", True, (0,0,0))
pressL_3 = small_font.render("lasers at obstacles for", True, (0,0,0))
pressL_4 = small_font.render("5 seconds!", True, (0,0,0))
press_L = [pressL_1, pressL_2, pressL_3, pressL_4]
pressL_1_rect = pressL_1.get_rect(center = (667, 270))
pressL_2_rect = pressL_2.get_rect(center = (667, 290))
pressL_3_rect = pressL_3.get_rect(center = (667, 310))
pressL_4_rect = pressL_4.get_rect(center = (667, 330))
press_L_rect = [pressL_1_rect, pressL_2_rect, pressL_3_rect, pressL_4_rect]

#press_L = small_font.render("When meter is full,\npress 'L' to shoot\nlasers at obstacles for\n5 seconds!", True, (0,0,0))
#press_L_rect = press_L.get_rect(center = (667, 300))

# list of stuff to blit
instruction_screen_stuff = [(how_to_play, how_to_play_rect), (controls, controls_rect), 
    (obstacles_text, obstacles_text_rect), (powerup_text, powerup_text_rect), (jump_text, jump_text_rect),
    (fall_faster_text, fall_faster_rect), (activate_laser_text, activate_laser_rect), (avoid_text, avoid_text_rect),
    (cactus1_surf, cactus_shrunk_rect), (tumbleweed_surf, tumbleweed_rect_menu), (bat_scaled, bat_scaled_rect),
    (heart_star_text, heart_star_text_rect), (back_from_instructions, back_from_instructions_rect), 
    (laser1_surf, menu_laser_rect), (lasermeter4_surf, menu_laser_meter), (press_L, press_L_rect)]

# stuff for end screen

game_over = game_font.render('Game over!', True, (0,0,0))
game_over_rect = game_over.get_rect(center = (400, 50))

end_playagain = score_font.render("Press space to play again    Press 'B' to go to menu", True, (0,0,0))
end_playagain_rect = end_playagain.get_rect(midbottom = (400, 350))

end_cactus = pygame.transform.rotozoom(cactus1_surf, 0, 2.2)
end_cactus_rect = end_cactus.get_rect(center = (200, 220))

# list of stuff to blit
end_screen_stuff = [(game_over, game_over_rect), (end_cactus, end_cactus_rect), 
(end_playagain, end_playagain_rect)]

# create times for obstacle/powerup spawning
obstacle_timer = pygame.USEREVENT + 1
difficulty_level = max(0, (pygame.time.get_ticks() - start_time) // 5000) # helps make game harder
spawn_delay = max(400, 1000 - (difficulty_level * 50)) # obstacle spawn more often as game progresses
pygame.time.set_timer(obstacle_timer, spawn_delay)

heart_timer = pygame.USEREVENT + 2
heart_spawn_rng = random.randint(10000,15000)
pygame.time.set_timer(heart_timer, heart_spawn_rng)

multiplier_timer = pygame.USEREVENT + 3
multiplier_spawn_rng = random.randint(20000,25000)
pygame.time.set_timer(multiplier_timer, multiplier_spawn_rng)

laser_timer = pygame.USEREVENT + 4
laser_spawn_rng = random.randint(16000,19000)
pygame.time.set_timer(laser_timer, laser_spawn_rng)

with open("highscores.txt", "a") as f:
    pass 

while running:
    # Check for events
    for event in pygame.event.get():
        # pygame.QUIT --> user clicked X to close your window
        if event.type == pygame.QUIT:
            running = False

        elif game_state == 'main_menu':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: # restart game
                    reset_variables()
                elif event.key == pygame.K_i:
                    game_state = 'instructions'
        
        elif game_state == 'instructions':
            if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                game_state = 'main_menu'
                
        elif game_state == "end_screen":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: # restart game
                    reset_variables()
                elif event.key == pygame.K_b: # go back
                    game_state = 'main_menu'            
                
        elif game_state == 'playing':
            # When player wants to jump by pressing SPACE or up arrow
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_SPACE or event.key == pygame.K_UP) and player_rect.bottom >= GROUND_Y:
                    players_gravity_speed = JUMP_GRAVITY_START_SPEED
            # Activate laser shooting when its allowed
                elif event.key == pygame.K_l and laser_count == 4:
                    auto_shoot_active = True
                    auto_shoot_start_time = pygame.time.get_ticks() - start_time
                    last_shot_time = 0
                    targeted_obstacles = []
                    laser_count = 0

            # append to obstacle list
            if event.type == obstacle_timer:
                if not obstacle_list or obstacle_list[-1][2].x < 800 - MIN_OBSTACLE_SPACING:
                    obstacle_spawn_point = random.randint(800, 1200)
                    obstacle_spawn_rng = random.random()
                    if obstacle_spawn_rng <= (1/10):
                        tumbleweed_rect = tumbleweed_surf.get_rect(bottomleft=(obstacle_spawn_point,GROUND_Y))
                        obstacle_list.append(('tumbleweed', tumbleweed_surf, tumbleweed_rect))
                    elif obstacle_spawn_rng <= (23/60):
                        cactus1_rect = cactus1_surf.get_rect(bottomleft=(obstacle_spawn_point, GROUND_Y))
                        obstacle_list.append(("cactus1", cactus1_surf, cactus1_rect,))
                    elif obstacle_spawn_rng <= (40/60):
                        cactus2_rect = cactus2_surf.get_rect(bottomleft=(obstacle_spawn_point, GROUND_Y))
                        obstacle_list.append(("cactus2", cactus2_surf, cactus2_rect))
                    else: # obstacle_spawn_rng > (40/60)
                        bat_rect = bat_surf.get_rect(center=(obstacle_spawn_point, 155))
                        obstacle_list.append(("bat", bat_surf, bat_rect))

            # append to powerup list
            if event.type == heart_timer:
                heart_rect = heart_surf.get_rect(midbottom=(random.randint(850, 1000), random.randint(150, GROUND_Y - 10)))
                powerup_list.append(("heart", heart_surf, heart_rect))
            
            if event.type == multiplier_timer:
                multiplier_rect = multiplier_surf.get_rect(midbottom=(random.randint(850, 1000), random.randint(150, GROUND_Y - 10)))
                powerup_list.append(("multiplier", multiplier_surf, multiplier_rect))
            
            if event.type == laser_timer:
                powerup_laser_rect = powerup_laser_surf.get_rect(midbottom=(random.randint(850, 1000), random.randint(150, GROUND_Y - 10)))
                powerup_list.append(("laser", powerup_laser_surf, powerup_laser_rect))


    if game_state == 'playing':
        # check for down arrow press (for fast fall)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN] and player_rect.bottom < GROUND_Y:
            players_gravity_speed += 3 
        else:
            players_gravity_speed += 1
        
        player_rect.y += players_gravity_speed
        
        # ensure player cant go underground
        if player_rect.bottom > GROUND_Y:
            player_rect.bottom = GROUND_Y

        # update game speed
        current_game_speed = update_difficulty()


        lasers = auto_shoot(player_rect, laser_surf, obstacle_list, lasers)

        # handle obstacle collisions
        for kind, surface, rect in obstacle_list:
            if rect.colliderect(player_rect):
                lives -= 1
                rect.x = -100
                if lives == 0:
                    game_state = 'end_screen'
        
        # handle power-up and laser collisions
        powerup_collision()
        lasers = laser_collision(lasers)
        
        if auto_shoot_active and current_time - auto_shoot_start_time > 5000:
            auto_shoot_active = False
            targeted_obstacles = []

    # Rendering    
    if game_state == 'main_menu':
        screen.fill((246,178,107))
        for (surface, rect) in main_menu_stuff:
            screen.blit(surface, rect)
       
    elif game_state == 'instructions':
        screen.fill((250, 137, 137))
        for (surface, rect) in instruction_screen_stuff:
            if isinstance(surface, list):
                for s, r in zip(surface, rect):
                    screen.blit(s, r)
            else:
                screen.blit(surface, rect)
       
    elif game_state == "end_screen":
        screen.fill((246,178,107))
        if not score_received:
            # store 5 highest scores in a file
            score_received = True
            with open('highscores.txt', 'a') as file:
                file.write(f"{score}\n")
            
            highscores = []
            with open("highscores.txt", "r") as file:
                highscores = sorted([int(line.strip()) for line in file], reverse=True)[:5]
            
            with open('highscores.txt', 'w') as file:
                for highscore in highscores:
                    file.write(f"{highscore}\n")
        # blit end screen            
        for (surface, rect) in end_screen_stuff:
            screen.blit(surface, rect)
        display_leaderboard() 
        # Display final score
        final_score_surf = score_font.render(f"Your Score: {score}", True, (0, 0, 0))
        final_score_rect = final_score_surf.get_rect(center=(220, 120))
        screen.blit(final_score_surf, final_score_rect)
        
    elif game_state == 'playing':
        # clear screen
        screen.fill("purple")  

        # scroll sky and ground
        sky_x -= 0.25
        ground_x -= 1

        if sky_x <= -1200: sky_x = 0
        if ground_x <= -1200: ground_x = 0

        # blit sky and ground
        screen.blit(SKY_SURF, (sky_x, 0))
        screen.blit(SKY_SURF, (sky_x + 1200, 0))

        screen.blit(GROUND_SURF, (ground_x, GROUND_Y))
        screen.blit(GROUND_SURF, (ground_x + 1200, GROUND_Y))

        # move obstacles, power-ups, lasers, and animate player
        obstacle_list = obstacle_move(obstacle_list, current_game_speed)  
        powerup_list = powerup_move(powerup_list)   
        animate_player()                              
        lasers = move_lasers(lasers, laser_surf, 17)  

        # print score
        score = score_printer()
        # blit # of lives
        for i in range(lives):
            screen.blit(lives_surf, (35 + (35 * (i)), 40))
        display_lasermeter()

        # animations
        animate_heart()
        bat_surf, bat_index = animate(bat_animation, bat_index, 3)
        cactus1_surf, cactus1_index = animate(cactus1_frames, cactus1_index, 4)
        cactus2_surf, cactus2_index = animate(cactus2_frames, cactus2_index, 4)
        tumbleweed_surf, tumbleweed_index = animate(tumbleweed_frames, tumbleweed_index, 5)
        powerup_laser_surf, laser_index = animate(powerup_laser_frames, laser_index, 4)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit() 