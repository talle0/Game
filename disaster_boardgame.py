# 재난 대비 보드게임
# 참여자들이 전국 안전을 담당하는 직책이 되어 재난 대비를 경쟁하는 게임

import pygame
import random
import math
import sys
import csv
import os

# ===== 설정 =====
W, H = 1920, 1080
COLORS = [(231,76,60), (52,152,219), (46,204,113), (241,196,15)]
WHITE, BLACK, GRAY, LIGHT_GRAY, DARK_GRAY = (255,255,255), (0,0,0), (149,165,166), (236,240,241), (52,73,94)
BLUE = (52, 152, 219)
RED = (231, 76, 60)
GREEN = (46, 204, 113)

class FontManager:
    """폰트 관리 클래스 - 한글 폰트 우선순위로 로드"""
    def __init__(self):
        self.fonts = {}
        self.load_fonts()
    
    def load_fonts(self):
        # 한글 폰트 우선순위 목록
        korean_fonts = [
            "malgungothic",     # 맑은 고딕
            "namumsquare",      # 나눔스퀘어
            "notosanskr",       # Noto Sans KR
            "applegothic",      # 애플 고딕 (macOS)
            "batang",           # 바탕
            "dotum",            # 돋움
            "gulim",            # 굴림
        ]
        
        # 시스템 폰트도 확인
        available_fonts = pygame.font.get_fonts()
        
        # 한글 폰트 찾기
        selected_font = None
        for font in korean_fonts:
            if font in available_fonts:
                selected_font = font
                break
        
        # 기본 폰트가 없으면 시스템 기본 폰트 사용
        if not selected_font:
            selected_font = pygame.font.get_default_font()
        
        # 다양한 크기의 폰트 생성
        try:
            self.fonts['large'] = pygame.font.SysFont(selected_font, 32, bold=True)
            self.fonts['medium'] = pygame.font.SysFont(selected_font, 24)
            self.fonts['small'] = pygame.font.SysFont(selected_font, 18)
            self.fonts['tiny'] = pygame.font.SysFont(selected_font, 14)
        except:
            # 폰트 로드 실패시 기본 폰트 사용
            self.fonts['large'] = pygame.font.Font(None, 32)
            self.fonts['medium'] = pygame.font.Font(None, 24)
            self.fonts['small'] = pygame.font.Font(None, 18)
            self.fonts['tiny'] = pygame.font.Font(None, 14)
    
    def get_font(self, size='medium'):
        return self.fonts.get(size, self.fonts['medium'])

def draw_text_wrapped(surface, text, font, color, rect, center=False):
    """텍스트를 지정된 영역에 맞춰 줄바꿈하여 그리기"""
    words = text.split(' ')
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= rect.width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line.strip())
                current_line = word + " "
            else:
                lines.append(word)
                current_line = ""
    
    if current_line:
        lines.append(current_line.strip())
    
    # 텍스트 그리기
    y_offset = rect.y
    line_height = font.get_height()
    
    for line in lines:
        if y_offset + line_height > rect.y + rect.height:
            break
            
        text_surface = font.render(line, True, color)
        if center:
            x = rect.x + (rect.width - text_surface.get_width()) // 2
        else:
            x = rect.x
        surface.blit(text_surface, (x, y_offset))
        y_offset += line_height

class Tile:
    def __init__(self, x1, x2, x3, x4):
        self.x1 = x1  # 대분류: 0(재난), 1(예산), 2(이벤트)
        self.x2 = x2  # 중분류
        self.x3 = x3  # 소분류
        self.x4 = x4  # 특수효과: 0(없음), 1(1번더), 2(출발지점스킵), 3(효과2배)

class Player:
    def __init__(self, name):
        self.name = name
        self.position = 0
        self.year = 1
        self.budget = 5000
        self.damage = 0
        self.safety_awareness = 0  # 시민안전인식
        self.tech_level = 0        # 기술수준
        self.readiness = 0         # 대비수준
        self.finished = False
        self.color = WHITE

