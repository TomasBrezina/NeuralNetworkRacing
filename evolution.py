from neural_network import NeuralNetwork
from core import index_loop
from os import listdir
import json
from objects import Result

"""
Class containing info about NNs and its parameters & generates new generations.
"""
class Evolution:
    def __init__(self):
        self.name = ""
        self.acceleration = 0
        self.max_speed = 0
        self.rotation_speed = 0
        self.shape = []

        self.gen_count = 0
        self.max_score = 0

        self.best_result = Result(None, -1, 0)

        self.mutation_rate = 0

    def get_first_generation(self, population):
        nn = NeuralNetwork(self.shape)
        nn.set_random_weights()
        return self.get_new_generation([nn], population)

    def load_generation(self, nn: NeuralNetwork, nn_stg: dict, population: int):

        return self.get_new_generation([nn], population)

    def get_new_generation(self, nns, population):
        self.gen_count += 1
        return [nns[index_loop(i, len(nns))].reproduce(self.mutation_rate) for i in range(population)]

    def get_new_generation_from_results(self, results, population):
        self.find_best_nn(results)
        best_nns = []
        # order by cp_score - if equal than dist_to_next_cp
        # sorted_results = sorted(results, key=lambda x: (x[1], -x[2]), reverse=True)
        sorted_results = sorted(results, reverse=True)

        # add best 8
        to_add = 2 if len(sorted_results) >= 2 else len(sorted_results)
        for i in range(to_add):
            best_nns.append(sorted_results[i].nn)

        return self.get_new_generation(best_nns, population)

    def find_best_nn(self, results):
        # best cp_score - if equal than better dist_to_next_cp
        result = max(results)
        if self.best_result < result:
            self.best_result = result
            if self.max_score < self.best_result.score:
                self.max_score = self.best_result.score
        """nn, score, dist_to_next_cp = max(results, key=lambda x: (x[1], -x[2]))
        if (score > self.max_score) or (score == self.max_score and dist_to_next_cp < 1) :
            self.max_score = score
            self.best_nn = dist_to_next_cp"""

    def get_car_parameters(self):
        return {
            "acceleration": self.acceleration,
            "max_speed": self.max_speed,
            "rotation_speed": self.rotation_speed,
        }

    def get_save_parameters(self):
        return {
            "name" : self.name,
            "acceleration": self.acceleration,
            "max_speed": self.max_speed,
            "rotation_speed": self.rotation_speed,
            "shape": self.shape,
            "max_score": self.max_score,
            "gen_count": self.gen_count
        }

    def set_parameters_from_dict(self, par: dict):
        # get from dict, if not in set default
        self.name = par.get("name", self.name)
        self.acceleration = par.get("acceleration", self.acceleration)
        self.max_speed = par.get("max_speed", self.max_speed)
        self.rotation_speed = par.get("rotation_speed", self.rotation_speed)
        self.shape = par.get("shape", self.shape)

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

        save_file = {
            "settings": self.get_save_parameters(),
            "weights": [np_arr.tolist() for np_arr in self.best_result.nn.weights]
        }
        with open(folder + "/" + save_name, "w") as json_file:
            json.dump(save_file, json_file)
        print("Saved ", save_name)

    def load_file(self, path):
        try:
            with open(path) as json_file:
                file = json.load(json_file)
            self.set_parameters_from_dict(file)
            print(f"Loaded {path}")
        except:
            print(f"Failed to load: {path}")
            return False





