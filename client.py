from pygame import *
import socket
import json
from threading import Thread

# ---ПУГАМЕ НАЛАШТУВАННЯ ---
WIDTH, HEIGHT = 800, 600
init()
screen = display.set_mode((WIDTH, HEIGHT))
clock = time.Clock()
display.set_caption("Пінг-Понг")
# ---СЕРВЕР ---
def connect_to_server():
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('localhost', 8080))
            buffer = ""
            game_state = {}
            my_id = int(client.recv(24).decode())
            return my_id, game_state, buffer, client
        except:
            pass


def receive():
    global buffer, game_state, game_over
    while not game_over:
        try:
            data = client.recv(1024).decode()
            buffer += data
            while "\n" in buffer:
                packet, buffer = buffer.split("\n", 1)
                if packet.strip():
                    game_state = json.loads(packet)
        except:
            game_state["winner"] = -1
            break

# --- ШРИФТИ ---
font_win = font.Font(None, 72)
font_main = font.Font(None, 50)
# --- ЗОБРАЖЕННЯ ----
assets = {} 
try: 
    assets["background"] = image.load("bacground.png") 
    assets["background"] = transform.scale(assets["background"], (800, 600))
    assets["ball"] = image.load("pingpong ball.png") 
    assets["ball"] = transform.scale(assets["ball"], (40, 40)) 
    assets["paddle1"] = image.load("paddle1.png")
    assets["paddle1"] = transform.scale(assets["paddle1"], (60, 80))

    assets["paddle2"] = image.load("paddle2.png")
    assets["paddle2"] = transform.scale(assets["paddle2"], (60, 80))
except Exception as e: 
    print(f"помилка при завантажені: {e}") 
    assets = {}
# --- ЗВУКИ --- 
mixer.init() 

sounds = {}  

try: 
    sounds["wall"] = mixer.Sound("soundreality-tennis-ball-hit-151257.mp3")  
    sounds["paddle"] = mixer.Sound("soundreality-tennis-ball-hit-151257.mp3")
    mixer.music.set_volume(0.4) 

except Exception as e:  
    print(f"you have an error: {e}")  




# --- ГРА ---
game_over = False
winner = None
you_winner = None
my_id, game_state, buffer, client = connect_to_server()
Thread(target=receive, daemon=True).start()
while True:
    for e in event.get():
        if e.type == QUIT:
            exit()  

    keys = key.get_pressed()
    if keys[K_UP]:
        client.send(b"UP")
    elif keys[K_DOWN]:
        client.send(b"DOWN") 
    elif keys[K_r]: 
        client.send(b"RESTART") 
        your_winner = None


    if "countdown" in game_state and game_state["countdown"] > 0: 
        you_winner = None
        screen.fill((0, 0, 0))
        countdown_text = font.Font(None, 72).render(str(game_state["countdown"]), True, (255, 255, 255))
        screen.blit(countdown_text, (WIDTH // 2 - 20, HEIGHT // 2 - 30))
        display.update()
        continue  # Не малюємо гру до завершення відліку

    if "winner" in game_state and game_state["winner"] is not None: 
        you_winner = None 
        screen.fill((20, 20, 20))

        if you_winner is None:  # Встановлюємо тільки один раз
            if game_state["winner"] == my_id:
                you_winner = True
            else:
                you_winner = False

        if you_winner:
            text = "Ти переміг!"
        else:
            text = "Пощастить наступним разом!"

        win_text = font_win.render(text, True, (255, 215, 0))
        text_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(win_text, text_rect)

        text = font_win.render('R - Restart', True, (255, 215, 0))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))
        screen.blit(text, text_rect)

        display.update()
        continue  # Блокує гру після перемоги

    if game_state: 
        if "background" in assets: 
            screen.blit(assets["background"], (0,0)) 
        else: 
            screen.fill((30, 30, 30)) 

        p0_y = game_state['paddles']['0']
        p1_y = game_state['paddles']['1']

        if "paddle1" in assets:
            screen.blit(assets["paddle1"], (20, p0_y))
        else:
            draw.rect(screen, (0, 255, 0), (20, p0_y, 20, 100))

        if "paddle2" in assets:
            screen.blit(assets["paddle2"], (WIDTH - 80, p1_y))
        else:
            draw.rect(screen, (255, 0, 255), (WIDTH - 40, p1_y, 20, 100))
        bx = game_state['ball']['x'] 
        by = game_state['ball']['y'] 
        if "ball" in assets: 
            ball_rect = assets["ball"].get_rect(center = (bx, by)) 
            screen.blit(assets["ball"], ball_rect) 
        else: 
            draw.circle(screen, (255, 255, 255), (bx, by), 10)
        score_text = font_main.render(f"{game_state['scores'][0]} : {game_state['scores'][1]}", True, (0, 0, 0))
        screen.blit(score_text, (WIDTH // 2 -40, 25))

        if game_state['sound_event']:
            if game_state['sound_event'] == 'wall_hit': 
                sounds["wall"].play() 
                # звук відбиття м'ячика від стін
            if game_state['sound_event'] == 'platform_hit': 
                sounds["paddle"].play() 
                # звук відбиття м'ячика від платформи
                

    else:
        wating_text = font_main.render(f"Очікування гравців...", True, (255, 255, 255))
        screen.blit(wating_text, (WIDTH // 2 - 25, 20))

    display.update()
    clock.tick(60)

   
