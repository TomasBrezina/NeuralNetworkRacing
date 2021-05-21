from neural_network import NeuralNetwork
from core import index_loop
from os import listdir
import json

def get_evolution_from_dict(nn_stg, mutation_rate):

        return Evolution(
            name=nn_stg["name"],
            acceleration=nn_stg["acceleration"],
            max_speed=nn_stg["max_speed"],
            rotation_speed=nn_stg["rotation_speed"],
            shape=nn_stg["shape"],
            mutation_rate=mutation_rate
        )

"""
Class containing info about NNs and its parameters & generates new generations.
"""
class Evolution:
    def __init__(
        self,
        name = "NN",
        acceleration = 3.5,
        max_speed = 35,
        rotation_speed = 3.5,
        shape = [5, 4, 3, 2],

        mutation_rate = 0.15,
    ):
        self.name = name
        self.acceleration = acceleration
        self.max_speed = max_speed
        self.rotation_speed = rotation_speed
        self.shape = shape

        self.gen_count = 0
        self.max_score = 0
        self.recent_max_score = 0
        self.best_nn = None  # nn to save

        self.mutation_rate = mutation_rate

    def get_first_generation(self, population):
        nn = NeuralNetwork(self.shape)
        nn.set_random_weights()
        return self.get_new_generation([nn], population)

    def load_generation(self, nn, population):
        return self.get_new_generation([nn],population)

    def get_new_generation(self, nns, population):
        return [nns[index_loop(i, len(nns))].reproduce(self.mutation_rate) for i in range(population)]

    def get_new_generation_from_results(self, results, population):
        best_nns = []

        # order by cp_score - if equal than dist_to_next_cp
        sorted_results = sorted(results, key=lambda x: (x[1], -x[2]), reverse=True)

        # add best 8
        to_add = 2 if len(sorted_results) >= 2 else len(sorted_results)
        for i in range(to_add):
            best_nns.append(sorted_results[i][0])

        return self.get_new_generation(best_nns, population)

    def get_car_parameters(self):
        return {
            "acceleration": self.acceleration,
            "max_speed": self.max_speed,
            "rotation_speed": self.rotation_speed,
        }

    def get_save_parameters(self):
        return {
            "acceleration": self.acceleration,
            "max_speed": self.max_speed,
            "rotation_speed": self.rotation_speed,
            "shape": self.shape,
            "max_score": self.max_score,
            "gen_count": self.gen_count
        }

    def save_file(self, folder="saves"):
        # get name
        files = listdir(folder)
        save_name = self.name
        name_count = 0
        while save_name + ".json" in files:
            name_count += 1
            save_name = "%s(%s)" % (self.name, name_count)
        save_file = {
            "settings": self.get_save_parameters(),
            "weights": [np_arr.tolist() for np_arr in self.best_nn.weights]
        }
        with open(folder + "/" + save_name + ".json", "w") as json_file:
            json.dump(save_file, json_file)
        print("Saved ", save_name)





