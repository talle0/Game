# 🎮 Pygame 보드게임 개발 가이드

이 가이드는 모노폴리 게임 코드를 기반으로 다양한 보드게임을 개발하는 방법을 안내합니다.

## 📋 목차
1. [기본 구조 이해](#기본-구조-이해)
2. [게임 커스터마이징](#게임-커스터마이징)
3. [새로운 게임 만들기](#새로운-게임-만들기)
4. [고급 기능 추가](#고급-기능-추가)
5. [게임 아이디어](#게임-아이디어)

---

## 🏗️ 기본 구조 이해

### 핵심 클래스
```python
class Player:
    # 플레이어 정보: 이름, 색상, 위치, 이동 상태
    
class Game:
    # 게임 로직: 상태 관리, 업데이트, 렌더링
```

### 게임 상태 (self.state)
- `0`: 주사위 대기
- `1`: 주사위 굴리기  
- `2`: 플레이어 이동
- `3`: 턴 완료

### 주요 메서드
- `update()`: 게임 로직 업데이트
- `draw()`: 화면 렌더링
- `handle_click()`: 사용자 입력 처리

---

## 🎨 게임 커스터마이징

### 1. 게임판 크기 변경
```python
# 18칸 → 12칸으로 변경
def __init__(self):
    # 게임판 생성 부분 수정
    self.board = []
    # 하단 4칸
    for i in range(4): self.board.append((l + i * w//3, t + h))
    # 오른쪽 2칸  
    for i in range(1, 3): self.board.append((l + w, t + h - i * h//2))
    # 상단 4칸
    for i in range(4): self.board.append((l + w - i * w//3, t))
    # 왼쪽 2칸
    for i in range(1, 3): self.board.append((l, t + i * h//2))
```

### 2. 플레이어 수 변경
```python
# 4명 → 6명으로 변경
COLORS = [(231,76,60), (52,152,219), (46,204,113), (241,196,15), (155,89,182), (230,126,34)]
self.players = [Player(i) for i in range(6)]  # 6명 생성
```

### 3. 색상 테마 변경
```python
# 다크 테마
WHITE, BLACK = (40,40,40), (240,240,240)
LIGHT_GRAY, DARK_GRAY = (60,60,60), (200,200,200)
```

### 4. 주사위 범위 변경
```python
# 1-6 → 1-4로 변경
self.dice = random.randint(1, 4)
```

---

## 🎲 새로운 게임 만들기

### 예시 1: 뱀과 사다리 게임
```python
class SnakesAndLadders(Game):
    def __init__(self):
        super().__init__()
        # 뱀과 사다리 위치 정의
        self.snakes = {14: 7, 11: 2, 16: 4}     # 뱀 (큰수→작은수)
        self.ladders = {3: 12, 8: 15, 5: 13}   # 사다리 (작은수→큰수)
    
    def move_next(self):
        super().move_next()  # 기본 이동
        p = self.players[self.turn]
        
        # 뱀 체크
        if p.pos in self.snakes:
            new_pos = self.snakes[p.pos]
            p.pos = new_pos
            p.tx, p.ty = self.board[new_pos]
            self.log_msg(f"{p.name} hit a snake! Down to {new_pos+1}")
        
        # 사다리 체크
        elif p.pos in self.ladders:
            new_pos = self.ladders[p.pos]
            p.pos = new_pos
            p.tx, p.ty = self.board[new_pos]
            self.log_msg(f"{p.name} climbed a ladder! Up to {new_pos+1}")
```

### 예시 2: 말 잡기 게임
```python
class CatchGame(Game):
    def move_next(self):
        super().move_next()
        p = self.players[self.turn]
        
        # 같은 위치에 다른 플레이어가 있는지 확인
        for other in self.players:
            if other != p and other.pos == p.pos:
                other.pos = 0  # 시작점으로 돌아가기
                other.x, other.y = self.board[0]
                self.log_msg(f"{p.name} caught {other.name}!")
```

### 예시 3: 골 게임
```python
class GoalGame(Game):
    def __init__(self):
        super().__init__()
        self.goal = 17  # 골 지점
        self.winner = None
    
    def move_next(self):
        super().move_next()
        p = self.players[self.turn]
        
        # 골 도달 체크
        if p.pos >= self.goal:
            self.winner = p
            self.log_msg(f"🎉 {p.name} WINS!")
            self.state = 4  # 게임 종료 상태
```

---

## 🔧 고급 기능 추가

### 1. 카드 시스템
```python
class CardGame(Game):
    def __init__(self):
        super().__init__()
        self.cards = ["Move +2", "Move -1", "Skip Turn", "Roll Again"]
        self.player_cards = [[] for _ in range(4)]
    
    def draw_card(self, player_idx):
        if self.cards:
            card = random.choice(self.cards)
            self.player_cards[player_idx].append(card)
            self.log_msg(f"{self.players[player_idx].name} drew: {card}")
```

### 2. 특수 칸 시스템
```python
class SpecialSpaces(Game):
    def __init__(self):
        super().__init__()
        self.special_spaces = {
            5: "boost",    # 부스트 칸
            10: "penalty", # 페널티 칸
            15: "bonus"    # 보너스 칸
        }
    
    def handle_special_space(self, pos):
        if pos in self.special_spaces:
            effect = self.special_spaces[pos]
            p = self.players[self.turn]
            
            if effect == "boost":
                # 추가 이동
                p.steps += 2
                self.log_msg(f"{p.name} got a boost!")
            elif effect == "penalty":
                # 한 턴 쉬기
                self.log_msg(f"{p.name} penalty! Skip next turn")
```

### 3. 점수 시스템
```python
class ScoreGame(Game):
    def __init__(self):
        super().__init__()
        self.scores = [0, 0, 0, 0]
        self.score_spaces = {3: 10, 7: 20, 12: 30}
    
    def update_score(self, player_idx, pos):
        if pos in self.score_spaces:
            points = self.score_spaces[pos]
            self.scores[player_idx] += points
            self.log_msg(f"{self.players[player_idx].name} +{points} points!")
```

---

## 💡 게임 아이디어

### 🎯 간단한 게임들
1. **레이싱 게임**: 먼저 골인하는 게임
2. **수집 게임**: 특정 칸을 지나며 아이템 수집
3. **퀴즈 게임**: 특정 칸에서 퀴즈 풀기
4. **미로 게임**: 복잡한 경로의 미로 탈출

### 🎨 중급 게임들
1. **RPG 보드게임**: 레벨업, 스킬, 전투 시스템
2. **전략 게임**: 자원 관리, 건설 요소
3. **협력 게임**: 플레이어들이 함께 목표 달성
4. **카드 게임**: 카드 조합으로 특수 능력 발동

### 🚀 고급 게임들
1. **실시간 게임**: 시간 제한 요소 추가
2. **AI 상대**: 컴퓨터 플레이어 추가
3. **멀티 보드**: 여러 게임판 연결
4. **온라인 게임**: 네트워크 멀티플레이

---

## 🛠️ 개발 팁

### 1. 단계별 개발
```python
# 1단계: 기본 게임 복사
# 2단계: 게임 규칙 수정
# 3단계: 새로운 기능 추가
# 4단계: UI/UX 개선
# 5단계: 밸런스 조정
```

### 2. 디버깅 팁
```python
# 상태 출력 함수 추가
def debug_state(self):
    print(f"Turn: {self.turn}, State: {self.state}")
    print(f"Players: {[(p.name, p.pos) for p in self.players]}")
```

### 3. 설정 파일 활용
```python
# config.py
BOARD_SIZE = 18
PLAYER_COUNT = 4
COLORS = [(231,76,60), (52,152,219), (46,204,113), (241,196,15)]
SPECIAL_RULES = True
```

---

## 🎊 시작하기

1. **기본 코드 복사**: 모노폴리 게임 코드를 새 파일로 복사
2. **게임 이름 변경**: 클래스명과 제목 수정
3. **규칙 수정**: `move_next()` 함수에 새로운 규칙 추가
4. **테스트**: 게임 플레이하며 밸런스 확인
5. **개선**: 사용자 피드백 반영

### 예시 시작 코드
```python
# my_game.py
import pygame
# ... (기본 import)

class MyGame(Game):  # Game 클래스 상속
    def __init__(self):
        super().__init__()
        # 여기에 새로운 게임 요소 추가
        self.my_special_rule = True
    
    def move_next(self):
        super().move_next()  # 기본 이동
        # 여기에 새로운 규칙 추가
        if self.my_special_rule:
            # 특수 규칙 구현
            pass

if __name__ == "__main__":
    MyGame().run()
```

---

## 🤝 커뮤니티

새로운 게임을 만들었다면:
- 코드 공유하기
- 피드백 받기  
- 다른 개발자와 협업하기
- 게임 대회 개최하기

**즐거운 게임 개발 되세요! 🎮✨**
