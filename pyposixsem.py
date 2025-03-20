import ctypes
import os
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # Note, Buffer is 3.12+
    from collections.abc import Buffer


pthread = ctypes.CDLL("libpthread.so.0", use_errno=True)


# Note, we use the size of 32 bytes that is valid for 64-bit systems,
# even though it's actually only 16 bytes on 32-bit systems.
SEM_T_SIZE = 32


class SemT(ctypes.Union):
    _fields_ = [
        ("__size", ctypes.c_char * SEM_T_SIZE),
        ("__align", ctypes.c_long),
    ]


sem_init = pthread.sem_init
sem_init.restype = ctypes.c_int
sem_init.argtypes = [ctypes.POINTER(SemT), ctypes.c_int, ctypes.c_uint]
sem_wait = pthread.sem_wait
sem_wait.restype = ctypes.c_int
sem_wait.argtypes = [ctypes.POINTER(SemT)]
sem_post = pthread.sem_post
sem_post.restype = ctypes.c_int
sem_post.argtypes = [ctypes.POINTER(SemT)]


def _ctypes_oserror(func: str) -> OSError:
    errno = ctypes.get_errno()
    return OSError(f"{func}: {errno}: {os.strerror(errno)}")


class SharedSemaphore:
    def __init__(self, inner: SemT) -> None:
        self.inner = inner

    @staticmethod
    def from_buffer(buf: "Buffer") -> "SharedSemaphore":
        return SharedSemaphore(SemT.from_buffer(buf))

    def init(self, pshared: int, value: int) -> None:
        """
        Initializes the semaphore in multithreading (pshared=0)
        or multiprocessing (pshared>0) mode with the given initial value.
        """
        if sem_init(self.inner, pshared, value):
            raise _ctypes_oserror("sem_init")

    def wait(self) -> None:
        "Decrements semaphore by one."
        if sem_wait(self.inner):
            raise _ctypes_oserror("sem_wait")

    def post(self) -> None:
        "Increments semaphore by one."
        if sem_post(self.inner):
            raise _ctypes_oserror("sem_post")
