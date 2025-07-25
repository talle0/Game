#pip install pygame
import pygame
import random
import math
import sys

# 설정
W, H = 1000, 700
COLORS = [(231,76,60), (52,152,219), (46,204,113), (241,196,15)]
WHITE, BLACK, GRAY, LIGHT_GRAY, DARK_GRAY = (255,255,255), (0,0,0), (149,165,166), (236,240,241), (52,73,94)

class Player:
    def __init__(self, i):
        self.name = f"Player {i+1}"
        self.color = COLORS[i]
        self.pos = self.x = self.y = self.tx = self.ty = 0
        self.moving = self.steps = self.timer = 0

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Disaster Boardgame")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small = pygame.font.Font(None, 18)
        
        # 배경 이미지 로드 시도
        try:
            # 업로드된 이미지를 읽어서 사용
            # 실제 사용시에는 아래 파일명을 업로드한 파일명으로 변경하세요
            import os
            if os.path.exists("disaster.jpg"):
                self.bg_image = pygame.image.load("disaster.jpg")
                self.bg_image = pygame.transform.scale(self.bg_image, (400, 300))
            else:
                # 첨부된 이미지를 직접 로드하는 방법
                # 파일이 같은 폴더에 있다면 파일명을 여기에 입력하세요
                self.bg_image = None
        except:
            self.bg_image = None
            print("배경 이미지를 로드할 수 없습니다. 기본 배경을 사용합니다.")
        
        # 게임 상태
        self.turn = 0
        self.dice = 1
        self.state = 0  # 0:대기, 1:굴리기, 2:이동, 3:턴완료
        self.timer = self.turn_timer = 0
        self.log = []
        
        # 플레이어 생성
        self.players = [Player(i) for i in range(4)]
        
        # 18칸 게임판 생성
        self.board = []
        l, t, w, h = 150, 150, 400, 300
        # 하단 6칸
        for i in range(6): self.board.append((l + i * w//5, t + h))
        # 오른쪽 3칸
        for i in range(1, 4): self.board.append((l + w, t + h - i * h//4))
        # 상단 6칸
        for i in range(6): self.board.append((l + w - i * w//5, t))
        # 왼쪽 3칸
        for i in range(1, 4): self.board.append((l, t + i * h//4))
        
        # 시작 위치 설정
        for p in self.players:
            p.x = p.y = p.tx = p.ty = self.board[0][0]
            p.y = p.ty = self.board[0][1]
        
        self.log_msg("=== Game Started! ===")
        self.log_msg(f"{self.players[0].name}'s turn")
    
    def log_msg(self, msg):
        self.log.append(msg)
        if len(self.log) > 8: self.log.pop(0)
    
    def draw_disaster_background(self):
        """게임판 중앙에 배경 그리기"""
        if self.bg_image:
            # 업로드된 배경 이미지 사용
            self.screen.blit(self.bg_image, (150, 150))
            
            # 이미지 위에 반투명 오버레이로 칸들이 잘 보이게 함
            overlay = pygame.Surface((400, 300))
            overlay.set_alpha(60)
            overlay.fill((255, 255, 255))
            self.screen.blit(overlay, (150, 150))
        else:
            # 기본 배경 (단순한 재해 테마)
            overlay = pygame.Surface((400, 300))
            overlay.set_alpha(50)
            overlay.fill((100, 100, 100))
            self.screen.blit(overlay, (150, 150))
    
    def handle_click(self, pos):
        if 620 <= pos[0] <= 670 and 210 <= pos[1] <= 260 and self.state == 0:
            self.state = 1
            self.timer = pygame.time.get_ticks() + 1000
            self.log_msg(f"{self.players[self.turn].name} rolls...")
    
    def update(self):
        now = pygame.time.get_ticks()
        p = self.players[self.turn]
        
        # 주사위 굴리기
        if self.state == 1:
            self.dice = random.randint(1, 6)
            if now >= self.timer:
                self.dice = random.randint(1, 6)
                self.log_msg(f"Result: {self.dice}")
                self.state = 2
                p.steps = self.dice
                p.moving = 1
                self.move_next()
        
        # 이동 중
        elif self.state == 2 and p.moving:
            dx, dy = p.tx - p.x, p.ty - p.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > 2:
                p.x += dx/dist * 5
                p.y += dy/dist * 5
            else:
                p.x, p.y = p.tx, p.ty
                if p.steps > 0:
                    if now >= p.timer:
                        self.move_next()
                else:
                    p.moving = 0
                    self.state = 3
                    self.turn_timer = now + 1000
                    self.log_msg(f"{p.name} done!")
        
        # 턴 완료
        elif self.state == 3 and now >= self.turn_timer:
            self.turn = (self.turn + 1) % 4
            self.state = 0
            self.log_msg(f"{self.players[self.turn].name}'s turn")
    
    def move_next(self):
        p = self.players[self.turn]
        if p.steps > 0:
            old = p.pos
            p.pos = (p.pos + 1) % 18
            if p.pos < old:
                self.log_msg(f"{p.name} passed START!")
            p.tx, p.ty = self.board[p.pos]
            p.steps -= 1
            p.timer = pygame.time.get_ticks() + 300
    
    def draw(self):
        self.screen.fill(LIGHT_GRAY)
        
        # 제목
        title = self.font.render("Disaster Boardgame", True, DARK_GRAY)
        self.screen.blit(title, (W//2 - 80, 30))
        
        # 게임판 테두리
        pygame.draw.rect(self.screen, DARK_GRAY, (120, 120, 460, 360), 3)
        
        # 배경 그리기
        self.draw_disaster_background()
        
        # 칸 그리기
        for i, (x, y) in enumerate(self.board):
            pygame.draw.circle(self.screen, WHITE, (x, y), 25)
            pygame.draw.circle(self.screen, BLACK, (x, y), 25, 2)
            txt = self.small.render(str(i+1), True, BLACK)
            self.screen.blit(txt, (x-5, y-5))
        
        # 중앙 로고
        if self.bg_image:
            # 배경 이미지가 있을 때는 텍스트를 더 눈에 띄게
            logo_text = "Disaster BoardGame"
            text_surface = self.font.render(logo_text, True, WHITE)
            text_rect = text_surface.get_rect(center=(350, 290))
            
            # 텍스트 배경 박스
            bg_rect = text_rect.copy()
            bg_rect.inflate_ip(20, 10)
            pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect)
            pygame.draw.rect(self.screen, WHITE, bg_rect, 2)
            
            self.screen.blit(text_surface, text_rect)
        else:
            logo = self.font.render("Disaster BoardGame", True, DARK_GRAY)
            self.screen.blit(logo, (270, 290))
        
        # 플레이어
        for i, p in enumerate(self.players):
            ox, oy = (i%2)*16-8, (i//2)*16-8
            x, y = int(p.x + ox), int(p.y + oy)
            pygame.draw.circle(self.screen, p.color, (x, y), 8)
            pygame.draw.circle(self.screen, BLACK, (x, y), 8, 2)
            txt = self.small.render(str(i+1), True, WHITE)
            self.screen.blit(txt, (x-4, y-6))
        
        # UI
        x = 620
        curr = self.players[self.turn]
        
        # 현재 플레이어
        txt = self.font.render(f"Current: {curr.name}", True, curr.color)
        self.screen.blit(txt, (x, 150))
        
        # 주사위
        color = WHITE if self.state == 0 else GRAY
        pygame.draw.rect(self.screen, color, (x, 210, 50, 50))
        pygame.draw.rect(self.screen, BLACK, (x, 210, 50, 50), 2)
        
        # 주사위 점
        dots = {1:[(0,0)], 2:[(-1,-1),(1,1)], 3:[(-1,-1),(0,0),(1,1)],
                4:[(-1,-1),(1,-1),(-1,1),(1,1)], 5:[(-1,-1),(1,-1),(0,0),(-1,1),(1,1)],
                6:[(-1,-1),(1,-1),(-1,0),(1,0),(-1,1),(1,1)]}
        for dx, dy in dots[self.dice]:
            pygame.draw.circle(self.screen, BLACK, (x+25+dx*10, 235+dy*10), 3)
        
        # 상태 메시지
        msgs = ["Click to roll", "Rolling...", "Moving...", "Turn complete"]
        txt = self.small.render(msgs[self.state], True, BLACK)
        self.screen.blit(txt, (x, 280))
        
        # 플레이어 위치
        for i, p in enumerate(self.players):
            color = p.color if i == self.turn else BLACK
            txt = self.small.render(f"{p.name}: Space {p.pos+1}", True, color)
            self.screen.blit(txt, (x, 320 + i*20))
        
        # 로그
        txt = self.font.render("Game Log:", True, BLACK)
        self.screen.blit(txt, (x, 450))
        for i, msg in enumerate(self.log):
            txt = self.small.render(msg, True, DARK_GRAY)
            self.screen.blit(txt, (x, 475 + i*18))
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
            
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    Game().run()