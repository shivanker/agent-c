#! /usr/bin/python3

import logging as log
from memory.memory import Memory
import time
from itertools import accumulate

log.basicConfig(level=log.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class InPlaceMemory(Memory):
    def __init__(self, limiter_fn, sizer_fn):
        super().__init__(limiter_fn, sizer_fn)
        self.mem = {}

    def get(self, user):
        if user not in self.mem:
            return None
        return list(map(lambda x: x[1], self.mem[user]))

    def append(self, user, msg):
        if user not in self.mem:
            self.mem[user] = []
        msgs = self.mem[user]
        msgs.append((time.time(), msg))
        # Filter out stale / out of limit messages if needed
        n = len(msgs)
        ts, msgs = zip(*reversed(msgs))
        cum_sizes = accumulate(map(self.sizer, msgs))
        filtered = filter(
            lambda x: self.limiter(*x), zip(range(0, n), ts, cum_sizes, msgs)
        )
        self.mem[user] = list(map(lambda x: (x[1], x[3]), filtered))
        self.mem[user].reverse()

    def pop(self, user):
        return self.mem.pop(user)
