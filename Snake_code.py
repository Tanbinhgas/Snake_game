import pygame
import random
import sqlite3

pygame.init()
pygame.mixer.init()

# Âm thanh
pygame.mixer.music.load("Sound/Background.wav")   # nhạc nền
eat_sound = pygame.mixer.Sound("Sound/Eat.wav")   # ăn táo
hit_sound = pygame.mixer.Sound("Sound/Hit.wav")   # va chạm
gameover_sound = pygame.mixer.Sound("Sound/Gameover.wav")  # chết

# Load ảnh STOP
pause_img = pygame.image.load("assets/stop.jpg")
pause_img = pygame.transform.scale(pause_img, (200, 250))

# Làm mờ ảnh (overlay trắng mờ alpha)
pause_overlay = pygame.Surface((200, 250), pygame.SRCALPHA)
pause_overlay.fill((255, 255, 255, 120))
pause_img.blit(pause_overlay, (0, 0))

# Load ảnh Cup
trophy_img = pygame.image.load("assets/cup.png")
trophy_img = pygame.transform.scale(trophy_img, (50, 50))

# Load ảnh mộ
grave_img = pygame.image.load("assets/grave.png")
grave_img = pygame.transform.scale(grave_img, (150, 150))

# Kết nối database
conn = sqlite3.connect("snake_game.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS players (username TEXT PRIMARY KEY)")
cursor.execute("""
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    score INTEGER,
    FOREIGN KEY(username) REFERENCES players(username)
)
""")
conn.commit()

# Màn hình
width = 900
height = 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Rắn săn mồi")

# Rắn
clock = pygame.time.Clock()
snake_block = 30
snake_speed = 10

font_small = pygame.font.SysFont("Times new roman", 25)
font_medium = pygame.font.SysFont("Times new roman", 30)
font_large = pygame.font.SysFont("Times new roman", 100)
font_title = pygame.font.SysFont("Times new roman", 50)
menu_font = pygame.font.SysFont("Times new roman", 45)
button_font = pygame.font.SysFont("Times new roman", 30)
leaderboard_font = pygame.font.SysFont("Times new roman", 35)

# Màu sắc và màn hình
white = (255, 255, 255)
red = (213, 50, 80)
purple = (106, 13, 173)
green = (0, 255, 0)
light_green = (170, 215, 81)
dark_green = (162, 209, 73)
neon_green = (57, 255, 20)
blue = (50, 153, 213)
yellow = (0, 255, 255)
orange = (255, 165, 0)

# Hiệu ứng chữ phát sáng
def glow_text(text, font, x, y, color):
    main_text = font.render(text, True, color)

    for radius in range(6, 0, -2):
        glow_surf = font.render(text, True, color)
        glow_surf.set_alpha(30)
        screen.blit(glow_surf, (x - radius, y))
        screen.blit(glow_surf, (x + radius, y))
        screen.blit(glow_surf, (x, y - radius))
        screen.blit(glow_surf, (x, y + radius))

    screen.blit(main_text, (x, y))

# Vẽ nền gradient
def draw_gradient_background():
    top_color = (30, 0, 60)
    bottom_color = (5, 0, 20)
    for i in range(height):
        r = top_color[0] + (bottom_color[0] - top_color[0]) * i // height
        g = top_color[1] + (bottom_color[1] - top_color[1]) * i // height
        b = top_color[2] + (bottom_color[2] - top_color[2]) * i // height
        pygame.draw.line(screen, (r,g,b), (0,i), (width,i))
particles = []

# Hiệu ứng hạt
def spawn_particles():
    if len(particles) < 50:
        particles.append([random.randint(0, width), height, random.uniform(1, 2)])

# Vẽ hạt
def draw_particles():
    for p in particles:
        p[1] -= p[2]
        pygame.draw.circle(screen, (255,255,255), (int(p[0]), int(p[1])), 2)
        if p[1] <= 0:
            particles.remove(p)

# Vẽ nền
def draw_background():
    for r in range(0, height, snake_block):
        for c in range(0, width, snake_block):
            color = light_green if (r//snake_block + c//snake_block) % 2 == 0 else dark_green
            pygame.draw.rect(screen, color, (c, r, snake_block, snake_block))

# Load ảnh
def load(path):
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, (snake_block, snake_block))

head = {
    "UP": load("assets/head_up.png"),
    "DOWN": load("assets/head_down.png"),
    "LEFT": load("assets/head_left.png"),
    "RIGHT": load("assets/head_right.png")
}

body_straight = {
    "V": load("assets/body_vertical.png"),
    "H": load("assets/body_horizontal.png"),
}

