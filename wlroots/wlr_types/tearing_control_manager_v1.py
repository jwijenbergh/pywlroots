# Copyright (c) Jeroen Wijenbergh 2024

from __future__ import annotations

import enum
from wlroots import Ptr, ffi, lib

import typing
if typing.TYPE_CHECKING:
    from pywayland.server import Display
    from pywlroots.compositor import Surface

@enum.unique
class WpTearingControlV1PresentationHint(enum.IntEnum):
    VSYNC = lib.WP_TEARING_CONTROL_V1_PRESENTATION_HINT_VSYNC
    ASYNC = lib.WP_TEARING_CONTROL_V1_PRESENTATION_HINT_ASYNC

class TearingControlManagerV1(Ptr):
    def __init__(self, display: Display, version: int) -> None:
        self._ptr = lib.wlr_tearing_control_manager_v1_create(display._ptr, version)

    def surface_hint_from_surface(surface: Surface | None):
        surfaceptr = ffi.NULL
        if surface is not None:
            surfaceptr = surface._ptr
        return WpTearingControlV1PresentationHint(lib.wlr_tearing_control_manager_v1_surface_hint_from_surface(self._ptr, surfaceptr))
