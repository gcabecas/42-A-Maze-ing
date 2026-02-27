import sys
from typing import Any, Optional
from mlx import Mlx
from mazegen import Maze


class ImgData:
    """Represent image buffer metadata used for rendering.

    This class stores the MLX image pointer and all information
    required to manipulate raw pixel data.

    Attributes:
        img (Any): Pointer to the MLX image object.
        width (int): Image width in pixels.
        height (int): Image height in pixels.
        data (bytearray): Raw image buffer.
        sl (int): Size of one image line in bytes.
        bpp (int): Bits per pixel.
        iformat (int): Pixel format identifier.
    """    """Container for image-related rendering data.

    This class stores the raw image pointer, its dimensions, and
    metadata required for pixel manipulation.
    """
    def __init__(self) -> None:
        """Initialize an empty ImgData instance.

        Returns:
            None
        """
        self.img: Any = None
        self.width: int = 0
        self.height: int = 0
        self.data: bytearray = bytearray()
        self.sl: int = 0
        self.bpp: int = 0
        self.iformat: int = 0


class RenderData:
    """Store rendering configuration parameters.

    This class centralizes all visual settings used during maze
    rendering.

    Attributes:
        color (int): Current wall color.
        ppc (int): Pixels per cell.
        show_path (bool): Whether the solution path is displayed.
        entry_color (int): Color for entry cell.
        exit_color (int): Color for exit cell.
        path_color (int): Color for solution path.
        menu_color (int): Color for menu text.
    """
    def __init__(self) -> None:
        """Initialize default rendering values.

        Returns:
            None
        """
        self.color = 0x55FFFF00
        self.ppc = 0
        self.show_path = False
        self.entry_color = 0xFFF08080
        self.exit_color = 0xFFFF00FF
        self.path_color = 0xFFFFFFEE
        self.menu_color = 0xFFFFFFEE

    def change_color(self) -> None:
        """Change the current wall color cyclically.

        Returns:
            None
        """
        colors = [0x5500FFFF, 0x554169E1, 0x55FFFF00]
        i = colors.index(self.color)
        self.color = colors[(i + 1) % len(colors)]


class Renderer:
    """Render a maze into an MLX image buffer.

    This class is responsible for drawing the maze grid, entry and exit
    cells, solution path, and menu overlay into a graphical window
    using an MLX backend.
    """
    def __init__(
            self,
            mlx: Mlx,
            mlx_ptr: Any,
            window: Any,
            img: ImgData,
            maze: Maze,
            rend_data: RenderData) -> None:
        """Initialize the renderer with required graphical resources.

        Args:
            mlx (Mlx): MLX wrapper instance.
            mlx_ptr (Any): Pointer returned by mlx_init.
            window (Any): Window pointer created by MLX.
            img (ImgData): Image data container.
            maze (Maze): Maze instance to render.
            rend_data (RenderData): Rendering configuration data.

        Returns:
            None
        """
        self.mlx: Mlx = mlx
        self.mlx_ptr = mlx_ptr
        self.window = window
        self.img = img
        self.maze = maze
        self.rend_data = rend_data
        self.setup_ppc()

    def setup_ppc(self) -> None:
        """Compute pixels per cell based on image and maze size.

        The value is stored in the rendering configuration.

        Returns:
            None
        """
        img_size = min(self.img.width, self.img.height)
        maze_size = max(self.maze.width, self.maze.height)
        self.rend_data.ppc = img_size // maze_size

    def put_pixel(self, offset: int, color: int) -> None:
        """Write a single pixel color into the image buffer.

        Args:
            offset (int): Byte offset in the image buffer.
            color (int): 32-bit integer color value.

        Returns:
            None
        """
        self.img.data[offset: offset + 4] = color.to_bytes(4, 'little')

    def find_offset(self, x: int, y: int) -> int:
        """Compute the memory offset for a maze cell.

        Args:
            x (int): Cell x-coordinate.
            y (int): Cell y-coordinate.

        Returns:
            int: Corresponding byte offset in the image buffer.
        """
        opp = self.img.bpp // 8
        pxl_x = x * self.rend_data.ppc
        pxl_y = y * self.rend_data.ppc
        offset = pxl_y * self.img.sl + pxl_x * opp
        return offset

    def clear_img(self) -> None:
        """Clear the entire image buffer.

        All pixels are reset to transparent black.

        Returns:
            None
        """
        for i in range(0, len(self.img.data), 4):
            self.img.data[i: i + 4] = (0x00000000).to_bytes(4, 'little')

    def draw_block(self, offset: int, color: int) -> None:
        """Draw a filled square representing a maze cell.

        Args:
            offset (int): Starting byte offset of the cell.
            color (int): 32-bit integer color value.

        Returns:
            None
        """
        opp = self.img.bpp // 8
        ppc = self.rend_data.ppc

        for y in range(ppc):
            line = offset + y * self.img.sl
            for x in range(ppc):
                self.put_pixel(line + x * opp, color)

    def draw_cell(self, offset: int, value: int) -> None:
        """Draw maze cell walls according to a bitmask value.

        Each bit in the value represents the presence of a wall in
        one of the four cardinal directions.

        Args:
            offset (int): Starting byte offset of the cell.
            value (int): Bitmask representing cell walls.

        Returns:
            None
        """
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
        """Render the complete maze grid.

        Returns:
            None
        """
        for i, value in enumerate(self.maze.grid):
            x = i % self.maze.width
            y = i // self.maze.width
            offset = self.find_offset(x, y)

            if value == 15:
                self.draw_block(offset, self.rend_data.color)
            else:
                self.draw_cell(offset, value)

    def draw_entry_exit(self) -> None:
        """Highlight the maze entry and exit cells.

        Returns:
            None
        """
        entry_x, entry_y = self.maze.entry
        entry_off = self.find_offset(entry_x, entry_y)
        self.draw_block(entry_off, self.rend_data.entry_color)

        exit_x, exit_y = self.maze.exit
        exit_off = self.find_offset(exit_x, exit_y)
        self.draw_block(exit_off, self.rend_data.exit_color)

    def draw_path(self) -> None:
        """Draw the solution path over the maze.

        Returns:
            None
        """
        current = self.maze.entry
        for direction in self.maze.solver[: -1]:
            current = self.next_step(direction, current)
            offset = self.find_offset(current[0], current[1])
            self.draw_block(offset, self.rend_data.path_color)
        self.draw_maze()

    @staticmethod
    def next_step(direction: str, current: tuple[int, int]) -> tuple[int, int]:
        """Compute the next cell position from a direction.

        Args:
            direction (str): Direction ("N", "S", "E", or "W").
            current (tuple[int, int]): Current (x, y) coordinates.

        Returns:
            tuple[int, int]: Updated (x, y) coordinates.
        """
        x, y = current
        moves = {"E": (x + 1, y),
                 "S": (x, y + 1),
                 "W": (x - 1, y),
                 "N": (x, y - 1)}
        return moves[direction]

    def draw_menu(self) -> None:
        """Render the control menu text in the window.

        Returns:
            None
        """
        self.mlx.mlx_string_put(
            self.mlx_ptr,
            self.window,
            400,
            5,
            self.rend_data.menu_color,
            "1.regen 2.color 3.path 4.exit")

    def draw_all(self) -> None:
        """Render the complete scene.

        This includes clearing the image, drawing entry/exit,
        optionally drawing the path, and rendering the maze grid.

        Returns:
            None
        """
        self.clear_img()
        self.draw_entry_exit()
        self.draw_menu()
        if self.rend_data.show_path:
            self.draw_path()
        self.draw_maze()

    def push(self, window_width: int) -> None:
        """Display the rendered image in the window.

        Args:
            window_width (int): Width of the application window.

        Returns:
            None
        """
        pos_x = (window_width - self.rend_data.ppc * self.maze.width) // 2
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr,
            self.window,
            self.img.img,
            pos_x,
            50
        )


