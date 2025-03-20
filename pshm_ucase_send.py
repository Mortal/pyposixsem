#!/usr/bin/env python3
# Licensed under GNU General Public License v2 or later.
# Ported from pshm_ucase_send.c from shm_open(3) in Linux man-pages 6.13.
"""
The "send" program takes two command-line arguments:
the pathname of a shared memory object previously created by the "bounce" program
and a string that is to be copied into that object.

The program opens the shared memory object and maps the object into its address space.
It then copies the data specified in its second argument into the shared memory,
and posts the first semaphore, which tells the "bounce" program that it can now access that data.
After the "bounce" program posts the second semaphore,
the "send" program prints the contents of the shared memory on standard output.
"""

import argparse
import multiprocessing.shared_memory

import pshm_ucase
import pyposixsem


parser = argparse.ArgumentParser()
parser.add_argument("shmpath")
parser.add_argument("string")


def main() -> None:
    args = parser.parse_args()
    s = args.string.encode()
    if len(s) > pshm_ucase.BUF_SIZE:
        raise SystemExit("String is too long")

    # Open the existing shared memory object and map it into the caller's address space.
    buf = multiprocessing.shared_memory.SharedMemory(args.shmpath, track=False)
    try:
        # Access the shared memory through the Shmbuf type.
        shmbuf = pshm_ucase.Shmbuf.from_buffer(buf.buf)

        # Copy data into the shared memory object.
        shmbuf.cnt = len(s)
        shmbuf.buf = s

        # Tell peer that it can now access shared memory.
        sem1 = pyposixsem.SharedSemaphore(shmbuf.sem1)
        sem1.post()

        # Wait until peer says that it has finished accessing the shared memory.
        sem2 = pyposixsem.SharedSemaphore(shmbuf.sem2)
        sem2.wait()

        # Write modified data in shared memory to standard output.
        print(shmbuf.buf[: len(s)].decode())
    finally:
        # del shmbuf to prevent "BufferError: cannot close exported pointers exist"
        del shmbuf, sem1, sem2


if __name__ == "__main__":
    main()
