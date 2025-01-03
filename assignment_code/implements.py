import math
import random
import time

import config

import pygame
from pygame.locals import Rect, K_LEFT, K_RIGHT


class Basic:
    def __init__(self, color: tuple, speed: int = 0, pos: tuple = (0, 0), size: tuple = (0, 0)):
        self.color = color
        self.rect = Rect(pos[0], pos[1], size[0], size[1])
        self.center = (self.rect.centerx, self.rect.centery)
        self.speed = speed
        self.start_time = time.time()
        self.dir = 270

    def move(self):
        dx = math.cos(math.radians(self.dir)) * self.speed
        dy = -math.sin(math.radians(self.dir)) * self.speed
        self.rect.move_ip(dx, dy)
        self.center = (self.rect.centerx, self.rect.centery)


class Block(Basic):
    def __init__(self, color: tuple, pos: tuple = (0,0), alive = True):
        super().__init__(color, 0, pos, config.block_size)
        self.pos = pos
        self.alive = alive

    def draw(self, surface) -> None:
        pygame.draw.rect(surface, self.color, self.rect)
    
    def collide(self, blocks: list,items: list):
        self.alive = False
        if self in blocks:  # 블록 리스트에서 자신을 제거
            blocks.remove(self)
        if random.random() < 0.2: # 20%의 확률로 아이템 생성됨
            item_color = random.choice(config.items_color)
            items.append(Item(item_color,self.rect.center))


class Paddle(Basic):
    def __init__(self):
        super().__init__(config.paddle_color, 0, config.paddle_pos, config.paddle_size)
        self.start_pos = config.paddle_pos
        self.speed = config.paddle_speed
        self.cur_size = config.paddle_size

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

    def move_paddle(self, event: pygame.event.Event):
        if event.key == K_LEFT and self.rect.left > 0:
            self.rect.move_ip(-self.speed, 0)
        elif event.key == K_RIGHT and self.rect.right < config.display_dimension[0]:
            self.rect.move_ip(self.speed, 0)


class Ball(Basic):
    def __init__(self, pos: tuple = config.ball_pos, color: tuple = config.ball_color, is_item: bool = False):
        super().__init__(color, config.ball_speed, pos, config.ball_size)
        self.power = 1
        self.dir = 90 + random.randint(-45, 45)
        self.is_item = is_item
        self.original_size = config.ball_size
        
    def increase_size(self):
        if self.rect.width == self.original_size[0]:
            new_size = (self.rect.width * 3, self.rect.height * 3)
            center = self.rect.center
            self.rect.size = new_size
            self.rect.center = center
                   
    def draw(self, surface):
        pygame.draw.ellipse(surface, self.color, self.rect)

    def collide_block(self, blocks: list, items: list):
        if not self.is_item or self.color ==(0,0,255):
            for block in blocks:
                if self.rect.colliderect(block.rect):  # 충돌 확인
                    block.collide(blocks,items)  # 블록의 collide 메서드 호출

                    # 가로 및 세로 거리 계산
                    vertical_distance = min(
                        abs(self.rect.bottom - block.rect.top),
                        abs(self.rect.top - block.rect.bottom)
                    )
                    horizontal_distance = min(
                        abs(self.rect.right - block.rect.left),
                        abs(self.rect.left - block.rect.right)
                    )

                    # 더 가까운 면을 기준으로 충돌 방향 반전
                    if vertical_distance < horizontal_distance:
                        self.dir = -self.dir  # y축 반전 (가로면 충돌)
                    else:
                        self.dir = 180 - self.dir  # x축 반전 (세로면 충돌)

                    break  # 한 번에 하나의 블록만 처리
            


    def collide_paddle(self, paddle: Paddle) -> None:
        if self.rect.colliderect(paddle.rect):
            self.dir = 360 - self.dir + random.randint(-5, 5)

    def hit_wall(self):
        # 좌우 벽 충돌
        if self.rect.left <= 0 or self.rect.right >= config.display_dimension[0]:
            self.dir = 180 - self.dir  # x축 반전

        # 상단 벽 충돌
        if self.rect.top <= 0:
            self.dir = -self.dir  # y축 반전
    
    def alive(self):
        return self.rect.bottom <= config.display_dimension[1]


class Item(Basic):
    def __init__(self, color: tuple, pos: tuple):
        speed = config.ball_speed * 1.15
        super().__init__(color, speed , pos , config.item_size)

    def move(self):
        self.rect.move_ip(0,self.speed)

    def draw(self,surface):
        pygame.draw.ellipse(surface,self.color,self.rect)
        
