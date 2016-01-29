import pickle
from random import randint

"""
Handle the generate of collatz tests. Since we don't want to include the
algorithm here, load a pickle file with all the sequence counts to generate
the tests.
"""
class Collatz:
    data_file = 'data.pickle'

    def __init__(self):
        with open(self.data_file, 'rb') as f:
            self.data = pickle.load(f)

    """
    Generate a set of tests, which includes 100 individual tests, as well as
    their answers
    """
    def generate_tests(self):
        test_in = test_out = ""
        for i in range(1, 100):
            i, j, ans = self.generate_test()
            tmp = str(i) + " " + str(j)
            test_in += tmp + "\n"
            test_out += tmp + " " + str(ans) + "\n"

        return (test_in, test_out)

    """
    Generate a single test, returning the start and stop of a range, and the
    max cycle of that range
    """
    def generate_test(self):
        start = randint(1, 999999)
        stop = randint(1, 999999)

        i, j = (start, stop) if stop > start else (stop, start)

        max = 0
        for i in range(i, j):
            max = self.data[i] if self.data[i] > max else max

        return (start, stop, max)
