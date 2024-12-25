# Copyright (c) 2019 Sean Vig

from __future__ import annotations

import enum
import weakref

from pywayland.server import EventLoop, Signal

from wlroots.util.log import logger
from wlroots.wlr_types.input_device import InputDevice
from wlroots.wlr_types.output import Output

from . import Ptr, ffi, lib


class BackendType(enum.Enum):
    AUTO = enum.auto()
    HEADLESS = enum.auto()


class Backend(Ptr):
    def __init__(self, loop: EventLoop, *, backend_type=BackendType.AUTO) -> None:
        """Create a backend to interact with a Wayland display

        :param loop:
            The Wayland event loop to create the backend against.
        :param backend_type:
            The type of the backend to create.  The default (auto-detection)
            will use environment variables, including $DISPLAY (for X11 nested
            backends), $WAYLAND_DISPLAY (for Wayland backends), and
            $WLR_BACKENDS (to set the available backends).
        """
        self.session: Session | None = None

        if backend_type == BackendType.AUTO:
            session_ptr = ffi.new("struct wlr_session **")
            ptr = lib.wlr_backend_autocreate(loop._ptr, session_ptr)
            self.session = Session(session_ptr[0])
        elif backend_type == BackendType.HEADLESS:
            ptr = lib.wlr_headless_backend_create(loop._ptr)
        else:
            raise ValueError(f"Unknown backend type: {backend_type}")

        if ptr == ffi.NULL:
            raise RuntimeError("Failed to create wlroots backend")

        self._ptr = ffi.gc(ptr, lib.wlr_backend_destroy)
        self._weak_event_loop = weakref.ref(loop)

        self.destroy_event = Signal(ptr=ffi.addressof(self._ptr.events.destroy))
        self.new_input_event = Signal(
            ptr=ffi.addressof(self._ptr.events.new_input), data_wrapper=InputDevice
        )
        self.new_output_event = Signal(
            ptr=ffi.addressof(self._ptr.events.new_output), data_wrapper=Output
        )

    def destroy(self) -> None:
        """Destroy the backend and clean up all of its resources

        Normally called automatically when the wl_event_loop is destroyed.
        """
        if self._ptr is None:
            logger.warning("Backend already destroyed, doing nothing")
        else:
            maybe_loop = self._weak_event_loop()
            if maybe_loop is not None and maybe_loop._ptr is not None:
                ffi.release(self._ptr)
            else:
                logger.warning(
                    "The display has already been cleaned up, clearing loop without destroying"
                )
                self._ptr = ffi.gc(self._ptr, None)

            self._ptr = None

    def start(self) -> bool:
        """Start the backend

        This may signal new_input or new_output immediately, but may also wait
        until the display's event loop begins.
        """
        return lib.wlr_backend_start(self._ptr)

    def __enter__(self) -> Backend:
        """Context manager to create and clean-up the backend"""
        if not self.start():
            self.destroy()
            raise RuntimeError("Unable to start backend")
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        """Destroy the backend on context exit"""
        self.destroy()

    def get_session(self) -> Session:
        if self.session is None:
            raise ValueError("Backend does not have a session")
        return self.session

    @property
    def is_headless(self) -> bool:
        return lib.wlr_backend_is_headless(self._ptr)

    @property
    def is_multi(self) -> bool:
        """
        Returns if this backend represents a multi-backend.

        Multi-backends wrap an arbitrary number of backends and aggregate
        their new_output/new_input signals.
        """
        return lib.wlr_backend_is_multi(self._ptr)


class Session:
    def __init__(self, ptr) -> None:
        """The running session"""
        self._ptr = ptr

    def change_vt(self, vt: int) -> bool:
        return lib.wlr_session_change_vt(self._ptr, vt)
