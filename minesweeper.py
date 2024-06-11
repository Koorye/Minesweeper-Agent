import numpy as np
import random
import re


_OPERATION_PATTERN = re.compile(r'[rf],\s*\d+,\s*\d+')

_EMPTY_LABEL = 0
_MINE_LABEL = 1
_REVEALED_LABEL = 2
_FLAG_LABEL = 3


class MineSweeper(object):
    def __init__(self, width, height, num_mines, index=False):
        self.width = width
        self.height = height
        self.num_mines = num_mines
        self.index = index
        self.reset()
        self.operation_time = 0
    
    def reset(self):
        self.map = np.zeros((self.height, self.width), dtype=int)
        self.map.fill(_EMPTY_LABEL)

        indexs = random.sample(range(self.width * self.height), self.num_mines)
        for index in indexs:
            y = index // self.width
            x = index % self.width
            self.map[y, x] = _MINE_LABEL
        
        self.mines_around_map = np.zeros((self.height, self.width), dtype=int)
        for y in range(self.height):
            for x in range(self.width):
                if self.map[y, x] == _MINE_LABEL:
                    continue
                count = 0
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dy == 0 and dx == 0:
                            continue
                        ny = y + dy
                        nx = x + dx
                        if ny < 0 or ny >= self.height or nx < 0 or nx >= self.width:
                            continue
                        if self.map[ny, nx] == _MINE_LABEL:
                            count += 1
                self.mines_around_map[y, x] = count
        
        self.revealed_map = np.zeros((self.height, self.width), dtype=int)
    
    def operation(self, answer):
        self.operation_time += 1
        
        try:
            op = re.findall(_OPERATION_PATTERN, answer)[-1]
            op = op.replace(' ', '')
            action, r, c = op.split(',')
            y, x = int(r), int(c)
        except:
            return 'invalid answer, answer should be in the form of triples (action,x,y).'
        
        if not self.check_position(x, y):
            return 'invalid position, out of range.'

        if action == 'r':
            result = self.reveal(x, y)
        elif action == 'f':
            result = self.flag(x, y)
        else:
            result = 'invalid action, action should be r or f.'
        
        # print(self.show())

        if result == 'game over':
            self.reset()
            return 'game over'
        
        if self.check_win():
            self.reset()
            return 'win'
        
        return result
    
    def reveal(self, x, y):
        if self.revealed_map[y, x] == _REVEALED_LABEL:
            return 'invalid operation, the area is already revealed.'

        self.revealed_map[y, x] = _REVEALED_LABEL

        if self.map[y, x] == _MINE_LABEL:
            return 'game over'
        if self.mines_around_map[y, x] > 0:
            return 'safe'

        if self.mines_around_map[y, x] == 0:
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    ny = y + dy
                    nx = x + dx
                    if ny < 0 or ny >= self.height or nx < 0 or nx >= self.width:
                        continue
                    self.reveal(nx, ny)
            return 'safe'
    
    def flag(self, x, y):
        if self.revealed_map[y, x] == _REVEALED_LABEL:
            return 'invalid operation, the area is already revealed.'
        
        if self.revealed_map[y, x] == _FLAG_LABEL:
            self.revealed_map[y, x] = _EMPTY_LABEL
            return 'remove flag'
        else:
            if np.sum(self.revealed_map == _FLAG_LABEL) >= self.num_mines:
                return 'invalid operation, the number of flags exceeds the number of mines.'
            
            self.revealed_map[y, x] = _FLAG_LABEL
            return 'add flag'
    
    def check_position(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        return True

    def check_win(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.map[y, x] == _MINE_LABEL:
                    if self.revealed_map[y, x] != _FLAG_LABEL:
                        return False
        return True
    
    def show(self):
        string = ''
        
        if self.index:
            string += '    '
            for x in range(self.width):
                string += str(x) + ' '
            string += '\n  + '
            for _ in range(self.width):
                string += '- '
            string += '\n'
        
        for y in range(self.height):
            if self.index:
                string += str(y) + ' | '
            
            for x in range(self.width):
                if self.revealed_map[y, x] == _REVEALED_LABEL:
                    if self.map[y, x] == _MINE_LABEL:
                        string += 'X '
                    else:
                        string += str(self.mines_around_map[y, x]) + ' '
                elif self.revealed_map[y, x] == _FLAG_LABEL:
                    string += 'F '
                else:
                    string += '? '
            string += '\n'
        
        mines_rest = self.num_mines - np.sum(self.revealed_map == _FLAG_LABEL)
        string += f'Mines rest: {mines_rest}'

        # give covered areas
        string += '\n'
        string += 'Revealed areas: '
        for y in range(self.height):
            for x in range(self.width):
                if self.revealed_map[y, x] == _REVEALED_LABEL:
                    num = self.mines_around_map[y, x]
                    string += f'({y},{x}): {num}, '

        # give uncovered areas
        string += '\n'
        string += 'Unrevealed areas: '
        for y in range(self.height):
            for x in range(self.width):
                if self.revealed_map[y, x] != _REVEALED_LABEL:
                    string += f'({y},{x}), '
        
        # give flagged areas
        string += '\n'
        string += 'Flagged areas: '
        for y in range(self.height):
            for x in range(self.width):
                if self.revealed_map[y, x] == _FLAG_LABEL:
                    string += f'({y},{x}), '
        
        return string
            
            
if __name__ == '__main__':
    # game = MineSweeper(10, 10, 10)
    game = MineSweeper(5, 5, 2)
    print(game.show())
    
    while True:
        # input as action, x, y
        print('Action: r - reveal, f - flag')
        op = input('Operation (action, r, c): ')
        result = game.operation(op)
        print(result)
        if result in ['game over', 'win']:
            break
