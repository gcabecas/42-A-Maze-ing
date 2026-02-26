from mlx import Mlx
from typing import Generator
from maze import Maze
import sys
from config_parser import MazeConfig, read_config, verify_config

class ImgData:
    """Structure for image data"""

    def __init__(self):
        self.img = None
        self.width = 0
        self.height = 0
        self.data = None
        self.sl = 0  # size line
        self.bpp = 0  # bits per pixel
        self.iformat = 0


class MazeData:
    color = 0x55FFFF00
    ppc = 0
    path_check = 0

    @staticmethod
    def set_ppc(maze_w: int, maze_h: int, img_maze: ImgData):
        #print(img_maze.width, maze_w)
        if img_maze.width < img_maze.height:
            if maze_w < maze_h:
                MazeData.ppc = img_maze.width // maze_h
            else:
                MazeData.ppc = img_maze.width // maze_w
        else:
            if maze_w < maze_h:
                MazeData.ppc = img_maze.height // maze_h
            else:
                MazeData.ppc = img_maze.height // maze_w

    @staticmethod
    def new_color() -> Generator[None, None, None]:
        while 1:
            MazeData.color = 0x5500FFFF
            yield
            MazeData.color = 0x554169E1
            yield 
            MazeData.color = 0x55FFFF00
            yield


class XVar:
    """Structure for main vars"""

    def __init__(self):
        self.mlx: Mlx = None
        self.mlx_ptr = None
        self.screen_w = 0
        self.screen_h = 0
        self.win_1 = None
        self.win_1_w = 0
        self.win_1_h = 0
        self.img_maze: ImgData = ImgData()
        self.img_menu: ImgData = ImgData()
        self.img_png: ImgData = ImgData()
        self.img_xpm: ImgData = ImgData()
        self.imgidx = 0
        self.gen_color = None
        self.maze: Maze = None
    
def gere_close_1(xvar):
    xvar.mlx.mlx_destroy_image(xvar.mlx_ptr, xvar.img_maze.img)
    xvar.mlx.mlx_destroy_window(xvar.mlx_ptr, xvar.win_1)
    xvar.mlx.mlx_loop_exit(xvar.mlx_ptr)


def gere_mouse(button, x, y, xvar, win):
    print(f"Got mouse : {button} at {x}x{y}")

    if button == 1:
        return 0

    if button == 3:  # right click
        gere_close_1(xvar)


def gere_mouse_1(button, x, y, xvar):
    gere_mouse(button, x, y, xvar, xvar.win_1)

# Event keypress
def key_press(keycode: int, xvar: XVar):
    print(keycode)
    if keycode == 49 or keycode == 38 :
        xvar.mlx.mlx_clear_window(xvar.mlx_ptr, xvar.win_1)
        new_maze = regen_maze()
        xvar.maze = new_maze
        xvar.img_maze.img = xvar.mlx.mlx_new_image(xvar.mlx_ptr, xvar.img_maze.width, xvar.img_maze.height)
        xvar.img_maze.data, xvar.img_maze.bpp, xvar.img_maze.sl, xvar.img_maze.iformat = xvar.mlx.mlx_get_data_addr(
            xvar.img_maze.img)
        print(xvar.img_maze.iformat)

        xvar.maze = new_maze
        MazeData.set_ppc(new_maze.width, new_maze.height, xvar.img_maze)
        if MazeData.path_check == 1:
            draw_path(xvar)
            MazeData.path_check = 1
        draw_all(xvar)
        test = (xvar.win_1_w - MazeData.ppc * xvar.maze.width) // 2
        xvar.mlx.mlx_put_image_to_window(
            xvar.mlx_ptr, xvar.win_1, xvar.img_maze.img, test, 50)
    elif keycode == 50:
        if xvar.gen_color is None:
            xvar.gen_color = iter(MazeData.new_color())
        next(xvar.gen_color)
        xvar.mlx.mlx_clear_window(xvar.mlx_ptr, xvar.win_1)
        draw_all(xvar)
        test = (xvar.win_1_w - MazeData.ppc * xvar.maze.width) // 2
        xvar.mlx.mlx_put_image_to_window(
            xvar.mlx_ptr, xvar.win_1, xvar.img_maze.img, test, 50)
    elif keycode == 51:
        xvar.mlx.mlx_clear_window(xvar.mlx_ptr, xvar.win_1)
        if MazeData.path_check == 0:
            draw_all(xvar)
            draw_path(xvar)
            MazeData.path_check = 1
        else:
            xvar.img_maze.img = xvar.mlx.mlx_new_image(xvar.mlx_ptr, xvar.img_maze.width, xvar.img_maze.height)
            xvar.img_maze.data, xvar.img_maze.bpp, xvar.img_maze.sl, xvar.img_maze.iformat = xvar.mlx.mlx_get_data_addr(
            xvar.img_maze.img)
            draw_all(xvar)
            MazeData.path_check = 0

        pos = (xvar.win_1_w - MazeData.ppc * xvar.maze.width) // 2
        xvar.mlx.mlx_put_image_to_window(
            xvar.mlx_ptr, xvar.win_1, xvar.img_maze.img, pos, 50)
    elif keycode == 52:
        gere_close_1(xvar)


