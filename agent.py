import os
import pandas as pd
import time
from minesweeper import MineSweeper as Environment
from logger import reset_logger, set_logger
from api import *


_MINESWEEPER_PROMPT_BEFORE = '''
In Minesweeper , hidden mines are scattered throughout a board, which is divided into areas. 
The rows are seperated by newlines, and columns by space. 
The board is structured as a table, with the first row and column labeled using numbers in double quotation marks to indicate row and column indices. 
Areas have multiple possible states: 
- Unrevealed areas (represented by `?', which cover the board at the start of the game, can also be made by removing flags)
- Numbered areas (represented by `0' to `8', which indicate the number of mines in the eight neighboring cells, including those diagonally adjacent)
- Flagged areas (represented by `F', which are marked by the player to indicate a potential mine location)

A player selects a cell to open it. If a player opens a cell containing a mine, the game ends in a loss. 
Otherwise, the opened cell displays either a number, indicating the number of mines diagonally and/or adjacent to it, 
or a blank tile, and all adjacent cells will automatically be opened. 
To win a game of Minesweeper, all non-mine cells must be opened without opening a mine.

Here are some tips and tricks for playing Minesweeper:
- Start at the corners: Begin by clicking on one of the four corner cells. There's a 1/3 chance of not hitting a mine, and it helps open up more of the board.
- Use the numbers: Each number tells you how many mines are adjacent (including diagonally) to that cell. Use this information to logically deduce where mines are or aren't.
- The 1-2-3 Rule: When you see a sequence like 1-2-3, the '3' must be surrounded by all three mines. This can help you clear the surrounding cells safely.
- Chord Method: If two adjacent cells with numbers have only one common adjacent unrevealed cell between them, that cell must be a mine. This is because the numbers account for all the mines around them, and the overlap indicates a mine.
- Flagging: As soon as you identify a mine, flag it immediately. This helps keep track and avoids accidental clicks.
- Safely open empty areas: When you find an area surrounded by numbered cells that account for all adjacent mines, you can safely open all cells around it without clicking. This is called "chaining" or "bracketing".
- Patterns: Learn common patterns like "2-1-1", where a '2' is next to a '1', indicating the third cell in line must be a mine, as the '2' accounts for the '1' and the mine.
- Practice and Patience: Minesweeper is a game of logic and patience. The more you play, the better you'll get at recognizing patterns and making quick decisions.
- Take calculated risks: Sometimes, especially in advanced levels, you might need to make an educated guess. Weigh the probabilities before clicking, and remember, every game is learnable from mistakes.

Below is a Minesweeper board:
'''


_MINESWEEPER_PROMPT_AFTER = '''
Let's step back and think, then give your answer. 
Please explain your reason first, and then answer (action,row,col) in the form of triples.
- "action" can be "r" (reveal) or "f" (flag or unflag),
- "row" and "col" are the row and column indices of the area, the upper left corner is (0,0).

For example, "r,1,2" means to reveal the area at row 1 and column 2, 
and "f,3,4" means to flag the area at row 3 and column 4, if the area is flagged, it will be unflagged.
Now, please enter the action, choose an unrevealed area to reveal or flag.
Only one action is allowed at a time. The answer must be in the form of triples, separated by commas, and do not add spaces.
'''