class App:
    """Main graphical application for displaying and interacting with a maze.

    This class initializes the MLX environment, creates the rendering
    context, and manages user interactions such as regenerating the
    maze, changing colors, and toggling the solution path display.
    """

    def __init__(self, maze: Maze) -> None:
        """Initialize the application with a maze instance.

        Args:
            maze (Maze): Maze instance to display.

        Returns:
            None
        """
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
        """Start the graphical event loop.

        This method registers keyboard and window hooks and launches
        the MLX main loop.

        Returns:
            None
        """
        self.draw()
        self.mlx.mlx_key_hook(self.window, self.gere_keys, self)
        self.mlx.mlx_hook(self.window, 33, 0, self.close, None)
        self.mlx.mlx_loop(self.mlx_ptr)

    def setup_image(self) -> None:
        """Create and configure the image buffer.

        The image size is determined based on maze dimensions. Larger
        mazes result in a dynamically scaled image size.

        Returns:
            None
        """
        img_size = 1000
        if self.maze.width > 300 or self.maze.height > 300:
            img_size = max(self.maze.width, self.maze.height) * 4
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
        """Create and configure the application window.

        Returns:
            None
        """
        self.win_w = self.img.width + 200
        self.win_h = self.img.height + 200
        self.window = self.mlx.mlx_new_window(
            self.mlx_ptr,
            self.win_w,
            self.win_h,
            "A-maze-ing"
        )

    def gere_keys(self, keycode: int, _: Any) -> None:
        """Handle keyboard input events.

        Args:
            keycode (int): Key code representing the pressed key.
            _ (Any): Unused callback parameter.

        Returns:
            None
        """
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
        """Regenerate the maze and refresh the display.

        Returns:
            None
        """
        self.maze = regen_maze(self.maze)
        self.renderer.maze = self.maze
        self.renderer.setup_ppc()
        self.draw()

    def change_color(self) -> None:
        """Change the wall color and refresh the display.

        Returns:
            None
        """
        self.rend_data.change_color()
        self.draw()

    def toogle_path(self) -> None:
        """Toggle the visibility of the solution path.

        Returns:
            None
        """
        self.rend_data.show_path = not self.rend_data.show_path
        self.draw()

    def draw(self) -> None:
        """Redraw the complete window content.

        Returns:
            None
        """
        self.mlx.mlx_clear_window(self.mlx_ptr, self.window)
        self.renderer.draw_all()
        self.renderer.push(self.win_w)

    def close(self, _: Optional[Any] = None) -> None:
        """Release graphical resources and close the application.

        Args:
            _ (Optional[Any]): Optional callback parameter.

        Returns:
            None
        """
        self.renderer.clear_img()
        self.mlx.mlx_destroy_image(self.mlx_ptr, self.img.img)
        self.mlx.mlx_destroy_window(self.mlx_ptr, self.window)
        self.mlx.mlx_loop_exit(self.mlx_ptr)


def regen_maze(maze: Maze) -> Maze:
    """Generate a new maze using the same configuration.

    Args:
        maze (Maze): Existing maze instance.

    Returns:
        Maze: Newly generated maze instance.

    Raises:
        SystemExit: If maze generation fails.
    """
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
    """Launch the graphical application to display a maze.

    Args:
        maze (Maze): Maze instance to display.

    Returns:
        None
    """
    app = App(maze)
    app.start()