def regen_maze() -> Maze:
    raw_cfg: dict[str, str] = read_config(sys.argv[1])
    maze_conf: MazeConfig = verify_config(raw_cfg)
    try:
        maze = Maze(
            maze_conf.WIDTH,
            maze_conf.HEIGHT,
            None,
            maze_conf.ENTRY,
            maze_conf.EXIT,
            maze_conf.OUTPUT_FILE,
            maze_conf.PERFECT)
        maze.generate()
    except ValueError as e:
        print(f"Error generating maze: {e}", file=sys.stderr)
        sys.exit(1)
    else:
        return maze


# All draw
def draw_pattern(
        start: int,
        ppc: int,
        img_maze: ImgData,
        color: int = MazeData.color):
    all_start = [j * img_maze.sl for j in range(ppc)]
    for i in all_start:
        new_start = start + i# + path * (xvar.img_maze.bpp // 8)
        for k in range(0, ppc * 4, 4):
            img_maze.data[new_start + k: new_start + k + 4] = color.to_bytes(4, 'little')


def draw_cell(
        start: int,
        value: int,
        ppc: int,
        img_maze: ImgData):
    if value & 1 << 0:
        for i in range(0, ppc * 4, 4):
            pos = int(start + i)
            img_maze.data[pos: pos + 4] = MazeData.color.to_bytes(4, 'little')
    if value & 1 << 1:
        new_start = start + (ppc * 4)
        for i in range(ppc):
            pos = new_start + (i * img_maze.sl)
            img_maze.data[pos: pos + 4] = MazeData.color.to_bytes(4, 'little')
    if value & 1 << 2:
        new_start = start + (ppc * img_maze.sl)
        for i in range(0, ppc * 4, 4):
            pos = new_start + i
            img_maze.data[pos: pos + 4] = MazeData.color.to_bytes(4, 'little')
    if value & 1 << 3:
        for i in range(ppc):
            pos = start + (i * img_maze.sl)
            img_maze.data[pos: pos + 4] = MazeData.color.to_bytes(4, 'little')


def next_step(path: str, current: tuple) -> tuple:
    if path == "E":
        return [current[0] + 1, current[1]]
    if path == "S":
        return [current[0], current[1] + 1]
    if path == "W":
        return [current[0] - 1, current[1]]
    if path == "N":
        return [current[0] , current[1] - 1]