class Agent(object):
    def __init__(self, llm, env, end_prompts=['win', 'game over'], verbose=True):
        self.llm = llm
        self.env = env
        self.end_prompts = end_prompts
        self.verbose = verbose
        self.contexts = []
        self._step = 0
        self._invalid_step = 0
        self._invalid_step_continue = 0
    
    def run(self, prompt_before, prompt_after):
        while True:
            self._step += 1
            result = self.step(prompt_before, prompt_after)
            if 'invalid' in result:
                self._invalid_step += 1
                self._invalid_step_continue += 1
            else:
                self._invalid_step_continue = 0

            if self._step >= 20:
                return 'game over'
            if self._invalid_step_continue >= 5:
                return 'game over'

            if result in self.end_prompts:
                return result
            
            time.sleep(5)
            
    def step(self, prompt_before, prompt_after):
        env_info = self.env.show()
        prompt = prompt_before + '\n' + env_info + '\n' + prompt_after
        if self.verbose:
            print('\nPrompt:', prompt)

        answer = self.llm.chat(self.get_prev_context() + prompt)
        if self.verbose:
            print('\nAnswer:', answer)
        
        # find a,x,y in answer, the answer is a long string

        result = self.env.operation(answer)
        if self.verbose:
            print('\nResult:', result)

        self.add_context(prompt, answer, result)
        return result
    
    def get_step(self):
        return self._step
    
    def get_invalid_step(self):
        return self._invalid_step
    
    def add_context(self, prompt, answer, result):
        s = 'Prompt:\n' + prompt + '\nAnswer:\n' + answer + '\n\n' + 'Result:\n' + result
        self.contexts.append(s)
    
    def get_prev_context(self):
        return self.contexts[-1] if self.contexts else ''


if __name__ == '__main__':
    model_name = 'memory'
    llm = CustomLLM(model_name, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcxNzY5NTE4MywianRpIjoiZTFlNGU3Y2EtZjBkNi00MGRkLWI2NDctMzIxODQxODI5ZjBjIiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiI4Y2I2YWNiOWQ1OWQ0YWQ2OTE0Mzk0YTg4OTYyZDRmMCIsIm5iZiI6MTcxNzY5NTE4MywiZXhwIjoxNzMzMjQ3MTgzLCJ1aWQiOiI2NjYxZjJjZTE3N2Y0Yjg1Y2I2MmM0YmIiLCJ1cGxhdGZvcm0iOiJwYyIsInJvbGVzIjpbInVuYXV0aGVkX3VzZXIiXX0.QHRaNnoERGByCrgeabllRDCYZxxvsdwUxgYa0OlL5vs')

    save_path = f'{model_name}.csv'
    df = None
    
    if os.path.exists(save_path):
        df = pd.read_csv(save_path)

    sizes = [9]
    all_num_mines = [1, 2, 3]
    num_tries = 10
    
    sizes_out, num_mines_out, num_wins_out, num_steps_out, num_invalid_steps_out = [], [], [], [], []
    break_flag = False
    
    for size in sizes:
        for num_mines in all_num_mines:
            reset_logger()
            filename = f'logs/{model_name}_{size}_{num_mines}.log'
            if os.path.exists(filename):
                continue
            
            set_logger(filename)
            
            if df is not None and ((df['size'] == size) & (df['num_mines'] == num_mines)).any():
                num_wins = df[(df['size'] == size) & (df['num_mines'] == num_mines)]['num_wins'].values[0]
                num_steps = df[(df['size'] == size) & (df['num_mines'] == num_mines)]['num_steps'].values[0]

            else:
                print(f'Running for size={size}, num_mines={num_mines}...')
                num_wins = 0
                num_steps, num_invalid_steps = [], []

                for i in range(num_tries):
                    env = Environment(size, size, num_mines, index=True)
                    agent = Agent(llm, env, verbose=True)
                    result = agent.run(_MINESWEEPER_PROMPT_BEFORE, _MINESWEEPER_PROMPT_AFTER)
                    if result == 'win':
                        num_wins += 1
                    step = agent.get_step()
                    invalid_step = agent.get_invalid_step()
                    num_steps.append(step)
                    num_invalid_steps.append(invalid_step)
                    print(f'[{i + 1} / {num_tries}] {result} with {step} steps, {invalid_step} invalid steps.')
                
                num_wins = num_wins / num_tries
                num_steps = sum(num_steps) / num_tries
                num_invalid_steps = sum(num_invalid_steps) / num_tries
                print(f'win ratio: {num_wins}, average steps: {num_steps}, average invalid steps: {num_invalid_steps}.')
                
            sizes_out.append(size)
            num_mines_out.append(num_mines)
            num_wins_out.append(num_wins)
            num_steps_out.append(num_steps)
            num_invalid_steps_out.append(num_invalid_steps)
