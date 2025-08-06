# 재난 대비 보드게임
# 참여자들이 전국 안전을 담당하는 직책이 되어 재난 대비를 경쟁하는 게임

import pygame
import random
import math
import sys
import csv

# ===== 설정 =====
W, H = 1920, 1080
COLORS = [(231,76,60), (52,152,219), (46,204,113), (241,196,15)]
WHITE, BLACK, GRAY, LIGHT_GRAY, DARK_GRAY = (255,255,255), (0,0,0), (149,165,166), (236,240,241), (52,73,94)
BLUE = (52, 152, 219)
RED = (231, 76, 60)
GREEN = (46, 204, 113)

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
    def __init__(self, screen, player_name):
        self.screen = screen
        self.player_name = player_name
        self.font = pygame.font.SysFont("malgungothic", 30)
        self.points = 25
        self.stats = {"시민안전인식": 0, "기술수준": 0, "대비수준": 0}
        self.done = False

    def draw(self):
        self.screen.fill((240, 240, 240))
        title = self.font.render(f"{self.player_name} 스탯을 분배하세요 (남은 포인트: {self.points})", True, BLACK)
        self.screen.blit(title, (80, 50))

        for i, (k, v) in enumerate(self.stats.items()):
            y = 150 + i * 100
            label = self.font.render(f"{k}: {v}", True, BLACK)
            self.screen.blit(label, (100, y))
            
            # + 버튼
            plus_rect = pygame.Rect(400, y, 50, 50)
            pygame.draw.rect(self.screen, BLUE, plus_rect)
            plus_text = self.font.render("+", True, WHITE)
            self.screen.blit(plus_text, (415, y + 5))
            
            # - 버튼
            minus_rect = pygame.Rect(460, y, 50, 50)
            pygame.draw.rect(self.screen, RED, minus_rect)
            minus_text = self.font.render("-", True, WHITE)
            self.screen.blit(minus_text, (475, y + 5))

        if self.points == 0:
            confirm_rect = pygame.Rect(200, 500, 200, 60)
            pygame.draw.rect(self.screen, GREEN, confirm_rect)
            confirm_text = self.font.render("확인", True, WHITE)
            self.screen.blit(confirm_text, (260, 510))

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
                    for i, k in enumerate(self.stats.keys()):
                        y = 150 + i * 100
                        # + 버튼
                        if 400 <= mx <= 450 and y <= my <= y + 50:
                            if self.points > 0:
                                self.stats[k] += 1
                                self.points -= 1
                        # - 버튼
                        if 460 <= mx <= 510 and y <= my <= y + 50:
                            if self.stats[k] > 0:
                                self.stats[k] -= 1
                                self.points += 1

                    # 확인 버튼
                    if self.points == 0 and 200 <= mx <= 400 and 500 <= my <= 560:
                        self.done = True

            clock.tick(30)
        return self.stats