# draw_path
def draw_path(xvar: XVar):
    current = xvar.maze.entry
    solver = xvar.maze.solver
    for i in solver[0:-1]:
        next = next_step(i, current)
        test = find_pos(next[0], next[1], xvar) + xvar.img_maze.sl + (xvar.img_maze.bpp // 8)
        draw_pattern(test, MazeData.ppc, xvar.img_maze, (0xFFFFFFEE))
                
                

        current = next
    draw_all(xvar)

def find_pos(x: int, y: int, xvar: XVar) -> int:
    pixel_x = x * MazeData.ppc
    pixel_y = y * MazeData.ppc
    opp = xvar.img_maze.bpp // 8
    if x != 0:
        pixel_x -= 1
    offset = pixel_y * xvar.img_maze.sl + pixel_x * opp
    return offset

def draw_menu(xvar: XVar):
    xvar.mlx.mlx_string_put(xvar.mlx_ptr, xvar.win_1, 400, 5,0xFFFFFFEE , "1:regen 2:color 3:path 4:exit")

def draw_all(xvar: XVar):
    entry = find_pos(xvar.maze.entry[0], xvar.maze.entry[1], xvar)
    exit = find_pos(xvar.maze.exit[0], xvar.maze.exit[1], xvar)
    draw_pattern(entry, MazeData.ppc, xvar.img_maze, (0xFFF08080))
    draw_pattern(exit, MazeData.ppc, xvar.img_maze, (0xFFFF00FF))
    for i, value in enumerate(xvar.maze.grid):
        # print(i)
        x = int(i % xvar.maze.width)
        y = int(i / xvar.maze.width)
        # pixel_x = x * MazeData.ppc
        # pixel_y = y * MazeData.ppc
        # opp = xvar.img_maze.bpp // 8
        # if x != 0:
            # pixel_x -= 1
        # offset = pixel_y * xvar.img_maze.sl + pixel_x * opp
        offset = find_pos(x, y, xvar)
        if value == 15:
            draw_pattern(offset, MazeData.ppc, xvar.img_maze, MazeData.color)
        else:
            draw_cell(offset, value, MazeData.ppc, xvar.img_maze)
    draw_menu(xvar)


def display(maze: Maze):
    # setup xvar
    xvar = XVar()
    xvar.maze = maze
    try:
        img_h = 1000
        img_w = 1000
        if xvar.maze.width > 450 or xvar.maze.height > 450:
            tmp = xvar.maze.width
            if xvar.maze.height > tmp:
                tmp = xvar.maze.height
            img_w = tmp * 2
            img_h = tmp * 2 + 1
        xvar.mlx = Mlx()
        xvar.mlx_ptr = xvar.mlx.mlx_init()
        xvar.win_1 = xvar.mlx.mlx_new_window(
            xvar.mlx_ptr, img_w + 200, img_h + 200, "A-maze-ing")
        xvar.win_1_w = img_w + 200
        xvar.win_1_h = img_h + 200
        # img maze
        xvar.img_maze.img = xvar.mlx.mlx_new_image(xvar.mlx_ptr, img_w, img_h)
        xvar.img_maze.data, xvar.img_maze.bpp, xvar.img_maze.sl, xvar.img_maze.iformat = xvar.mlx.mlx_get_data_addr(
            xvar.img_maze.img)
        # print(xvar.img_maze.iformat)
        xvar.img_maze.width = img_w
        xvar.img_maze.height = img_h
        if maze.width < 10 or maze.height < 10:
            xvar.img_maze.width = 800
            xvar.img_maze.height = 800
        MazeData.set_ppc(xvar.maze.width, xvar.maze.height, xvar.img_maze)
    except Exception as e:
        print(f"Error setup xvar (mlx, MazeData): {e}")
    # draw put img
    try:
        # print(len(xvar.img_maze.data))
        draw_all(xvar)
        img_pos = (xvar.win_1_w - MazeData.ppc * xvar.maze.width) // 2
        xvar.mlx.mlx_put_image_to_window(xvar.mlx_ptr, xvar.win_1, xvar.img_maze.img, img_pos, 50)
    except Exception as e:
        print(f"Error draw / put img: {e}")
        sys.exit(1)

    # Hook event
    xvar.mlx.mlx_mouse_hook(xvar.win_1, gere_mouse_1, xvar)
    xvar.mlx.mlx_hook(xvar.win_1, 33, 0, gere_close_1, xvar)
    xvar.mlx.mlx_key_hook(xvar.win_1, key_press, xvar)

    # loop
    xvar.mlx.mlx_loop(xvar.mlx_ptr)


if __name__ == "__main__":
    print("test")
