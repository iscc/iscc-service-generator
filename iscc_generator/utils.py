# -*- coding: utf-8 -*-
import random
import time


FLAKE_START_TIME = 1609459200
FLAKE_RANDOM_LENGTH = 23
FLAKE_RANDOM_SHIFT = 0
FLAKE_TIMESTAMP_SHIFT = 23


def make_flake() -> int:
    """
    See: https://instagram-engineering.tumblr.com/post/10853187575/sharding-ids-at-instagram
    """
    second_time = time.time()
    second_time -= FLAKE_START_TIME
    millisecond_time = int(second_time * 1000)
    randomness = random.SystemRandom().getrandbits(FLAKE_RANDOM_LENGTH)
    flake = (millisecond_time << FLAKE_TIMESTAMP_SHIFT) + randomness
    return flake
