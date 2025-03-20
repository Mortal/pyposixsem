# Licensed under GNU General Public License v2 or later.
# Ported from pshm_ucase.c from shm_open(3) in Linux man-pages 6.13.
"""
This file is used by the two programs pshm_ucase_bounce.py and pshm_ucase_send.py.
Its primary purpose is to define a structure that will be imposed on the memory
object that is shared between the two programs.
"""

import ctypes

import pyposixsem


# Maximum size for exchanged string
BUF_SIZE = 1024


# Define a structure that will be imposed on the shared memory object
class Shmbuf(ctypes.Structure):
    _fields_ = [
        # POSIX unnamed semaphore
        ("sem1", pyposixsem.SemT),
        # POSIX unnamed semaphore
        ("sem2", pyposixsem.SemT),
        # Number of bytes used in 'buf'
        ("cnt", ctypes.c_size_t),
        # Data being transferred
        ("buf", ctypes.c_char * BUF_SIZE),
    ]