class StatAllocationScreen:
    def __init__(self, screen, player_name, font_manager):
        self.screen = screen
        self.player_name = player_name
        self.font_manager = font_manager
        self.points = 25
        self.stats = {"시민안전인식": 0, "기술수준": 0, "대비수준": 0}
        self.done = False

    def draw(self):
        self.screen.fill((240, 240, 240))
        
        # 제목
        title_font = self.font_manager.get_font('large')
        title = title_font.render(f"{self.player_name} 스탯 분배", True, BLACK)
        title_rect = title.get_rect(center=(W//2, 100))
        self.screen.blit(title, title_rect)
        
        # 남은 포인트
        points_font = self.font_manager.get_font('medium')
        points_text = points_font.render(f"남은 포인트: {self.points}", True, RED)
        points_rect = points_text.get_rect(center=(W//2, 150))
        self.screen.blit(points_text, points_rect)

        # 스탯 목록
        start_y = 250
        for i, (stat_name, value) in enumerate(self.stats.items()):
            y = start_y + i * 120
            
            # 스탯 이름과 값
            stat_font = self.font_manager.get_font('medium')
            stat_text = stat_font.render(f"{stat_name}: {value}", True, BLACK)
            self.screen.blit(stat_text, (W//2 - 200, y))
            
            # + 버튼
            plus_rect = pygame.Rect(W//2 + 50, y - 10, 60, 40)
            color = BLUE if self.points > 0 else GRAY
            pygame.draw.rect(self.screen, color, plus_rect)
            plus_text = stat_font.render("+", True, WHITE)
            plus_text_rect = plus_text.get_rect(center=plus_rect.center)
            self.screen.blit(plus_text, plus_text_rect)
            
            # - 버튼
            minus_rect = pygame.Rect(W//2 + 120, y - 10, 60, 40)
            color = RED if value > 0 else GRAY
            pygame.draw.rect(self.screen, color, minus_rect)
            minus_text = stat_font.render("-", True, WHITE)
            minus_text_rect = minus_text.get_rect(center=minus_rect.center)
            self.screen.blit(minus_text, minus_text_rect)

        # 확인 버튼
        if self.points == 0:
            confirm_rect = pygame.Rect(W//2 - 100, 600, 200, 60)
            pygame.draw.rect(self.screen, GREEN, confirm_rect)
            confirm_font = self.font_manager.get_font('medium')
            confirm_text = confirm_font.render("확인", True, WHITE)
            confirm_text_rect = confirm_text.get_rect(center=confirm_rect.center)
            self.screen.blit(confirm_text, confirm_text_rect)

        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        while not self.done:
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    
                    start_y = 250
                    for i, stat_name in enumerate(self.stats.keys()):
                        y = start_y + i * 120
                        
                        # + 버튼
                        plus_rect = pygame.Rect(W//2 + 50, y - 10, 60, 40)
                        if plus_rect.collidepoint(mx, my) and self.points > 0:
                            self.stats[stat_name] += 1
                            self.points -= 1
                        
                        # - 버튼
                        minus_rect = pygame.Rect(W//2 + 120, y - 10, 60, 40)
                        if minus_rect.collidepoint(mx, my) and self.stats[stat_name] > 0:
                            self.stats[stat_name] -= 1
                            self.points += 1

                    # 확인 버튼
                    if self.points == 0:
                        confirm_rect = pygame.Rect(W//2 - 100, 600, 200, 60)
                        if confirm_rect.collidepoint(mx, my):
                            self.done = True

            clock.tick(30)
        return self.stats

class StatUpgradeUI:
    def __init__(self, screen, stat_name, player_budget, font_manager):
        self.screen = screen
        self.stat_name = stat_name
        self.player_budget = player_budget
        self.font_manager = font_manager
        self.unit_cost = 200
        self.selected = 0
        self.done = False

    def draw(self):
        self.screen.fill((250, 250, 250))
        
        # 제목
        title_font = self.font_manager.get_font('large')
        title = title_font.render(f"{self.stat_name} 강화", True, BLACK)
        title_rect = title.get_rect(center=(W//2, 100))
        self.screen.blit(title, title_rect)

        # 예산 정보
        budget_font = self.font_manager.get_font('medium')
        budget_text = budget_font.render(f"현재 예산: {self.player_budget:,}$", True, BLACK)
        budget_rect = budget_text.get_rect(center=(W//2, 150))
        self.screen.blit(budget_text, budget_rect)

        # 강화 옵션들 (5x2 그리드)
        start_x = W//2 - 300
        start_y = 220
        
        for i in range(1, 11):
            col = (i - 1) % 5
            row = (i - 1) // 5
            
            x = start_x + col * 120
            y = start_y + row * 100
            
            cost = i * self.unit_cost
            affordable = self.player_budget >= cost
            
            # 버튼 색상
            if not affordable:
                color = GRAY
            elif self.selected == i:
                color = GREEN
            else:
                color = BLUE
            
            rect = pygame.Rect(x, y, 100, 80)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 2)
            
            # 텍스트
            button_font = self.font_manager.get_font('small')
            plus_text = button_font.render(f"+{i}", True, WHITE)
            cost_text = self.font_manager.get_font('tiny').render(f"{cost:,}$", True, WHITE)
            
            plus_rect = plus_text.get_rect(center=(x + 50, y + 25))
            cost_rect = cost_text.get_rect(center=(x + 50, y + 55))
            
            self.screen.blit(plus_text, plus_rect)
            self.screen.blit(cost_text, cost_rect)

        # 확인 및 취소 버튼
        button_y = 500
        confirm_rect = pygame.Rect(W//2 - 150, button_y, 120, 60)
        cancel_rect = pygame.Rect(W//2 + 30, button_y, 120, 60)
        
        pygame.draw.rect(self.screen, GREEN, confirm_rect)
        pygame.draw.rect(self.screen, RED, cancel_rect)
        
        button_font = self.font_manager.get_font('medium')
        confirm_text = button_font.render("확인", True, WHITE)
        cancel_text = button_font.render("취소", True, WHITE)
        
        confirm_text_rect = confirm_text.get_rect(center=confirm_rect.center)
        cancel_text_rect = cancel_text.get_rect(center=cancel_rect.center)
        
        self.screen.blit(confirm_text, confirm_text_rect)
        self.screen.blit(cancel_text, cancel_text_rect)

        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        while not self.done:
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    
                    # 강화 옵션 버튼들
                    start_x = W//2 - 300
                    start_y = 220
                    
                    for i in range(1, 11):
                        col = (i - 1) % 5
                        row = (i - 1) // 5
                        
                        x = start_x + col * 120
                        y = start_y + row * 100
                        
                        rect = pygame.Rect(x, y, 100, 80)
                        if rect.collidepoint(mx, my):
                            cost = i * self.unit_cost
                            if self.player_budget >= cost:
                                self.selected = i

                    # 확인 버튼
                    confirm_rect = pygame.Rect(W//2 - 150, 500, 120, 60)
                    if confirm_rect.collidepoint(mx, my):
                        self.done = True
                        
                    # 취소 버튼
                    cancel_rect = pygame.Rect(W//2 + 30, 500, 120, 60)
                    if cancel_rect.collidepoint(mx, my):
                        self.selected = 0
                        self.done = True

            clock.tick(30)

        return self.selected

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("재난 대비 보드게임")
        self.clock = pygame.time.Clock()
        self.font_manager = FontManager()
        
        self.players = []
        self.board_map = {}  # 플레이어별 보드 저장
        self.turn = 0
        self.state = -2  # -2: 플레이어 수 선택, -1: 게임 종료, 0: 게임 진행
        self.dice_value = 0
        self.log = []
        self.num_players = 2
        
        # 재난 설명
        self.disaster_descriptions = {
            0: "지진 발생! 도심 지역에서 강한 진동이 감지되었습니다.",
            1: "가뭄 발생! 식수와 농업용수가 고갈되고 있습니다.",
            2: "폭우 & 홍수! 도심 전역이 침수되고 교통이 마비되었습니다.",
            3: "폭설! 도로와 철도가 눈에 파묻혔습니다.",
            4: "화재! 주택가에서 큰 화재가 발생했습니다.",
            5: "건물 붕괴! 노후 건물이 무너져 다수 피해 발생."
        }
        
        # 이벤트 메시지
        self.event_messages = {
            (0, 0): "정부의 긴급 지원으로 대규모 예산이 추가되었습니다.",
            (0, 1): "정부 보조금 정책으로 중규모 예산이 편성되었습니다.",
            (0, 2): "소규모 후원금이 도착했습니다.",
            (1, 0): "예산 집행 지연으로 대규모 삭감이 발생했습니다.",
            (1, 1): "지역 개발 갈등으로 예산 일부가 삭감되었습니다.",
            (1, 2): "관리 실수로 소규모 예산이 사라졌습니다."
        }

    def generate_tile(self):
        # x1 분포: 재난40%, 예산40%, 이벤트20%
        x1_rand = random.random()
        if x1_rand < 0.4:
            x1 = 0  # 재난
        elif x1_rand < 0.8:
            x1 = 1  # 예산
        else:
            x1 = 2  # 이벤트
        
        # x2 분포
        if x1 == 0:  # 재난
            x2_rand = random.random()
            if x2_rand < 0.4:
                x2 = 0  # 대규모
            elif x2_rand < 0.8:
                x2 = 1  # 중규모
            else:
                x2 = 2  # 소규모
        elif x1 == 1:  # 예산
            x2 = random.choice([0, 1, 2])  # 안전교육, 연구, 방재조치
        else:  # x1 == 2, 이벤트
            x2 = random.choice([0, 1])  # 예산증액, 예산감소
        
        # x3 분포
        if x1 == 0:  # 재난
            x3_rand = random.random()
            if x3_rand < 0.1:
                x3 = 0  # 지진
            elif x3_rand < 0.45:
                x3 = random.choice([1, 2, 3])  # 가뭄, 홍수, 폭설
            else:
                x3 = random.choice([4, 5])  # 화재, 붕괴
        elif x1 == 1:  # 예산
            x3 = 0  # 소분류 없음
        else:  # x1 == 2, 이벤트
            x3_rand = random.random()
            if x3_rand < 0.25:
                x3 = 0  # 대규모
            elif x3_rand < 0.55:
                x3 = 1  # 중규모
            else:
                x3 = 2  # 소규모
        
        # x4 분포: 효과없음70%, 1번더10%, 스킵5%, 2배15%
        x4_rand = random.random()
        if x4_rand < 0.7:
            x4 = 0  # 효과없음
        elif x4_rand < 0.8:
            x4 = 1  # 1번더
        elif x4_rand < 0.85:
            x4 = 2  # 출발지점스킵
        else:
            x4 = 3  # 효과2배
        
        return Tile(x1, x2, x3, x4)

    def generate_board(self):
        board = [Tile(0, 0, 0, 0)]  # 출발점
        for _ in range(15):
            board.append(self.generate_tile())
        return board

    def create_players(self):
        for i in range(self.num_players):
            stat_screen = StatAllocationScreen(self.screen, f"플레이어 {i+1}", self.font_manager)
            stats = stat_screen.run()
            
            player = Player(f"플레이어 {i+1}")
            player.safety_awareness = stats["시민안전인식"]
            player.tech_level = stats["기술수준"]
            player.readiness = stats["대비수준"]
            player.color = COLORS[i % len(COLORS)]
            
            self.players.append(player)
            self.board_map[player] = self.generate_board()

    def calculate_damage(self, scale, disaster_type, player):
        # 피해 수치 사전 (소규모 기준)
        base = {
            0: {"death": 1, "injury": 3, "property": 30000},   # 지진
            1: {"death": 0, "injury": 0, "property": 70000},   # 가뭄
            2: {"death": 2, "injury": 10, "property": 50000},  # 홍수
            3: {"death": 1, "injury": 5, "property": 20000},   # 폭설
            4: {"death": 2, "injury": 6, "property": 5000},    # 화재
            5: {"death": 3, "injury": 9, "property": 2000}     # 붕괴
        }

        info = base.get(disaster_type, {"death": 1, "injury": 1, "property": 10000})
        multiplier = {0: 100, 1: 10, 2: 1}.get(scale, 1)  # 대/중/소규모

        # 피해 원본 계산
        death = info["death"] * multiplier
        injury = info["injury"] * multiplier
        property_loss = info["property"] * multiplier

        # 스탯 기반 경감율 (각 스탯 1포인트당 3% 감소, 최대 75%)
        def reduce_damage(value, stat):
            rate = min(stat * 0.03, 0.75)
            return int(value * (1 - rate))

        death = reduce_damage(death, player.safety_awareness)
        injury = reduce_damage(injury, player.tech_level)
        property_loss = reduce_damage(property_loss, player.readiness)

        total_damage = death * 1000 + injury * 50 + property_loss
        return total_damage

    def handle_tile_effect(self, player, tile):
        x1, x2, x3, x4 = tile.x1, tile.x2, tile.x3, tile.x4
        multiplier = 2 if x4 == 3 else 1

        if x1 == 0:  # 재난
            desc = self.disaster_descriptions.get(x3, "재난 발생!")
            scale_name = ["대규모", "중규모", "소규모"][x2]
            self.log_msg(f"{scale_name} {desc}")
            
            damage = self.calculate_damage(x2, x3, player) * multiplier
            player.damage += damage
            self.log_msg(f"{player.name}: 재난 피해 {damage:,}$ 발생")

        elif x1 == 1:  # 예산 사용
            stat_names = ["시민안전인식", "기술수준", "대비수준"]
            stat_name = stat_names[x2]
            
            # 스탯 강화 UI
            ui = StatUpgradeUI(self.screen, stat_name, player.budget, self.font_manager)
            selected_points = ui.run()

            if selected_points > 0:
                total_cost = selected_points * 200
                player.budget -= total_cost

                actual_points = selected_points * multiplier
                if x2 == 0:
                    player.safety_awareness += actual_points
                elif x2 == 1:
                    player.tech_level += actual_points
                elif x2 == 2:
                    player.readiness += actual_points

                self.log_msg(f"{player.name}: {stat_name} +{actual_points} (비용: {total_cost:,}$)")
            else:
                self.log_msg(f"{player.name}: 스탯 강화를 취소했습니다.")

        elif x1 == 2:  # 이벤트
            msg = self.event_messages.get((x2, x3), "이벤트 발생!")
            self.log_msg(msg)
            
            amount = [1000, 500, 100][x3] * multiplier
            if x2 == 0:  # 예산 증가
                player.budget += amount
                self.log_msg(f"{player.name}: 예산 +{amount:,}$")
            elif x2 == 1:  # 예산 감소
                player.budget = max(0, player.budget - amount)
                self.log_msg(f"{player.name}: 예산 -{amount:,}$")

        # 특수 효과 처리
        if x4 == 1:  # 1번 더
            self.log_msg(f"{player.name}: 주사위를 한 번 더 굴립니다!")
            return True
        elif x4 == 2:  # 출발지점으로 스킵
            player.position = 0
            player.year += 1
            player.budget += 1000
            self.log_msg(f"{player.name}: 출발지점으로 이동! {player.year}년차, 예산 +1000$")
            self.randomize_board_for(player)
            if player.year > 5:
                player.finished = True
                self.log_msg(f"✅ {player.name}이 5년차를 완료했습니다!")
            
        return False

    def move_player(self, player, steps):
        old_position = player.position
        player.position += steps

        # 한 바퀴 완주 체크
        if player.position >= 16:
            player.position %= 16
            player.year += 1
            player.budget += 1000
            self.log_msg(f"🌟 {player.name}: {player.year}년차 시작, 예산 +1000$")
            self.randomize_board_for(player)

            if player.year > 5:
                player.finished = True
                self.log_msg(f"✅ {player.name}이 5년차를 완료했습니다!")
                return

        # 칸 효과 처리
        tile = self.get_tile(player.position, player)
        roll_again = self.handle_tile_effect(player, tile)
        
        return roll_again

    def randomize_board_for(self, player):
        self.board_map[player] = self.generate_board()
        self.log_msg(f"{player.name}: 보드판 재배치")

    def get_tile(self, position, player):
        return self.board_map[player][position]

    def log_msg(self, msg):
        self.log.append(msg)
        if len(self.log) > 15:  # 로그 개수 증가
            self.log.pop(0)

    def draw_board(self, player, x_offset, y_offset):
        board_size = 400  # 보드 크기 증가
        cell_size = board_size // 5
        
        # 보드 테두리
        pygame.draw.rect(self.screen, BLACK, (x_offset, y_offset, board_size, board_size), 3)
        
        # 칸 그리기
        positions = []
        # 위쪽 행 (오른쪽으로)
        for i in range(5):
            positions.append((x_offset + i * cell_size, y_offset))
        # 오른쪽 열 (아래로) - 모서리 제외
        for i in range(1, 4):
            positions.append((x_offset + 4 * cell_size, y_offset + i * cell_size))
        # 아래쪽 행 (왼쪽으로)
        for i in range(4, -1, -1):
            positions.append((x_offset + i * cell_size, y_offset + 4 * cell_size))
        # 왼쪽 열 (위로) - 모서리 제외
        for i in range(3, 0, -1):
            positions.append((x_offset, y_offset + i * cell_size))
        
        # 칸별 정보 표시
        for i, (px, py) in enumerate(positions):
            rect = pygame.Rect(px, py, cell_size, cell_size)
            
            if i == 0:  # 출발점
                pygame.draw.rect(self.screen, GREEN, rect)
                text_surface = self.font_manager.get_font('tiny').render("START", True, WHITE)
            else:
                tile = self.get_tile(i, player)
                
                # 칸 색상 결정
                if tile.x1 == 0:  # 재난
                    color = RED
                elif tile.x1 == 1:  # 예산
                    color = BLUE
                else:  # 이벤트
                    color = (241, 196, 15)  # 노란색
                
                pygame.draw.rect(self.screen, color, rect)
                
                # 특수 효과 표시
                if tile.x4 == 1:
                    text_surface = self.font_manager.get_font('tiny').render("⚡", True, WHITE)
                elif tile.x4 == 2:
                    text_surface = self.font_manager.get_font('tiny').render("🏠", True, WHITE)
                elif tile.x4 == 3:
                    text_surface = self.font_manager.get_font('tiny').render("×2", True, WHITE)
                else:
                    text_surface = None
            
            pygame.draw.rect(self.screen, BLACK, rect, 2)
            
            # 플레이어 위치 표시
            if i == player.position:
                pygame.draw.circle(self.screen, player.color, 
                                 (px + cell_size//2, py + cell_size//2), 20)
                pygame.draw.circle(self.screen, WHITE, 
                                 (px + cell_size//2, py + cell_size//2), 20, 3)
            
            # 텍스트 표시 (플레이어가 있는 칸이 아닐 때만)
            if text_surface and i != player.position:
                text_rect = text_surface.get_rect(center=(px + cell_size//2, py + cell_size//2))
                self.screen.blit(text_surface, text_rect)

    def draw(self):
        self.screen.fill(WHITE)
        
        if self.state == -2:  # 플레이어 수 선택
            title_font = self.font_manager.get_font('large')
            title = title_font.render("플레이어 수를 선택하세요 (2-4명)", True, BLACK)
            title_rect = title.get_rect(center=(W//2, H//2 - 100))
            self.screen.blit(title, title_rect)
            
            button_font = self.font_manager.get_font('medium')
            for i in range(2, 5):
                x = W//2 - 120 + (i-2) * 80
                y = H//2 - 25
                rect = pygame.Rect(x, y, 60, 50)
                pygame.draw.rect(self.screen, BLUE, rect)
                pygame.draw.rect(self.screen, BLACK, rect, 2)
                
                num_text = button_font.render(str(i), True, WHITE)
                num_rect = num_text.get_rect(center=rect.center)
                self.screen.blit(num_text, num_rect)
                
        elif self.state == -1:  # 게임 종료
            title_font = self.font_manager.get_font('large')
            title = title_font.render("게임 종료!", True, BLACK)
            title_rect = title.get_rect(center=(W//2, 150))
            self.screen.blit(title, title_rect)
            
            winner = min(self.players, key=lambda p: p.damage)
            winner_font = self.font_manager.get_font('medium')
            winner_text = winner_font.render(f"🏆 승자: {winner.name} (총 피해: {winner.damage:,}$)", True, GREEN)
            winner_rect = winner_text.get_rect(center=(W//2, 220))
            self.screen.blit(winner_text, winner_rect)
            
            # 순위 표시
            sorted_players = sorted(self.players, key=lambda p: p.damage)
            result_font = self.font_manager.get_font('small')
            for i, player in enumerate(sorted_players):
                y = 300 + i * 40
                rank_text = f"{i+1}위: {player.name} - 예산: {player.budget:,}$, 피해: {player.damage:,}$"
                result_surface = result_font.render(rank_text, True, BLACK)
                result_rect = result_surface.get_rect(center=(W//2, y))
                self.screen.blit(result_surface, result_rect)
                
        else:  # 게임 진행
            # 보드 레이아웃 계산 (2x2 또는 적응형)
            if self.num_players <= 2:
                cols, rows = 2, 1
                board_spacing_x = 500
                board_spacing_y = 500
            else:
                cols, rows = 2, 2
                board_spacing_x = 450
                board_spacing_y = 450
            
            board_start_x = 50
            board_start_y = 50
            
            # 플레이어별 보드 그리기
            for i, player in enumerate(self.players):
                col = i % cols
                row = i // cols
                
                x_offset = board_start_x + col * board_spacing_x
                y_offset = board_start_y + row * board_spacing_y
                
                # 플레이어 정보 (보드 위쪽)
                info_font = self.font_manager.get_font('small')
                info_text = f"{player.name} ({player.year}년차)"
                info_surface = info_font.render(info_text, True, player.color)
                self.screen.blit(info_surface, (x_offset, y_offset - 50))
                
                budget_text = f"예산: {player.budget:,}$ | 피해: {player.damage:,}$"
                budget_surface = info_font.render(budget_text, True, BLACK)
                self.screen.blit(budget_surface, (x_offset, y_offset - 30))
                
                stat_text = f"안전인식:{player.safety_awareness} 기술:{player.tech_level} 대비:{player.readiness}"
                stat_surface = self.font_manager.get_font('tiny').render(stat_text, True, DARK_GRAY)
                self.screen.blit(stat_surface, (x_offset, y_offset - 10))
                
                self.draw_board(player, x_offset, y_offset)
            
            # 게임 컨트롤 패널 (오른쪽)
            panel_x = board_start_x + cols * board_spacing_x + 50
            panel_y = 100
            
            # 현재 턴 표시
            current_player = self.players[self.turn]
            turn_font = self.font_manager.get_font('medium')
            turn_text = turn_font.render(f"현재 턴: {current_player.name}", True, current_player.color)
            self.screen.blit(turn_text, (panel_x, panel_y))
            
            # 주사위 표시
            if self.dice_value > 0:
                dice_font = self.font_manager.get_font('medium')
                dice_text = dice_font.render(f"주사위: {self.dice_value}", True, BLACK)
                self.screen.blit(dice_text, (panel_x, panel_y + 40))
            
            # 주사위 굴리기 버튼
            if not current_player.finished:
                dice_rect = pygame.Rect(panel_x, panel_y + 80, 150, 60)
                pygame.draw.rect(self.screen, BLUE, dice_rect)
                pygame.draw.rect(self.screen, BLACK, dice_rect, 2)
                
                dice_font = self.font_manager.get_font('medium')
                dice_button_text = dice_font.render("주사위 굴리기", True, WHITE)
                dice_button_rect = dice_button_text.get_rect(center=dice_rect.center)
                self.screen.blit(dice_button_text, dice_button_rect)
            
            # 로그 표시
            log_y = panel_y + 180
            log_font = self.font_manager.get_font('medium')
            log_title = log_font.render("게임 로그:", True, BLACK)
            self.screen.blit(log_title, (panel_x, log_y))
            
            # 로그 박스
            log_box_rect = pygame.Rect(panel_x, log_y + 30, 400, 600)
            pygame.draw.rect(self.screen, LIGHT_GRAY, log_box_rect)
            pygame.draw.rect(self.screen, BLACK, log_box_rect, 2)
            
            log_display_font = self.font_manager.get_font('tiny')
            for i, msg in enumerate(self.log[-20:]):  # 최근 20개 메시지
                y_pos = log_y + 40 + i * 25
                if y_pos + 20 <= log_box_rect.bottom - 10:
                    # 텍스트 길이 제한
                    if len(msg) > 45:
                        display_msg = msg[:42] + "..."
                    else:
                        display_msg = msg
                    
                    log_surface = log_display_font.render(display_msg, True, BLACK)
                    self.screen.blit(log_surface, (panel_x + 5, y_pos))

        pygame.display.flip()

    def save_game_report(self):
        try:
            with open("disaster_game_report.csv", mode="w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file)
                writer.writerow(["플레이어", "최종_예산", "총_피해", "시민안전인식", "기술수준", "대비수준", "순위"])
                
                # 피해 기준으로 정렬
                sorted_players = sorted(self.players, key=lambda p: p.damage)
                
                for rank, player in enumerate(sorted_players, 1):
                    writer.writerow([
                        player.name, player.budget, player.damage,
                        player.safety_awareness, player.tech_level, player.readiness, rank
                    ])
            self.log_msg("📄 결과가 'disaster_game_report.csv'로 저장되었습니다.")
        except Exception as e:
            self.log_msg(f"[오류] 보고서 저장 실패: {e}")

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                
                if self.state == -2:  # 플레이어 수 선택
                    for i in range(2, 5):
                        x = W//2 - 120 + (i-2) * 80
                        y = H//2 - 25
                        rect = pygame.Rect(x, y, 60, 50)
                        if rect.collidepoint(mx, my):
                            self.num_players = i
                            self.create_players()
                            self.state = 0
                            self.log_msg("🎮 게임이 시작되었습니다!")
                            break
                
                elif self.state == 0:  # 게임 진행 중
                    current_player = self.players[self.turn]
                    
                    # 주사위 굴리기 버튼
                    if self.num_players <= 2:
                        panel_x = 50 + 2 * 500 + 50
                    else:
                        panel_x = 50 + 2 * 450 + 50
                    
                    dice_rect = pygame.Rect(panel_x, 180, 150, 60)
                    if dice_rect.collidepoint(mx, my) and not current_player.finished:
                        self.roll_dice()

    def roll_dice(self):
        current_player = self.players[self.turn]
        if current_player.finished:
            return
            
        self.dice_value = random.randint(1, 6)
        self.log_msg(f"🎲 {current_player.name}: 주사위 {self.dice_value}")
        
        # 플레이어 이동
        roll_again = self.move_player(current_player, self.dice_value)
        
        # 한 번 더 굴리기가 아니라면 턴 넘기기
        if not roll_again:
            self.next_turn()

    def next_turn(self):
        # 다음 플레이어로 턴 이동
        self.turn = (self.turn + 1) % len(self.players)
        
        # 모든 플레이어가 완료했는지 확인
        if all(p.finished for p in self.players):
            self.end_game()
        else:
            # 완료되지 않은 플레이어까지 턴 스킵
            while self.players[self.turn].finished:
                self.turn = (self.turn + 1) % len(self.players)
            
            self.log_msg(f"--- {self.players[self.turn].name}의 턴 ---")

    def end_game(self):
        winner = min(self.players, key=lambda p: p.damage)
        self.log_msg("=== 게임 종료! ===")
        self.log_msg(f"🏆 승자: {winner.name} (총 피해: {winner.damage:,}$)")
        
        # 순위 출력
        sorted_players = sorted(self.players, key=lambda p: p.damage)
        for rank, player in enumerate(sorted_players, 1):
            self.log_msg(f"{rank}위: {player.name} - 피해 {player.damage:,}$")
        
        self.save_game_report()
        self.state = -1

    def run(self):
        running = True
        while running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)

def main():
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"게임 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()