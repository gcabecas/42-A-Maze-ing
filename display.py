import sys
from typing import Any, Optional
from mlx import Mlx
from maze import Maze


class ImgData:
    def __init__(self) -> None:
        self.img: Any = None
        self.width: int = 0
        self.height: int = 0
        self.data: bytearray = bytearray()
        self.sl: int = 0
        self.bpp: int = 0
        self.iformat: int = 0


class RenderData:
    def __init__(self) -> None:
        self.color = 0x55FFFF00
        self.ppc = 0
        self.show_path = False
        self.entry_color = 0xFFF08080
        self.exit_color = 0xFFFF00FF
        self.path_color = 0xFFFFFFEE
        self.menu_color = 0xFFFFFFEE

    def change_color(self) -> None:
        colors = [0x5500FFFF, 0x554169E1, 0x55FFFF00]
        i = colors.index(self.color)
        self.color = colors[(i + 1) % len(colors)]


class Renderer:
    def __init__(
            self,
            mlx: Mlx,
            mlx_ptr: Any,
            window: Any,
            img: ImgData,
            maze: Maze,
            rend_data: RenderData) -> None:
        self.mlx: Mlx = mlx
        self.mlx_ptr = mlx_ptr
        self.window = window
        self.img = img
        self.maze = maze
        self.rend_data = rend_data

        self.setup_ppc()

    def setup_ppc(self) -> None:
        img_size = min(self.img.width, self.img.height)
        maze_size = max(self.maze.width, self.maze.height)
        self.rend_data.ppc = img_size // maze_size

    def put_pixel(self, offset: int, color: int) -> None:
        self.img.data[offset: offset + 4] = color.to_bytes(4, 'little')

    def find_offset(self, x: int, y: int) -> int:
        opp = self.img.bpp // 8
        pxl_x = x * self.rend_data.ppc
        pxl_y = y * self.rend_data.ppc
        offset = pxl_y * self.img.sl + pxl_x * opp
        return offset

    def clear_img(self) -> None:
        for i in range(0, len(self.img.data), 4):
            self.img.data[i: i + 4] = (0x00000000).to_bytes(4, 'little')

    def draw_block(self, offset: int, color: int) -> None:
        opp = self.img.bpp // 8
        ppc = self.rend_data.ppc

        for y in range(ppc):
            line = offset + y * self.img.sl
            for x in range(ppc):
                self.put_pixel(line + x * opp, color)

    def draw_cell(self, offset: int, value: int) -> None:
        ppc = self.rend_data.ppc
        color = self.rend_data.color
        sl = self.img.sl
        opp = self.img.bpp // 8

        if value & 1 << 0:
            for x in range(ppc):
                self.put_pixel(offset + x * opp, color)

        if value & 1 << 1:
            for y in range(ppc):
                self.put_pixel(offset + y * sl + (ppc - 1) * opp, color)

        if value & 1 << 2:
            for x in range(ppc):
                self.put_pixel(offset + (ppc - 1) * sl + x * opp, color)

        if value & 1 << 3:
            for y in range(ppc):
                self.put_pixel(offset + y * sl, color)

    def draw_maze(self) -> None:
        for i, value in enumerate(self.maze.grid):
            x = i % self.maze.width
            y = i // self.maze.width
            offset = self.find_offset(x, y)

            if value == 15:
                self.draw_block(offset, self.rend_data.color)
            else:
                self.draw_cell(offset, value)

    def draw_entry_exit(self) -> None:
        entry_x, entry_y = self.maze.entry
        entry_off = self.find_offset(entry_x, entry_y)
        self.draw_block(entry_off, self.rend_data.entry_color)

        exit_x, exit_y = self.maze.exit
        exit_off = self.find_offset(exit_x, exit_y)
        self.draw_block(exit_off, self.rend_data.exit_color)

    def draw_path(self) -> None:
        current = self.maze.entry
        for direction in self.maze.solver[: -1]:
            current = self.next_step(direction, current)
            offset = self.find_offset(current[0], current[1])
            self.draw_block(offset, self.rend_data.path_color)
        self.draw_maze()

    @staticmethod
    def next_step(direction: str, current: tuple[int, int]) -> tuple[int, int]:
        x, y = current
        moves = {"E": (x + 1, y),
                 "S": (x, y + 1),
                 "W": (x - 1, y),
                 "N": (x, y - 1)}
        return moves[direction]

    def draw_menu(self) -> None:
        self.mlx.mlx_string_put(
            self.mlx_ptr,
            self.window,
            400,
            5,
            self.rend_data.menu_color,
            "1.regen 2.color 3.path 4.exit")

    def draw_all(self) -> None:
        self.clear_img()
        self.draw_entry_exit()
        self.draw_menu()
        if self.rend_data.show_path:
            self.draw_path()
        self.draw_maze()

    def push(self, window_width: int) -> None:
        pos_x = (window_width - self.rend_data.ppc * self.maze.width) // 2
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr,
            self.window,
            self.img.img,
            pos_x,
            50
        )