class StatUpgradeUI:
    def __init__(self, screen, stat_name, player_budget):
        self.screen = screen
        self.font = pygame.font.SysFont("malgungothic", 28)
        self.stat_name = stat_name
        self.player_budget = player_budget
        self.unit_cost = 200
        self.selected = 0
        self.done = False

    def draw(self):
        self.screen.fill((250, 250, 250))
        title = self.font.render(f"{self.stat_name} 스탯을 얼마나 올릴까요?", True, BLACK)
        self.screen.blit(title, (100, 50))

        budget_text = self.font.render(f"현재 예산: {self.player_budget}$", True, BLACK)
        self.screen.blit(budget_text, (100, 100))

        for i in range(1, 11):
            x = 80 + ((i - 1) % 5) * 120
            y = 150 + ((i - 1) // 5) * 100
            cost = i * self.unit_cost
            color = BLUE if self.player_budget >= cost else GRAY
            
            rect = pygame.Rect(x, y, 100, 80)
            pygame.draw.rect(self.screen, color, rect)
            
            num_text = self.font.render(f"+{i}", True, WHITE)
            cost_text = pygame.font.SysFont("malgungothic", 20).render(f"{cost}$", True, WHITE)
            self.screen.blit(num_text, (x + 25, y + 15))
            self.screen.blit(cost_text, (x + 15, y + 45))

        # 선택된 항목 강조
        if self.selected > 0:
            i = self.selected
            x = 80 + ((i - 1) % 5) * 120
            y = 150 + ((i - 1) // 5) * 100
            pygame.draw.rect(self.screen, GREEN, pygame.Rect(x-2, y-2, 104, 84), 3)

        # 확인 및 취소 버튼
        confirm_rect = pygame.Rect(180, 400, 120, 60)
        cancel_rect = pygame.Rect(320, 400, 120, 60)
        pygame.draw.rect(self.screen, GREEN, confirm_rect)
        pygame.draw.rect(self.screen, RED, cancel_rect)
        
        confirm_text = self.font.render("확인", True, WHITE)
        cancel_text = self.font.render("취소", True, WHITE)
        self.screen.blit(confirm_text, (215, 415))
        self.screen.blit(cancel_text, (355, 415))

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
                    
                    # 숫자 버튼들
                    for i in range(1, 11):
                        x = 80 + ((i - 1) % 5) * 120
                        y = 150 + ((i - 1) // 5) * 100
                        if x <= mx <= x + 100 and y <= my <= y + 80:
                            cost = i * self.unit_cost
                            if self.player_budget >= cost:
                                self.selected = i

                    # 확인 버튼
                    if 180 <= mx <= 300 and 400 <= my <= 460:
                        self.done = True
                        
                    # 취소 버튼
                    if 320 <= mx <= 440 and 400 <= my <= 460:
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
        self.font = pygame.font.SysFont("malgungothic", 24)
        self.small_font = pygame.font.SysFont("malgungothic", 18)
        
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
            stat_screen = StatAllocationScreen(self.screen, f"플레이어 {i+1}")
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
            self.log_msg(f"{player.name}은 재난 피해 {damage}$을 입었습니다.")

        elif x1 == 1:  # 예산 사용
            stat_names = ["시민안전인식", "기술수준", "대비수준"]
            stat_name = stat_names[x2]
            
            # 스탯 강화 UI
            ui = StatUpgradeUI(self.screen, stat_name, player.budget)
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

                self.log_msg(f"{player.name}: 예산 {total_cost}$ 소모하여 {stat_name} +{actual_points}")
            else:
                self.log_msg(f"{player.name}: 스탯 강화를 취소했습니다.")

        elif x1 == 2:  # 이벤트
            msg = self.event_messages.get((x2, x3), "이벤트 발생!")
            self.log_msg(msg)
            
            amount = [1000, 500, 100][x3] * multiplier
            if x2 == 0:  # 예산 증가
                player.budget += amount
                self.log_msg(f"{player.name}: 예산 +{amount}$")
            elif x2 == 1:  # 예산 감소
                player.budget = max(0, player.budget - amount)
                self.log_msg(f"{player.name}: 예산 -{amount}$")

        # 특수 효과 처리
        if x4 == 1:  # 1번 더
            self.log_msg(f"{player.name}: 주사위를 한 번 더 굴립니다!")
            return True
        elif x4 == 2:  # 출발지점으로 스킵
            player.position = 0
            player.year += 1
            player.budget += 1000
            self.log_msg(f"{player.name}: 출발지점으로 이동! 1년 경과, 예산 +1000$")
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
            self.log_msg(f"🌟 {player.name}이 출발지점을 지나 {player.year}년차가 되었습니다! 예산 +1000$")
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
        self.log_msg(f"{player.name}의 보드판이 새롭게 재배치되었습니다.")

    def get_tile(self, position, player):
        return self.board_map[player][position]

    def log_msg(self, msg):
        self.log.append(msg)
        if len(self.log) > 10:
            self.log.pop(0)

    def draw_board(self, player, x_offset, y_offset):
        board_size = 300
        cell_size = board_size // 5
        
        # 보드 테두리
        pygame.draw.rect(self.screen, BLACK, (x_offset, y_offset, board_size, board_size), 2)
        
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
                text = self.small_font.render("START", True, WHITE)
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
                    text = self.small_font.render("⚡", True, WHITE)
                elif tile.x4 == 2:
                    text = self.small_font.render("🏠", True, WHITE)
                elif tile.x4 == 3:
                    text = self.small_font.render("×2", True, WHITE)
                else:
                    text = self.small_font.render("", True, WHITE)
            
            pygame.draw.rect(self.screen, BLACK, rect, 1)
            
            # 플레이어 위치 표시
            if i == player.position:
                pygame.draw.circle(self.screen, player.color, 
                                 (px + cell_size//2, py + cell_size//2), 15)
            
            if i == 0 or (i > 0 and text):
                text_rect = text.get_rect(center=(px + cell_size//2, py + cell_size//2))
                if i != player.position:  # 플레이어가 있는 칸이 아닐 때만 텍스트 표시
                    self.screen.blit(text, text_rect)

    def draw(self):
        self.screen.fill(WHITE)
        
        if self.state == -2:  # 플레이어 수 선택
            title = self.font.render("플레이어 수를 선택하세요 (2-4명)", True, BLACK)
            self.screen.blit(title, (400, 300))
            
            for i in range(2, 5):
                rect = pygame.Rect(450 + (i-2) * 80, 350, 60, 50)
                pygame.draw.rect(self.screen, BLUE, rect)
                num_text = self.font.render(str(i), True, WHITE)
                self.screen.blit(num_text, (470 + (i-2) * 80, 360))
                
        elif self.state == -1:  # 게임 종료
            title = self.font.render("게임 종료!", True, BLACK)
            self.screen.blit(title, (500, 200))
            
            winner = min(self.players, key=lambda p: p.damage)
            winner_text = self.font.render(f"승자: {winner.name} (피해: {winner.damage}$)", True, GREEN)
            self.screen.blit(winner_text, (400, 250))
            
            # 결과 표시
            for i, player in enumerate(self.players):
                y = 300 + i * 30
                result_text = self.small_font.render(
                    f"{player.name}: 예산 {player.budget}$, 피해 {player.damage}$", 
                    True, BLACK
                )
                self.screen.blit(result_text, (300, y))
                
        else:  # 게임 진행
            # 보드 그리기 (2x2 격자로 배치)
            for i, player in enumerate(self.players):
                x_offset = 50 + (i % 2) * 350
                y_offset = 50 + (i // 2) * 350
                
                # 플레이어 정보
                info_text = self.small_font.render(
                    f"{player.name} ({player.year}년차) 예산: {player.budget}$ 피해: {player.damage}$",
                    True, BLACK
                )
                self.screen.blit(info_text, (x_offset, y_offset - 30))
                
                stat_text = self.small_font.render(
                    f"안전인식:{player.safety_awareness} 기술:{player.tech_level} 대비:{player.readiness}",
                    True, BLACK
                )
                self.screen.blit(stat_text, (x_offset, y_offset - 10))
                
                self.draw_board(player, x_offset, y_offset)
            
            # 현재 턴 표시
            current_player = self.players[self.turn]
            turn_text = self.font.render(f"현재 턴: {current_player.name}", True, BLACK)
            self.screen.blit(turn_text, (750, 100))
            
            # 주사위 표시
            if self.dice_value > 0:
                dice_text = self.font.render(f"주사위: {self.dice_value}", True, BLACK)
                self.screen.blit(dice_text, (750, 140))
            
            # 주사위 굴리기 버튼
            if not current_player.finished:
                dice_rect = pygame.Rect(750, 180, 120, 50)
                pygame.draw.rect(self.screen, BLUE, dice_rect)
                dice_button_text = self.font.render("주사위 굴리기", True, WHITE)
                self.screen.blit(dice_button_text, (755, 195))
            
            # 로그 표시
            log_title = self.font.render("게임 로그:", True, BLACK)
            self.screen.blit(log_title, (750, 250))
            
            for i, msg in enumerate(self.log[-8:]):  # 최근 8개 메시지
                log_text = self.small_font.render(msg[:50] + "..." if len(msg) > 50 else msg, True, BLACK)
                self.screen.blit(log_text, (750, 280 + i * 25))

        pygame.display.flip()

    def save_game_report(self):
        try:
            with open("disaster_game_report.csv", mode="w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file)
                writer.writerow(["플레이어", "최종 예산", "총 피해", "시민안전인식", "기술수준", "대비수준", "순위"])
                
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
                        rect = pygame.Rect(450 + (i-2) * 80, 350, 60, 50)
                        if rect.collidepoint(mx, my):
                            self.num_players = i
                            self.create_players()
                            self.state = 0
                            self.log_msg("게임이 시작되었습니다!")
                            break
                
                elif self.state == 0:  # 게임 진행 중
                    current_player = self.players[self.turn]
                    
                    # 주사위 굴리기 버튼
                    dice_rect = pygame.Rect(750, 180, 120, 50)
                    if dice_rect.collidepoint(mx, my) and not current_player.finished:
                        self.roll_dice()

    def roll_dice(self):
        current_player = self.players[self.turn]
        if current_player.finished:
            return
            
        self.dice_value = random.randint(1, 6)
        self.log_msg(f"{current_player.name}이 주사위를 굴려 {self.dice_value}이 나왔습니다.")
        
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
        self.log_msg(f"🏆 승자: {winner.name} (총 피해: {winner.damage}$)")
        
        # 순위 출력
        sorted_players = sorted(self.players, key=lambda p: p.damage)
        for rank, player in enumerate(sorted_players, 1):
            self.log_msg(f"{rank}위: {player.name} - 피해 {player.damage}$")
        
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
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()