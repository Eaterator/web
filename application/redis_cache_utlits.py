from flask import request
from functools import reduce
import string
import re
import functools


def _primes_to(n):
    return reduce(
        (lambda r, x: r - set(range(x**2, n, x)) if (x in r) else r), range(2, n), set(range(2, n))
    )


## get primes to 105 to get 26 (len alphabet + '&' symbol)
PRIMES_MAP = {ord(char): prime for char, prime in zip(string.ascii_lowercase + '&', _primes_to(105))}
PRIMES_MAP[ord('s')] = 0
INTERNAL_INGREDIENT_SPACE_PATTERN = re.compile(r'\s+|\-')


def _clean_and_stringify_ingredients_query(ingredients):
    return list(map(lambda s: re.sub(INTERNAL_INGREDIENT_SPACE_PATTERN, '&', s.strip().lower()), ingredients))


class RedisUtilities:

    @staticmethod
    def make_search_cache_key(*args, **kwargs):
        payload = request.get_json()
        ingredients = ''.join(_clean_and_stringify_ingredients_query(payload["ingredients"]))
        return str(sum(PRIMES_MAP[ord(char)] for char in ingredients))

    @staticmethod
    def cache_by_static_page(*args, **kwargs):
        return request.path.split('/')[-1]
