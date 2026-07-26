import random
import string
import pytest

import treqna


def generate_random_bytes(length: int = 100) -> bytes:
    return bytes(random.getrandbits(8) for _ in range(length))


def generate_random_string(length: int = 100) -> str:
    return "".join(random.choices(string.printable, k=length))


def test_fuzzing_10000_inputs() -> None:
    random.seed(1337)
    formats = ("csv", "json", "yaml", "xml")

    for i in range(10000):
        if i % 2 == 0:
            payload: str | bytes = generate_random_string(random.randint(5, 200))
        else:
            payload = generate_random_bytes(random.randint(5, 200))

        det_res = treqna.detect(payload)
        assert isinstance(det_res.success, bool)

        insp_res = treqna.inspect(payload)
        assert isinstance(insp_res.success, bool)

        val_res = treqna.validate(payload)
        assert isinstance(val_res.success, bool)

        target_fmt = formats[i % len(formats)]
        res = treqna.transform(payload).to(target_fmt).execute()
        assert isinstance(res.success, bool)