body_curve = {
    "UR": load("assets/body_topright.png"),
    "UL": load("assets/body_topleft.png"),
    "DR": load("assets/body_bottomright.png"),
    "DL": load("assets/body_bottomleft.png")
}

tail_img = {
    "UP": load("assets/tail_up.png"),
    "DOWN": load("assets/tail_down.png"),
    "LEFT": load("assets/tail_left.png"),
    "RIGHT": load("assets/tail_right.png")
}

apple = load("assets/apple.png")

def draw_button(text, x, y, w, h, inactive_color, active_color):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x < mouse[0] < x + w and y < mouse[1] < y + h:
        pygame.draw.rect(screen, active_color, (x, y, w, h))
        if click[0] == 1:
            return True
    else:
        pygame.draw.rect(screen, inactive_color, (x, y, w, h))
    
    label = button_font.render(text, True, (20, 20, 20))
    screen.blit(label, (x + (w - label.get_width()) // 2, y + (h - label.get_height()) // 2))

    return False

def input_username():
    username = ""
    input_active = False
    placeholder = "Nickname"

    input_box = pygame.Rect(width//2 - 150, 275, 300, 50)
    play_button = pygame.Rect(width//2 + 170, 275, 100, 50)

    while True:
        draw_gradient_background()
        spawn_particles()
        draw_particles()

        # Nút chiếc cúp góc trên phải
        trophy_rect = pygame.Rect(width - 70, 20, 50, 50)
        screen.blit(trophy_img, trophy_rect.topleft)

        # Tiêu đề
        glow_text("Enter Nickname", font_title, width//2 - 170, 200, (0,255,200))

        # Khung nhập nickname
        border_color = (0,200,255) if input_active else (100,120,150)
        pygame.draw.rect(screen, (25,40,70), input_box, border_radius=10)
        pygame.draw.rect(screen, border_color, input_box, 2, border_radius=10)

        # Placeholder & text
        if not username and not input_active:
            placeholder_surface = font_medium.render(placeholder, True, (130,130,150))
            screen.blit(placeholder_surface, (input_box.x + 10, input_box.y + 10))
        else:
            text_surface = font_medium.render(username, True, white)
            screen.blit(text_surface, (input_box.x + 10, input_box.y + 10))

        # Vẽ nút PLAY
        mouse = pygame.mouse.get_pos()
        color = (0,255,150) if play_button.collidepoint(mouse) else (0,180,100)
        pygame.draw.rect(screen, color, play_button, border_radius=8)

        play_text = font_medium.render("PLAY", True, (0,0,0))
        screen.blit(play_text, (play_button.centerx - play_text.get_width()//2,
                                play_button.centery - play_text.get_height()//2))

        pygame.display.update()

        # Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # click vào ô nhập
                if input_box.collidepoint(event.pos):
                    input_active = True
                else:
                    input_active = False
                
                # Khi click vào nút cúp
                if trophy_rect.collidepoint(event.pos):
                    result = leaderboard_screen()
                    if result == "menu":
                        continue

                # click vào nút PLAY
                if play_button.collidepoint(event.pos) and username.strip():
                    cursor.execute("INSERT OR IGNORE INTO players (username) VALUES (?)", (username,))
                    conn.commit()
                    return username

            if event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_RETURN and username.strip():
                    cursor.execute("INSERT OR IGNORE INTO players (username) VALUES (?)", (username,))
                    conn.commit()
                    return username
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif len(username) < 15 and event.unicode.isprintable():
                    username += event.unicode

# Màn hình menu
def menu_screen():
    pygame.mixer.music.load("Sound/Background.wav")
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.4)
    pulse = 0
    pulse_direction = 1

    while True:
        draw_gradient_background()
        spawn_particles()
        draw_particles()

        # Tựa game glow
        pulse += 0.04 * pulse_direction
        if pulse > 1: pulse_direction = -1
        if pulse < 0: pulse_direction = 1
        glow_val = int(120 + 120 * pulse)
        title_color = (glow_val, 255, 5)
        glow_text("SNAKE HUNT PREY", font_title, width//2 - 235, 130, title_color)

        # Menu hướng dẫn
        prompt = font_small.render("Nhấn ENTER để chơi", True, (255,255,255))
        screen.blit(prompt, (width//2 - prompt.get_width()//2, 300))

        prompt2 = font_small.render("Nhấn ESC để thoát", True, (200,200,200))
        screen.blit(prompt2, (width//2 - prompt2.get_width()//2, 340))

        pygame.display.update()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "start"
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()

def save_score_once(username, score):
    cursor.execute("SELECT MAX(score) FROM scores WHERE username = ?", (username,))
    row = cursor.fetchone()
    current_best = row[0] if row and row[0] is not None else None

    if current_best is None or score > current_best:
        cursor.execute("INSERT INTO scores (username, score) VALUES (?, ?)", (username, score))
        conn.commit()

def get_top_players(limit=5):
    cursor.execute("""
        SELECT username, MAX(score) AS top_score
        FROM scores
        GROUP BY username
        ORDER BY top_score DESC
        LIMIT ?
    """, (limit,))
    return cursor.fetchall()

def score_display(score):
    value = font_medium.render("Điểm: " + str(score), True, white)
    screen.blit(value, [2, 550])

# Lấy hướng giữa 2 điểm
def get_dir(a, b):
    ax, ay = int(a[0]), int(a[1]); bx, by = int(b[0]), int(b[1])
    if ax < bx: return "RIGHT"
    if ax > bx: return "LEFT"
    if ay < by: return "DOWN"
    if ay > by: return "UP"
    return "RIGHT"

# Vẽ con rắn
def draw_snake(snake_list):
    if len(snake_list) < 2:
        return
    # đuôi rắn
    tx, ty = snake_list[0]
    tail_dir = get_dir(snake_list[1], snake_list[0])
    screen.blit(tail_img[tail_dir], (int(tx), int(ty)))

    # thân rắn
    for i in range(1, len(snake_list)-1):
        px, py = snake_list[i-1]
        x, y = snake_list[i]
        nx, ny = snake_list[i+1]

        # kiểm tra thẳng hay cong
        if int(px) == int(nx):
            screen.blit(body_straight["V"], (int(x), int(y)))
        elif int(py) == int(ny):
            screen.blit(body_straight["H"], (int(x), int(y)))
        else:
            d1 = get_dir([x,y], [px,py])
            d2 = get_dir([x,y], [nx,ny])
            key = None

            if (d1=="UP" and d2=="RIGHT") or (d2=="UP" and d1=="RIGHT"): key="UR"
            elif (d1=="UP" and d2=="LEFT") or (d2=="UP" and d1=="LEFT"): key="UL"
            elif (d1=="DOWN" and d2=="RIGHT") or (d2=="DOWN" and d1=="RIGHT"): key="DR"
            elif (d1=="DOWN" and d2=="LEFT") or (d2=="DOWN" and d1=="LEFT"): key="DL"

            if key is not None:
                screen.blit(body_curve[key], (int(x), int(y)))
            else:
                # fallback tránh crash
                if int(px) == int(nx):
                    screen.blit(body_straight["V"], (int(x), int(y)))
                else:
                    screen.blit(body_straight["H"], (int(x), int(y)))

    # đầu rắn
    hx, hy = snake_list[-1]
    head_dir = get_dir(snake_list[-2], snake_list[-1])
    screen.blit(head[head_dir], (int(hx), int(hy)))

# Hiển thị tin nhắn
def message(msg, color, y_offset=0, font_used=font_medium):
    mesg = font_used.render(msg, True, color)
    text_rect = mesg.get_rect(center=(width / 2, height / 2 + y_offset))
    screen.blit(mesg, text_rect)

def leaderboard_screen():
    while True:
        draw_leaderboard()

        msg = font_small.render("Nhấn SPACE để tiếp tục", True, (255,255,255))
        screen.blit(msg, (width//2 - msg.get_width()//2, 550))

        pygame.display.update()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return "menu"

def draw_leaderboard():
    draw_gradient_background()
    spawn_particles()
    draw_particles()

    # Tiêu đề glow
    glow_text("BẢNG XẾP HẠNG", font_title, width//2 - 200, 60, (57,255,20))

    top_players = get_top_players()

    card_width = 480
    card_height = 60
    start_y = 160
    spacing = 15

    for i, (name, score) in enumerate(top_players):
        x = width//2 - card_width//2
        y = start_y + i * (card_height + spacing)

        # màu rank
        if i == 0: color = (neon_green)
        elif i == 1: color = (orange)
        elif i == 2: color = (yellow)
        else: color = (255,255,255)

        # bo góc nền card
        pygame.draw.rect(screen, (10,10,30), (x, y, card_width, card_height), border_radius=12)

        # viền sáng
        pygame.draw.rect(screen, color, (x, y, card_width, card_height), 2, border_radius=12)

        # nội dung
        text = f"{i+1}. {name}"
        score_txt = f"{score} điểm"
        
        label = font_medium.render(text, True, color)
        score_label = font_medium.render(score_txt, True, color)

        screen.blit(label, (x + 20, y + 12))
        screen.blit(score_label, (x + card_width - score_label.get_width() - 20, y + 12))

def game_loop(username):
    played_gameover_sound = False
    x = (width // (2 * snake_block)) * snake_block
    y = (height // (2 * snake_block)) * snake_block
    dx, dy = snake_block, 0
    snake_list = [[x - snake_block, y], [x, y]]
    length = 2
    last_direction = "RIGHT"
    paused = False
    game_over = False
    game_close = False
    score_saved = False

    # tạo nhiều thức ăn
    num_apples = 5
    foods = []

    def spawn_food():
        fx = random.randrange(0, width, snake_block)
        fy = random.randrange(0, height, snake_block)
        return [fx, fy]
    
    for _ in range(num_apples):
        foods.append(spawn_food())

    # vòng lặp chính
    while not game_over:
        while game_close:
            if not played_gameover_sound:
                pygame.mixer.music.stop()
                gameover_sound.play()
                played_gameover_sound = True
                message("GAME OVER!", red, -200, font_large)
                score_display(length - 1)

            # Lưu điểm một lần
            if not score_saved:
                save_score_once(username, length - 1)
                score_saved = True

            # Hiện nút lựa chọn
            msg = font_small.render("Nhấn SPACE để tiếp tục", True, white)
            screen.blit(msg, (width//2 - msg.get_width()//2, 350))

            # Hiển thị ảnh ngôi mộ ở giữa
            grave_x = width // 2 - grave_img.get_width() // 2
            grave_y = height // 2 - 100
            screen.blit(grave_img, (grave_x, grave_y))

            pygame.display.update()
            clock.tick(10)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        result = leaderboard_screen()
                        if result == "menu":
                            return "menu"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and last_direction != "RIGHT":
                    dx, dy = -snake_block, 0
                    last_direction = "LEFT"
                elif event.key == pygame.K_RIGHT and last_direction != "LEFT":
                    dx, dy = snake_block, 0
                    last_direction = "RIGHT"
                elif event.key == pygame.K_UP and last_direction != "DOWN":
                    dx, dy = 0, -snake_block
                    last_direction = "UP"
                elif event.key == pygame.K_DOWN and last_direction != "UP":
                    dx, dy = 0, snake_block
                    last_direction = "DOWN"
                elif event.key == pygame.K_SPACE:
                    paused = not paused

        if paused:
            # Vẽ nền và rắn trước khi pause (để không bị đen màn hình)
            draw_background()
            for f in foods:
                screen.blit(apple, (int(f[0]), int(f[1])))
            draw_snake(snake_list)
            score_display(length - 1)

            # Hiển thị ảnh STOP mờ ở giữa màn hình
            screen.blit(pause_img, (width//2 - 100, height//2 - 125))

            # Text hướng dẫn
            msg = font_small.render("Nhấn SPACE để tiếp tục", True, white)
            screen.blit(msg, (width//2 - msg.get_width()//2, height//2 + 150))

            pygame.display.update()
            clock.tick(10)
            continue

        x += dx
        y += dy

        # va chạm tường
        if x < 0 or x >= width or y < 0 or y >= height:
            hit_sound.play()
            game_close = True

        draw_background()
        # vẽ thức ăn
        for f in foods:
            screen.blit(apple, (int(f[0]), int(f[1])))

        snake_head = [int(x), int(y)]
        snake_list.append(snake_head)
        if len(snake_list) > length:
            del snake_list[0]

        for segment in snake_list[:-1]:
            if segment == snake_head:
                hit_sound.play()
                game_close = True

        # draw snake (pass snake_list)
        draw_snake(snake_list)
        score_display(length - 1)
        pygame.display.update()

        # kiểm tra ăn từng quả táo
        for f in foods[:]:
            if abs(x - f[0]) < snake_block and abs(y - f[1]) < snake_block:
                length += 1
                eat_sound.play()
                foods.remove(f)
                # thêm quả mới
                new_f = spawn_food()
                # đảm bảo không spawn lên rắn
                while new_f in snake_list or new_f in foods:
                    new_f = spawn_food()
                foods.append(new_f)
                break

        clock.tick(snake_speed)

while True:
    action = menu_screen()

    if action == "start":
        username = input_username()
        if not username:
            continue
        result = game_loop(username)

        if result == "restart":
            continue
        elif result == "menu":
            continue
        elif result == "exit":
            break

pygame.quit()
conn.close()
