#!/usr/bin/env python3
# Licensed under GNU General Public License v2 or later.
# Ported from pshm_ucase_bounce.c from shm_open(3) in Linux man-pages 6.13.
"""
The "bounce" program creates a new shared memory object with the name given in
its command-line argument and sizes the object to match the size of the shmbuf
structure defined in the header file. It then maps the object into the process's
address space, and initializes two POSIX semaphores inside the object to 0.

After the "send" program has posted the first of the semaphores, the "bounce"
program upper cases the data that has been placed in the memory by the "send"
program and then posts the second semaphore to tell the "send" program that it
may now access the shared memory.
"""

import argparse
import ctypes
import multiprocessing.shared_memory

import pshm_ucase
import pyposixsem


parser = argparse.ArgumentParser()
parser.add_argument("shmpath")


def main() -> None:
    args = parser.parse_args()
    # Create shared memory object and set its size to the size of our structure.
    buf = multiprocessing.shared_memory.SharedMemory(
        args.shmpath, create=True, size=ctypes.sizeof(pshm_ucase.Shmbuf), track=False
    )
    try:
        # Access the shared memory through the Shmbuf type.
        shmbuf = pshm_ucase.Shmbuf.from_buffer(buf.buf)

        # Initialize semaphores as process-shared, with value 0.
        sem1 = pyposixsem.SharedSemaphore(shmbuf.sem1)
        sem1.init(1, 0)
        sem2 = pyposixsem.SharedSemaphore(shmbuf.sem2)
        sem2.init(1, 0)

        # Wait for 'sem1' to be posted by peer before touching shared memory.
        sem1.wait()

        # Convert data in shared memory into upper case.
        shmbuf.buf = shmbuf.buf.upper()

        # Post 'sem2' to tell the peer that it can now access the modified data in shared memory.
        sem2.post()
    finally:
        # Use del to prevent "BufferError: cannot close exported pointers exist"
        del shmbuf, sem1, sem2
        # Unlink the shared memory object.
        # Even if the peer process is still using the object, this is okay.
        # The object will be removed only after all open references are closed.
        buf.unlink()


if __name__ == "__main__":
    main()
