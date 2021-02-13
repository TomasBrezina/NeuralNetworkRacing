
class Evolution:
    def __init__(self):
        pass

    def new_generation(self, nn):
        pass

class MyEvolution(Evolution):
    def new_generation(self, nn, population):
        self.gen_count += 1
        self.cars = []
        for i in range(population):
            # name, loaded image
            name,image = images[index_loop(i, len(images))]
            sprite = pyglet.sprite.Sprite(image, batch=batch)
            # starting point is on cp (this is important, dont change it)
            pos = (*self.track.cps_arr[self.track.stg["spawnindex"]], self.track.stg["spawna"])
            # get mutated version of one of best NNs
            best_nn = best_nns[index_loop(i, len(best_nns))].reproduce(mutation_rate)
            self.cars.append(Car(best_nn, pos, self.save_stg, sprite))