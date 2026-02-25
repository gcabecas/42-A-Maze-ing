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
            MazeData.color = 0x550000FF
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
        self.img_png: ImgData = ImgData()
        self.img_xpm: ImgData = ImgData()
        self.imgidx = 0
        self.gen_color = None
        self.maze: Maze = None
    
def gere_close_1(xvar):
    xvar.mlx.mlx_loop_exit(xvar.mlx_ptr)


def gere_close_2(xvar):
    xvar.mlx.mlx_destroy_window(xvar.mlx_ptr, xvar.win_2)
    xvar.win_2 = None


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
        xvar.img_maze.img = xvar.mlx.mlx_new_image(xvar.mlx_ptr, 1000, 1000)
        xvar.img_maze.data, xvar.img_maze.bpp, xvar.img_maze.sl, xvar.img_maze.iformat = xvar.mlx.mlx_get_data_addr(
            xvar.img_maze.img)
        xvar.maze = new_maze
        MazeData.set_ppc(new_maze.width, new_maze.height, xvar.img_maze)
        draw_all(xvar)
        test = (xvar.win_1_w - MazeData.ppc * xvar.maze.width) // 2
        xvar.mlx.mlx_put_image_to_window(
            xvar.mlx_ptr, xvar.win_1, xvar.img_maze.img, test, 5)
    elif keycode == 50:
        if xvar.gen_color is None:
            xvar.gen_color = iter(MazeData.new_color())
        next(xvar.gen_color)
        xvar.mlx.mlx_clear_window(xvar.mlx_ptr, xvar.win_1)
        draw_all(xvar)
        test = (xvar.win_1_w - MazeData.ppc * xvar.maze.width) // 2
        xvar.mlx.mlx_put_image_to_window(
            xvar.mlx_ptr, xvar.win_1, xvar.img_maze.img, test, 5)
    elif keycode == 51:
        xvar.mlx.mlx_clear_window(xvar.mlx_ptr, xvar.win_1)
        draw_all(xvar)
        # draw_path(xvar)

        pos = (xvar.win_1_w - MazeData.ppc * xvar.maze.width) // 2
        xvar.mlx.mlx_put_image_to_window(
            xvar.mlx_ptr, xvar.win_1, xvar.img_maze.img, pos, 5)


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
        img_maze: ImgData):
    for i in [j * img_maze.sl for j in range(ppc)]:
        new_start = start + i
        for k in range(0, ppc * 4, 4):
            img_maze.data[new_start + k: new_start + k + 4] = MazeData.color.to_bytes(4, 'little')


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


# draw_path
# def draw_path(xvar: XVar):
    # start = xvar.maze.entry
    # end = xvar.maze.exit


def draw_all(xvar: XVar):
    for i, value in enumerate(xvar.maze.grid):
        x = int(i % xvar.maze.width)
        y = int(i / xvar.maze.width)
        pixel_x = x * MazeData.ppc
        pixel_y = y * MazeData.ppc
        opp = xvar.img_maze.bpp // 8
        if x != 0:
            pixel_x -= 1
        offset = pixel_y * xvar.img_maze.sl + pixel_x * opp
        if value == 15:
            draw_pattern(offset, MazeData.ppc, xvar.img_maze)
        else:
            draw_cell(offset, value, MazeData.ppc, xvar.img_maze)


def display(maze: Maze):
    # setup xvar
    xvar = XVar()
    xvar.maze = maze
    try:
        xvar.mlx = Mlx()
        xvar.mlx_ptr = xvar.mlx.mlx_init()
        xvar.win_1 = xvar.mlx.mlx_new_window(
            xvar.mlx_ptr, 1200, 1200, "A-maze-ing")
        xvar.win_1_w = 1200
        xvar.win_1_h = 1200
        xvar.img_maze.img = xvar.mlx.mlx_new_image(xvar.mlx_ptr, 1000, 1000)
        xvar.img_maze.data, xvar.img_maze.bpp, xvar.img_maze.sl, xvar.img_maze.iformat = xvar.mlx.mlx_get_data_addr(
            xvar.img_maze.img)
        xvar.img_maze.width = 1000
        xvar.img_maze.height = 1000
        MazeData.set_ppc(xvar.maze.width, xvar.maze.height, xvar.img_maze)
    except Exception as e:
        print(f"Error setup xvar (mlx, MazeData): {e}")
    # draw put img
    try:
        draw_all(xvar)
        img_pos = (xvar.win_1_w - MazeData.ppc * xvar.maze.width) // 2
        xvar.mlx.mlx_put_image_to_window(xvar.mlx_ptr, xvar.win_1, xvar.img_maze.img, 100, 5)
        print(img_pos)
        print(MazeData.ppc)
        print(xvar.maze.width)
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