class App:

    def __init__(self, maze: Maze) -> None:
        self.maze = maze
        self.rend_data = RenderData()
        self.mlx = Mlx()
        self.mlx_ptr = self.mlx.mlx_init()
        self.setup_image()
        self.setup_window()
        self.renderer = Renderer(
            self.mlx,
            self.mlx_ptr,
            self.window,
            self.img,
            self.maze,
            self.rend_data
        )

    def start(self) -> None:
        self.draw()
        self.mlx.mlx_key_hook(self.window, self.gere_keys, self)
        self.mlx.mlx_hook(self.window, 33, 0, self.close, None)
        self.mlx.mlx_loop(self.mlx_ptr)

    def setup_image(self) -> None:
        img_size = 1000
        if self.maze.width > 300 or self.maze.height > 300:
            img_size = max(self.maze.width, self.maze.height) * 3
        self.img = ImgData()

        self.img.img = self.mlx.mlx_new_image(
            self.mlx_ptr,
            img_size,
            img_size
        )

        (
            self.img.data,
            self.img.bpp,
            self.img.sl,
            self.img.iformat
        ) = self.mlx.mlx_get_data_addr(self.img.img)

        self.img.width = img_size
        self.img.height = img_size

    def setup_window(self) -> None:
        self.win_w = self.img.width + 200
        self.win_h = self.img.height + 200
        self.window = self.mlx.mlx_new_window(
            self.mlx_ptr,
            self.win_w,
            self.win_h,
            "A-maze-ing"
        )

    def gere_keys(self, keycode: int, _: Any) -> None:
        actions = {
            49: self.regenerate,
            50: self.change_color,
            51: self.toogle_path,
            52: self.close
        }
        action = actions.get(keycode)
        if action:
            action()

    def regenerate(self) -> None:
        self.maze = regen_maze(self.maze)
        self.renderer.maze = self.maze
        self.renderer.setup_ppc()
        self.draw()

    def change_color(self) -> None:
        self.rend_data.change_color()
        self.draw()

    def toogle_path(self) -> None:
        self.rend_data.show_path = not self.rend_data.show_path
        self.draw()

    def draw(self) -> None:
        self.mlx.mlx_clear_window(self.mlx_ptr, self.window)
        self.renderer.draw_all()
        self.renderer.push(self.win_w)

    def close(self, _: Optional[Any]) -> None:
        self.renderer.clear_img()
        self.mlx.mlx_destroy_image(self.mlx_ptr, self.img.img)
        self.mlx.mlx_destroy_window(self.mlx_ptr, self.window)
        self.mlx.mlx_loop_exit(self.mlx_ptr)


def regen_maze(maze: Maze) -> Maze:
    try:
        new_maze = Maze(
            maze.width,
            maze.height,
            None,
            maze.entry,
            maze.exit,
            maze.output_file,
            maze.perfect)
        new_maze.generate()
    except ValueError as e:
        print(f"Error generating maze: {e}", file=sys.stderr)
        sys.exit(1)
    else:
        return new_maze


def display(maze: Maze) -> None:
    app = App(maze)
    app.start()
