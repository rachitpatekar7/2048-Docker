from flask import Flask, request, render_template
from markupsafe import escape
from random import random, choice
from copy import deepcopy

app = Flask(__name__)

def grid_string_to_grid(grid_string):
    grid = []
    rows = grid_string.split('x')
    for row in rows:
        cols = row.split('-')
        grid.append([int(c) for c in cols])
    return grid

def grid_to_grid_string(grid):
    row_strings = []
    for row in grid:
        row_strings.append('-'.join([str(x) for x in row]))
    return 'x'.join(row_strings)

def add_next_number(grid):
    assigned = False
    while not assigned:
        row = choice([0, 1, 2, 3])
        col = choice([0, 1, 2, 3])
        if grid[row][col] == 0:
            assigned = True
            grid[row][col] = choice([2, 4])
    return grid

def render_grid(g, score, game_over=False, suggested_move=None, autoplay=False):
    gg = [["" if r == 0 else r for r in row] for row in g]
    return render_template(
        'gui.html',
        r1c1=gg[0][0], r1c2=gg[0][1], r1c3=gg[0][2], r1c4=gg[0][3],
        r2c1=gg[1][0], r2c2=gg[1][1], r2c3=gg[1][2], r2c4=gg[1][3],
        r3c1=gg[2][0], r3c2=gg[2][1], r3c3=gg[2][2], r3c4=gg[2][3],
        r4c1=gg[3][0], r4c2=gg[3][1], r4c3=gg[3][2], r4c4=gg[3][3],
        grid_encoding=grid_to_grid_string(g), score=score, game_over=game_over,
        suggested_move=suggested_move, autoplay=autoplay
    )

def move_grid(g, direction, current_score):
    score = current_score
    grid_copy = [[0 for _ in range(4)] for _ in range(4)]

    if direction == 'up':
        for col in range(4):
            syms, new_syms = [], []
            for row in range(4):
                if g[row][col] != 0:
                    syms.append(g[row][col])
            skipnext = False
            for i in range(len(syms)):
                if skipnext:
                    skipnext = False
                    continue
                if i < len(syms)-1 and syms[i] == syms[i+1]:
                    new_syms.append(syms[i]*2)
                    score += syms[i]*2
                    skipnext = True
                else:
                    new_syms.append(syms[i])
            for row in range(len(new_syms)):
                grid_copy[row][col] = new_syms[row]

    if direction == 'down':
        for col in range(4):
            syms, new_syms = [], []
            for row in reversed(range(4)):
                if g[row][col] != 0:
                    syms.append(g[row][col])
            skipnext = False
            for i in range(len(syms)):
                if skipnext:
                    skipnext = False
                    continue
                if i < len(syms)-1 and syms[i] == syms[i+1]:
                    new_syms.append(syms[i]*2)
                    score += syms[i]*2
                    skipnext = True
                else:
                    new_syms.append(syms[i])
            for row in range(3, 3 - len(new_syms), -1):
                grid_copy[row][col] = new_syms[3 - row]

    if direction == 'left':
        for row in range(4):
            syms, new_syms = [], []
            for col in range(4):
                if g[row][col] != 0:
                    syms.append(g[row][col])
            skipnext = False
            for i in range(len(syms)):
                if skipnext:
                    skipnext = False
                    continue
                if i < len(syms)-1 and syms[i] == syms[i+1]:
                    new_syms.append(syms[i]*2)
                    score += syms[i]*2
                    skipnext = True
                else:
                    new_syms.append(syms[i])
            for col in range(len(new_syms)):
                grid_copy[row][col] = new_syms[col]

    if direction == 'right':
        for row in range(4):
            syms, new_syms = [], []
            for col in reversed(range(4)):
                if g[row][col] != 0:
                    syms.append(g[row][col])
            skipnext = False
            for i in range(len(syms)):
                if skipnext:
                    skipnext = False
                    continue
                if i < len(syms)-1 and syms[i] == syms[i+1]:
                    new_syms.append(syms[i]*2)
                    score += syms[i]*2
                    skipnext = True
                else:
                    new_syms.append(syms[i])
            for col in range(3, 3 - len(new_syms), -1):
                grid_copy[row][col] = new_syms[3 - col]

    return grid_copy, score

def game_over(grid):
    for r in range(4):
        for c in range(4):
            if grid[r][c] == 0:
                return False
            if r < 3 and grid[r][c] == grid[r+1][c]:
                return False
            if c < 3 and grid[r][c] == grid[r][c+1]:
                return False
    return True

def count_empty(grid):
    return sum(cell == 0 for row in grid for cell in row)

def suggest_move(original, num_simulations, depth):
    directions = ['up', 'down', 'right', 'left']
    total_score = {d: 0 for d in directions}
    total_deaths = {d: 0 for d in directions}
    expected_empty = {d: 0 for d in directions}
    min_number_moves_to_kill = {d: 1000 for d in directions}

    for direction in directions:
        griddd = deepcopy(original)
        score = 0
        gridd, score = move_grid(griddd, direction, score)
        if grid_to_grid_string(gridd) != grid_to_grid_string(original):
            for _ in range(num_simulations):
                grid = deepcopy(gridd)
                grid = add_next_number(grid)
                d = 1
                deathcount = depth
                while d <= depth:
                    dir = choice(directions)
                    prev_encoding = grid_to_grid_string(grid)
                    grid, score = move_grid(grid, dir, score)
                    if grid_to_grid_string(grid) != prev_encoding:
                        grid = add_next_number(grid)
                        d += 1
                    else:
                        break
                    if game_over(grid):
                        total_deaths[direction] += 1
                        deathcount = d
                        break
                total_score[direction] += score
                min_number_moves_to_kill[direction] = min(min_number_moves_to_kill[direction], deathcount)
                expected_empty[direction] += count_empty(grid)

    for key in total_deaths:
        if total_deaths[key] == 0:
            total_deaths[key] = float('inf')
    for key in min_number_moves_to_kill:
        if min_number_moves_to_kill[key] == 1000:
            min_number_moves_to_kill[key] = 0

    return max(total_score, key=total_score.get)

@app.route('/')
def index():
    start_grid = [[0]*4 for _ in range(4)]
    start_grid = add_next_number(start_grid)
    start_grid = add_next_number(start_grid)
    return render_grid(start_grid, 0)

@app.route('/move/<string:direction>/<string:last_encoding>/<int:score>/')
def move(direction, last_encoding, score):
    grid = grid_string_to_grid(last_encoding)
    grid, score = move_grid(grid, direction, score)
    if last_encoding != grid_to_grid_string(grid):
        grid = add_next_number(grid)
    suggested_move = suggest_move(grid, 200, 9)
    if game_over(grid):
        return render_grid(grid, score, True, suggested_move)
    return render_grid(grid, score, False, suggested_move)

@app.route('/autoplay/<string:direction>/<string:last_encoding>/<int:score>/')
def automove(direction, last_encoding, score):
    grid = grid_string_to_grid(last_encoding)
    grid, score = move_grid(grid, direction, score)
    if last_encoding != grid_to_grid_string(grid):
        grid = add_next_number(grid)
    suggested_move = suggest_move(grid, 200, 9)
    if game_over(grid):
        return render_grid(grid, score, True, suggested_move)
    return render_grid(grid, score, False, suggested_move, autoplay=True)

if __name__ == "__main__":
    app.run(debug=False, port=5000, host="0.0.0.0")
