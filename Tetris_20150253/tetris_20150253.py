# -*- coding:utf-8 -*-

#회전과 블럭 부수는 기능 구현.

from random import randint
import sys
import pygame
import pygame.sprite

class Cell(pygame.sprite.Sprite):
    cell_size = 40
    def __init__(self, image_file, x, y, w=40, h=40):
        super().__init__()
               
        image = pygame.image.load(image_file)
        self.image = pygame.transform.scale(image, (w, h))
        self.rect = self.image.get_rect().move(x, y)
                                                
class Shape:
    piece_shapes = [[[1, 1, 1], [0 ,1, 0]],
                    [[0, 2, 2], [2, 2, 0]],
                    [[3, 3, 0], [0, 3, 3]],
                    [[4, 0, 0], [4, 4, 4]],
                    [[0, 0, 5], [5, 5, 5]],
                    [[6, 6, 6, 6]],
                    [[7, 7], [7, 7]]]
    
    cell_images = ('1.png', '2.png', '3.png', '4.png', '5.png', '6.png', '7.png')
    
    def __init__(self):
        self.generate_shape()
        
    def generate_shape(self):
        idx = randint(0, 6)
        
        self.shape = Shape.piece_shapes[idx]
        self.pos = [4, 0]
    
        image_file = 'images/' + Shape.cell_images[idx]
        self.cells = [Cell(image_file,
                           Cell.cell_size*(y+self.pos[0])+Board.margin,
                           Cell.cell_size*(x+self.pos[1])+Board.margin)
                        for x in range(len(self.shape))
                        for y in range(len(self.shape[0])) if self.shape[x][y] != 0]

    def rotate(self, board):
        tmp_cells = [cell.rect.copy() for cell in self.cells]

        rotate_flag =True
        
        tmp_shape = [[self.shape[x][y] for x in range(len(self.shape)-1, -1, -1)]
                                        for y in range(len(self.shape[0]))]
        for x in range(len(tmp_shape[0])):
            if tmp_shape[-1][x] != 0:
                distance = x
        
        x, y = (self.cells[-1].rect.x-(Cell.cell_size*distance), self.cells[-1].rect.y-(Cell.cell_size*distance))

        pos = [[(x+j*Cell.cell_size, y+i*Cell.cell_size) for j in range(len(tmp_shape[0]))]
                                                             for i in range(len(tmp_shape))]
  
        tmp_list = [pos[x][y] for x in range(len(tmp_shape))
                        for y in range(len(tmp_shape[0])) if tmp_shape[x][y] != 0]
        
        
        for i in range(len(tmp_list)) :
            tmp_cells[i].x, tmp_cells[i].y = tmp_list[i]
        
        for cell in tmp_cells:
            if cell.collidelist(board.cells) >= 0 or not board.rect.contains(cell):
                rotate_flag = False
                break
                
        if rotate_flag:
            self.shape = [[self.shape[x][y] for x in range(len(self.shape)-1, -1, -1)]
                                    for y in range(len(self.shape[0]))]
            for i in range(len(tmp_list)) :
                self.cells[i].rect.x, self.cells[i].rect.y = tmp_list[i]
            
            

    def move(self, dx, board):
        dx = dx*Cell.cell_size
        move_flag = True
        tmp_cells = [cell.rect.copy() for cell in self.cells]
        
        for cell in tmp_cells:
            cell.move_ip((dx, 0))
            if cell.collidelist(board.cells) >= 0 or not board.rect.contains(cell):
                move_flag = False
                break
            
        if move_flag :
            for cell in self.cells:
                cell.rect.move_ip((dx, 0))
            self.pos[0] += dx
            
    def drop(self, board):
        dy = 5
        drop_flag = True
        
        tmp_cells = [cell.rect.copy() for cell in self.cells]
        
        for cell in tmp_cells:
            cell.move_ip((0, dy))
            if cell.collidelist(board.cells) >= 0 or not board.rect.contains(cell):
                drop_flag = False
                break
        
        if drop_flag:
            for cell in self.cells:
                cell.rect.move_ip((0, dy))
            self.pos[1] += dy
            
        return drop_flag
        
    def quick_drop(self, board):
        while self.drop(board) :
            pass
    
    
class Board(Cell):
    n_rows, n_cols = (18,10)
    margin = Cell.cell_size//2
    
    def __init__(self, image_file, x, y, w, h):
        super().__init__(image_file, x, y, w, h)
        
        self.grid = [[0 for _ in range(Board.n_cols)]
                        for _ in range(Board.n_rows)]
        self.cells = []
        
    def clear_line(self):
        
        clear_line_level = 0
        clear_flag = False
        
        for i, row in enumerate(self.grid[:]):
            tmp_cells = []
            if 0 not in row:
                self.grid.remove(self.grid[i])
                self.grid.insert(0, [0 for _ in range(Board.n_cols)])
                
                clear_line_level = i
                for cell in self.cells:
                    if cell.rect.y == Cell.cell_size*i+20 :
                        tmp_cells.append(cell)  #삭제할 cell 골라내기
                clear_flag = True
                
            if clear_flag:
                for tmp_cell in tmp_cells:      #삭제 작업
                    self.cells.remove(tmp_cell)
                    tmp_cell.kill()
                    
                for tmp_cell in self.cells:
                    if tmp_cell.rect.y < Cell.cell_size*clear_line_level+20 :
                        tmp_cell.rect.y += Cell.cell_size
                clear_flag = False
                
            
            
                
    
class TetApp:
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(200, 1000)
        screen_wh = (Cell.cell_size*(Board.n_cols+1), Cell.cell_size*(Board.n_rows+2))
        self.screen = pygame.display.set_mode(screen_wh)
        
        self.initialize_game()
        
    def initialize_game(self):
        self.score = 0
        self.gameover = False
        self.paused = False
            
        pygame.time.set_timer(pygame.USEREVENT+1, 1000)
            
    def start_game(self):
        if self.gameover:
            self.initialize_game()
            self.gameover = False
        
    def play(self):
        board = Board('images/background.png', Board.margin, Board.margin,
                      Cell.cell_size*Board.n_cols, Cell.cell_size*Board.n_rows)
        shape = Shape()
            
        all_group = pygame.sprite.Group(board)
        all_group.add(shape.cells)
        all_group.draw(self.screen)
        
        clock = pygame.time.Clock()
        
        drop_flag = True
        while not self.gameover and not self.paused:
            clock.tick(10)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if drop_flag :
                    drop_flag = shape.drop(board)     
                else:
                    for cell in shape.cells :
                        board.cells.append(cell)
                        board.grid[cell.rect.y//40][cell.rect.x//40] = 1        #grid값 수정
                        
                    board.clear_line()
                    shape.generate_shape()
                    all_group.add(shape.cells)
                    drop_flag = True
                    
                key = pygame.key.get_pressed()
                if key[pygame.K_RIGHT]:
                    shape.move(1, board)
                elif key[pygame.K_LEFT]:
                    shape.move(-1, board)
                elif key[pygame.K_UP]:
                    shape.quick_drop(board)
                elif key[pygame.K_SPACE]:
                    shape.rotate(board)
                    
                all_group.update()
                all_group.draw(self.screen)
                
                pygame.display.update()
                pygame.display.flip()
    
    
def main():
    tetris = TetApp()
    tetris.play()
    
main()