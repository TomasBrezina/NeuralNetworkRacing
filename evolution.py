from neural_network import NeuralNetwork
from core import index_loop
from os import listdir
import json
from objects import Result

class Entity:
    """
    Neural network entity with name, settings, neural network, ...
    Savable and loadable.
    """

    def __init__(self):
        # parameters
        self.name = ""
        self.acceleration = 0
        self.max_speed = 0
        self.rotation_speed = 0
        self.friction = 0

        self.shape = []

        # info
        self.gen_count = 0
        self.max_score = 0

        # result with nn to save
        self.nn = None

    # Add 1 to gen count
    def increment_gen_count(self):
        self.gen_count += 1

    # Get nn from Result object
    def get_nn(self):
        return self.nn

    def set_nn(self, nn):
        self.nn = nn

    # Get nn with random weights with this shape
    def get_random_nn(self):
        nn = NeuralNetwork(self.shape)
        nn.set_random_weights()
        return nn

    # set new result and max score
    def set_nn_from_result(self, result: Result):
        self.nn = result.nn
        self.max_score = result.score

    def get_car_parameters(self):
        return {
            "acceleration": self.acceleration,
            "max_speed": self.max_speed,
            "rotation_speed": self.rotation_speed,
            "friction": self.friction
        }

    def get_save_parameters(self):
        return {
            "name" : self.name,
            "acceleration": self.acceleration,
            "max_speed": self.max_speed,
            "rotation_speed": self.rotation_speed,
            "shape": self.shape,
            "max_score": self.max_score,
            "gen_count": self.gen_count,
            "friction": self.friction
        }

    def set_parameters_from_dict(self, par: dict):
        # get from dict, if not in set default
        self.name = par.get("name", self.name)

        self.acceleration = par.get("acceleration", self.acceleration)
        self.max_speed = par.get("max_speed", self.max_speed)
        self.rotation_speed = par.get("rotation_speed", self.rotation_speed)
        self.shape = par.get("shape", self.shape)
        self.friction = par.get("friction", self.friction)

        self.gen_count = par.get("gen_count", self.gen_count)
        self.max_score = par.get("max_score", self.max_score)

    def save_file(self, save_name="", folder="saves"):
        # if dir already contains that name
        """
        files = listdir(folder)
        name_count = 0
        while save_name + ".json" in files:
            name_count += 1
            save_name = "%s(%s)" % (self.name, name_count)"""
        if not save_name.endswith(".json"):
            save_name += ".json"
        save_file = {
            "settings": self.get_save_parameters(),
            "weights": [np_arr.tolist() for np_arr in self.nn.weights]
        }
        with open(folder + "/" + save_name, "w") as json_file:
            json.dump(save_file, json_file)
        print("Saved ", save_name)

    def load_file(self, path):
        #try:
        with open(path) as json_file:
            file_raw = json.load(json_file)

        file_parameters = file_raw["settings"]
        file_weights = file_raw["weights"]

        self.nn = NeuralNetwork(file_parameters["shape"])
        self.nn.set_weights(file_weights)
        self.set_parameters_from_dict(file_parameters)

        print(f"Loaded {path}")
        """except:
            print(f"Failed to load: {path}")
            return False"""

"""
Class containing info about NNs and its parameters & generates new generations.
"""
class Evolution:
    def __init__(self):
        self.best_result = Result(None, -1, 0)
        self.mutation_rate = 0

    def load_generation(self, nn: NeuralNetwork, nn_stg: dict, population: int):
        return self.get_new_generation([nn], population)

    def get_new_generation(self, nns: [NeuralNetwork], population: int):
        return [nns[index_loop(i, len(nns))].reproduce(self.mutation_rate) for i in range(population)]

    def get_new_generation_from_results(self, results: [Result], population: int, to_add_count=3):
        best_nns = []
        # order by cp_score - if equal than dist_to_next_cp
        # sorted_results = sorted(results, key=lambda x: (x[1], -x[2]), reverse=True)
        sorted_results = sorted(results, reverse=True)

        # add best X
        to_add = to_add_count if len(sorted_results) >= to_add_count else len(sorted_results)
        for i in range(to_add):
            best_nns.append(sorted_results[i].nn)

        return self.get_new_generation(best_nns, population)

    def find_best_result(self, results: [Result]):
        # best cp_score - if equal than better dist_to_next_cp
        current_best_result = max(results)
        self.best_result = current_best_result if current_best_result > self.best_result else self.best_result
        return self.best_result

        """nn, score, dist_to_next_cp = max(results, key=lambda x: (x[1], -x[2]))
        if (score > self.max_score) or (score == self.max_score and dist_to_next_cp < 1) :
            self.max_score = score
            self.best_nn = dist_to_next_cp"""

class CustomEvolution(Evolution):
    pass

from f1_tracks import get_drivers_init

class F1Evolution(Evolution):
    def __init__(self):
        self.best_result_count = len(get_drivers_init())
        self.best_results = [Result(None, -1, 0)] * self.best_result_count
        super(F1Evolution, self).__init__()

    def get_best_results(self, results):
        # merge new results and best results, sort them
        merged_results = sorted(self.best_results + results, reverse=True)
        # slice top n
        return merged_results[:self.best_result_count]

    def get_new_generation_from_results(self, results: [Result], population: int, to_add_count=3):
        best_nns = []
        self.best_results = self.get_best_results(results)
        print(self.best_results)

        for i in range(population):
            best_nns.append(self.best_results[index_loop(i, len(self.best_results))].nn)

        return self.get_new_generation(best_nns, population)


