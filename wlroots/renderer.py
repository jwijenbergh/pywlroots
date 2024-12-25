# Copyright (c) 2019 Sean Vig

from __future__ import annotations

from typing import Union

from pywayland.server import Display

from wlroots import Ptr, ffi, lib
from wlroots.backend import Backend

ColorType = Union[list, tuple, ffi.CData]


class Renderer(Ptr):
    def __init__(self, ptr) -> None:
        """Obtains the renderer this backend is using

        The renderer is automatically destroyed as the backend is destroyed.
        """
        self._ptr = ptr

    @staticmethod
    def autocreate(backend: Backend) -> Renderer:
        """Creates a suitable renderer for a backend."""
        renderer_ptr = lib.wlr_renderer_autocreate(backend._ptr)
        if renderer_ptr == ffi.NULL:
            raise RuntimeError("Unable to create a renderer.")
        return Renderer(renderer_ptr)

    def init_display(self, display: Display) -> None:
        """Creates necessary shm and invokes the initialization of the implementation

        :param display:
            The Wayland display to initialize the renderer against.
        """
        ret = lib.wlr_renderer_init_wl_display(self._ptr, display._ptr)
        if not ret:
            raise RuntimeError("Unable to initialize renderer for display")

class DRMFormatSet(Ptr):
    """struct wlr_drm_format_set"""

    def __init__(self, ptr) -> None:
        self._ptr = ptr

    def get(self, format: int) -> DRMFormat | None:
        ptr = lib.wlr_drm_format_set_get(self._ptr, format)
        if ptr == ffi.NULL:
            return None
        return DRMFormat(ptr)


class DRMFormat(Ptr):
    """struct wlr_drm_format"""

    def __init__(self, ptr) -> None:
        self._ptr = ptr
