from neural_network import NeuralNetwork

class Result:
    def __init__(self,
        nn : NeuralNetwork,
        score : int,
        dist_to_next_cp : float
    ):
        self.nn = nn
        self.score = score
        self.dist_to_next_cp = dist_to_next_cp

    def _cmp(self, other):
        if (self.score > other.score): return 1
        elif (self.score < other.score): return -1
        else:
            if (self.dist_to_next_cp > other.dist_to_next_cp): return 1
            elif (self.dist_to_next_cp < other.dist_to_next_cp): return -1
            else: return 0

    # Other comparators are unnecessary
    def __lt__(self, other): return self._cmp(other) == -1
    def __le__(self, other): return self._cmp(other) != 1
    def __eq__(self, other): return self._cmp(other) == 0
    def __ne__(self, other): return self._cmp(other) != 0
    def __gt__(self, other): return self._cmp(other) == 1
    def __ge__(self, other): return self._cmp(other) != -1