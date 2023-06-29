import getFlags
import random

result = getFlags.get_flag()

choices = [
    random.randint(-1, min(256, len(opt) - 1))
    for opt in result
]

assert len(result) == len(choices)
assert all(
            -1 <= c < len(result[i]) for i, c in enumerate(choices)
        )

opts = [
        option[choice]
        for option, choice in zip(result, choices)
        if choice >= 0
]

print("opts = ",opts)

