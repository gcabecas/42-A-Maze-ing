from typing import Any, Callable


class Mlx:
    def __init__(self) -> None: ...

    def mlx_init(self) -> Any: ...

    def mlx_new_window(
        self,
        mlx_ptr: Any,
        width: int,
        height: int,
        title: str) -> Any: ...

    def mlx_new_image(self, mlx_ptr: Any, width: int, height: int) -> Any: ...

    def mlx_get_data_addr(self, img: Any) -> tuple[Any, int, int, int]: ...

    def mlx_put_image_to_window(
        self,
        mlx_ptr: Any,
        win: Any,
        img: Any,
        x: int,
        y: int) -> int: ...

    def mlx_string_put(
        self,
        mlx_ptr: Any,
        win: Any,
        x: int,
        y: int,
        color: int,
        s: str) -> int: ...

    def mlx_clear_window(self, mlx_ptr: Any, win: Any) -> int: ...

    def mlx_key_hook(self, win: Any, func: Callable[[
                     int, Any], Any], param: Any) -> int: ...

    def mlx_loop(self, mlx_ptr: Any) -> int: ...

    def mlx_destroy_image(self, mlx_ptr: Any, img: Any) -> int: ...

    def mlx_destroy_window(self, mlx_ptr: Any, win: Any) -> int: ...

    def mlx_loop_exit(self, mlx_ptr: Any) -> int: ...
