from axon.util import partition


def test_partition():
    xs = [5, 4, 3, 2, 1]
    a, b = partition(lambda x: x < 3, xs)
    assert list(a) == [5, 4, 3]
    assert list(b) == [2, 1]
