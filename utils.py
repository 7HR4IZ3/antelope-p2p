import time
from os import urandom

def nanoseconds():
    load_ns = time.time_ns()
    load_ms = int(time.time() * 1000)
    diff_ns = time.time_ns() - load_ns
    return (load_ms * 10**6) + diff_ns


def random_bytes(length):
  """
  Generates a bytearray of the specified length filled with random bytes.

  Args:
      length: The desired length of the bytearray.

  Returns:
      A bytearray of the specified length filled with random bytes.
  """
  return bytearray(urandom(length))
