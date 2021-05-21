import numpy as np
from PIL import Image
from PIL.Image import ROTATE_90, ROTATE_180, ROTATE_270, FLIP_TOP_BOTTOM, FLIP_LEFT_RIGHT
import os
import pyglet

"""
LARGE_SIZE GRID
-- 12 --
01    21
-- 10 --
"""
LARGE_SIZE = 768
LARGE_DIM = 1

"""
MEDIUM_SIZE GRID
-- 14 24 34 --
03          43
02          42
01          41
-- 10 20 30 --
"""
MEDIUM_SIZE = LARGE_SIZE / 3
MEDIUM_DIM = 5

SMALL_SIZE = MEDIUM_SIZE / 8


def SEG_TO_COORDS(segment):
    x, y = segment
    arr = np.array([[],[]])
    if x == 0:
        arr = [[[0, ((y - 1) * MEDIUM_SIZE) + SMALL_SIZE]], [[0, (y * MEDIUM_SIZE) - SMALL_SIZE]]]
    elif x == 4:
        arr = [[[LARGE_SIZE, (y * MEDIUM_SIZE) - SMALL_SIZE]], [[LARGE_SIZE, ((y - 1) * MEDIUM_SIZE) + SMALL_SIZE]]]
    elif y == 0:
        arr = [[[(x * MEDIUM_SIZE) - SMALL_SIZE, 0]], [[((x - 1) * MEDIUM_SIZE) + SMALL_SIZE, 0]]]
    elif y == 4:
        arr = [[[((x - 1) * MEDIUM_SIZE) + SMALL_SIZE, LARGE_SIZE]], [[(x * MEDIUM_SIZE) - SMALL_SIZE, LARGE_SIZE]]]
    return np.array(arr)

def COORDS_TO_STR(coords):
    """
    :param coords: (x, y) array
    :return: "XY" string
    """
    return "".join([str(n) for n in coords])

def GRID_OUT_TO_INP(out, size=5):
    max_val = size - 1
    inp = out.copy()
    if out[0] == 0:
        inp[0] = max_val
    elif out[0] == max_val:
        inp[0] = 0
    elif out[1] == 0:
        inp[1] = max_val
    elif out[1] == max_val:
        inp[1] = 0
    return inp

def GRID_SHIFT(out, size=5):
    shift = np.array([0, 0])
    if out[0] == 0:
        shift[0] = -1
    elif out[0] == size - 1:
        shift[0] = 1
    elif out[1] == 0:
        shift[1] = -1
    elif out[1] == size - 1:
        shift[1] = 1
    return shift

# load track from a folder
def load_track(directory):
    # raw shape = (n, left/right, x/y)
    # [[[xl1,yl1],[xr1,yr1]],
    #  [[xl2,yl2],[xr2,yr2]], ...]
    raw = np.loadtxt(directory, delimiter=",")
    raw = np.atleast_2d(raw)
    raw = raw.reshape((raw.shape[0], 2, 2))
    # shaped shape = (left/right, n, x/y)
    # [[[xl1,yl1],[xl2,yl2]],
    #  [[xr1,yr1],[xr2,yr2]], ...]
    shaped = np.empty((2, raw.shape[0], 2))
    shaped[0,:] = raw[:,0]
    shaped[1,:] = raw[:,1]
    return shaped

def index_loop(ind, len):
    while ind >= len:
        ind -= len
    return ind

class Track:

    def __init__(self, nodes, stg, bg=False):
        self.nodes = nodes
        self.vertex_list = (
            pyglet.graphics.vertex_list(len(self.nodes[0]), ('v2i', (self.nodes[0].flatten()).astype(int))),
            pyglet.graphics.vertex_list(len(self.nodes[1]), ('v2i', (self.nodes[1].flatten()).astype(int)))
        )
        self.bg = bg

        # (n, left/right, prev/next, x/y)
        self.lines_arr = self.nodes_to_lines(nodes)
        self.cps_arr = self.nodes_to_cps(nodes)
        self.stg = stg

    def nodes_to_lines(self, nodes):
        """
        :param nodes: shape (left/right, n, x/y)
        :return: lines: shape (n, left/right, prev/next, x/y)
        """
        lines = np.swapaxes(np.stack((nodes, np.roll(nodes, -1, 1)), axis=2), 0, 1)
        return lines

    def nodes_to_cps(self, nodes):
        """
        :param nodes: shape (left/right, n, x/y)
        :return: cps: point in the center with shape (n, xy)
        """
        center_point = lambda gate: [(gate[0,0] + gate[1,0]) // 2, (gate[0,1] + gate[1,1]) // 2]
        return np.array([center_point(nodes[:,i,:]) for i in range(nodes.shape[1])])

    def change_scale(self, scale):
        for i in range(len(self.vertex_list)):
            self.vertex_list[i].vertices = (self.nodes[i].flatten() * scale).astype(int)
        if self.bg: self.bg.scale = scale


class Tile:

    def __init__(self, arr, inp, out):
        self.inp = inp  # (x, y)
        self.out = out  # (x, y)
        self.arr = arr  # (left / right, n, x / y)

    def inp_out_to_ndarray(self):
        return np.array([[self.inp, self.out]])

    def __str__(self):
        return "".join(str(char) for itr in (self.inp, self.out) for char in itr)


class TileManager:
    """
    03 13 23 33
    02 12 22 32
    01 11 21 31
    00 10 20 30
    """
    def __init__(self, shape=5):
        self.shape = shape
        self.tiles = {}
        self.GRID_PATHS = {
            (3, 2): [
                [[0,0], [1,0], [2,0], [2,1], [1,1], [0,1]]
            ],
            (4, 3): [
                [[0,0],[1,0],[2,0],[3,0],[3,1],[3,2],[2,2],[2,1],[1,1],[1,2],[0,2],[0,1]],
                [[0,0],[1,0],[2,0],[3,0],[3,1],[3,2],[2,2],[1,2],[0,2],[0,1]]
            ],
            (5, 3): [
                [[0,0], [1,0], [2,0], [3,0], [4,0], [4,1], [4,2], [3,2], [2,2], [1,2], [0,2], [0,1]]
            ]
        }

    def generate_random(self, shape=(4,3)):
        """Not working"""
        graph = self._grid_graph(shape=shape)
        # edge path
        path = [(s, 0) for s in range(shape[0])] + [(shape[0]-1, s) for s in range(1, shape[1] - 1)] + \
               [(s, shape[1] - 1) for s in range(shape[0] - 1, 0, -1)] + [(0, s) for s in range(shape[1] - 1, 0, -1)]
        for node in path:
            graph[node][1] = True

    def _grid_graph(self, shape=(3,2)):
        """Creates a 2D square lattice graph."""
        graph = {}
        for i in range(shape[0]):
            for j in range(shape[1]):
                graph[(i, j)] = [[], False]
                for si, sj in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
                    ti, tj = i + si, j + sj
                    if (0 <= ti < shape[0]) and (0 <= tj < shape[1]):
                        graph[(i, j)][0].append((ti, tj))
        return graph

    def _find_path(self, graph, start, end, path=[]):
        path = path + [start]
        if start == end:
            return path
        if start not in graph:
            return None
        for node in graph[start][0]:
            if node not in path and not graph[start][1]:
                newpath = self._find_path(graph, node, end, path)
                if newpath: return newpath
        return None

    def _grip_to_path(self, grid_coords):
        # path of grid coordinates to tile path
        path = []
        first = grid_coords[0]
        prev = first
        for ind in range(1, len(grid_coords)):
            now = grid_coords[ind]
            path.append([1 + (now[0] - prev[0]), 1 - (now[1] - prev[1])])
            prev = now
        path.append([1 + (first[0] - prev[0]), 1 - (first[1] - prev[1])])
        return path

    def generate(self, shape=(5, 3)):
        return self.generate_from_large_path(self._grip_to_path(self.GRID_PATHS[shape][0]))

    def generate_from_large_path(self, out_path, inp_start=None):
        """
        path of LARGE_DIM grid coordinates (0-2, 0-2) - 4 sides
        -- 10 --
        01    21
        -- 12 --
        """
        if inp_start is None:
            inp_start = GRID_OUT_TO_INP(out_path[-1], size=3)
        def l_to_m(c):
            if c[0] == 1:
                return [np.random.randint(1,4), 0 if c[1] == 0 else 4]
            if c[1] == 1:
                return [0 if c[0] == 0 else 4, np.random.randint(1, 4)]
        m_path = []
        first = l_to_m(inp_start)
        m_inp = first
        for out in out_path:
            m_out = l_to_m(out)
            m_path.append([m_inp, m_out])
            m_inp = GRID_OUT_TO_INP(m_out, size=MEDIUM_DIM)
        m_path[-1][1] = GRID_OUT_TO_INP(first, size=MEDIUM_DIM)
        return self.generate_from_medium_path(m_path)

    def generate_from_medium_path(self, path):
        """
        path of MEDIUM_DIM grid coordinates (0-4, 0-4) - 12 points
        -- 14 24 34 --
        03          43
        02          42
        01          41
        -- 10 20 30 --
        """
        nodes = np.array([])
        grid_pos = np.array([0, 0])
        for inp, out in path:
            tile = self.tiles[COORDS_TO_STR(inp) + COORDS_TO_STR(out)][0]
            nodes = self.add_tile_to_arr(nodes, grid_pos, tile)
            grid_pos += GRID_SHIFT(out, size=MEDIUM_DIM)
        return nodes

    def add_tile_to_arr(self, arr, grid_pos, tile):
        con_arr = tile.arr.copy()
        con_arr[:,:,0] += (grid_pos[0] * LARGE_SIZE)
        con_arr[:,:,1] += (grid_pos[1] * LARGE_SIZE)
        if not arr.size > 0: return con_arr
        return np.concatenate((arr, con_arr), axis=1)

    def load_tiles(self, root_dir=None):
        """
        root_dir
        └── tile_dir (INP_OUT_N)
            ├── tile.csv
            ├── tile.png
            └── tile.svg
        """
        print(root_dir)
        tiles = []
        dirs = os.scandir(root_dir) if root_dir else os.scandir()
        for dir in dirs:
            if os.path.isdir(dir):
                files = os.scandir(dir)
                for file in files:
                    name = os.path.basename(file)[:-4]
                    ext = os.path.splitext(file)[-1].lower()
                    if ext == ".csv":
                        arr = load_track(file)
                        # YX_YX_N ??
                        # "00_00_0" --> [0, 0] [0, 0] [0]
                        inp, out, num = map(lambda n: [int(s) for s in n], name.split("_"))
                        tiles.append(Tile(arr, inp, out))
        self.tiles = self.variate_tiles(tiles)
        return tiles

    def variate_tiles(self, def_tiles):
        # rotate and flip tiles - all possibilities
        tiles = {}
        for def_tile in def_tiles:
            for tile in (def_tile, self.flip_tile(def_tile)):
                for rot in range(4):
                    new_tile = self.rot_tile(tile, rot)
                    tiles.setdefault(str(new_tile), []).append(new_tile)
        return tiles

    def draw_track(self, arr):
        import matplotlib.pyplot as plt
        plt.gca().invert_yaxis()
        plt.plot(arr[0, :, 0], arr[0, :, 1])
        plt.plot(arr[1, :, 0], arr[1, :, 1])
        plt.show()

    def draw_tile(self, tile):
        import matplotlib.pyplot as plt
        plt.gca().invert_yaxis()
        plt.scatter([0,768], [0,768]) # corners
        arr = np.concatenate((tile.arr, SEG_TO_COORDS(tile.out)), axis=1)
        plt.plot(arr[0,:,0], arr[0,:,1])
        plt.plot(arr[1,:,0], arr[1,:,1])
        plt.show()

    def rot_tile(self, tile, n):
        arr = self._rot_3d_arr(tile.arr, n, LARGE_SIZE)
        inp = self._rot_1d_arr(tile.inp, n, MEDIUM_DIM)
        out = self._rot_1d_arr(tile.out, n, MEDIUM_DIM)
        return Tile(arr=arr, inp=inp, out=out)

    def flip_tile(self, tile):
        arr = self._flip_3d_arr(tile.arr, LARGE_SIZE)
        inp = self._flip_1d_arr(tile.inp, MEDIUM_DIM)
        out = self._flip_1d_arr(tile.out, MEDIUM_DIM)
        return Tile(arr=arr, inp=inp, out=out)

    def _rot_3d_arr(self, arr, n, max_dim = 5):
        # rot 90 deg * n
        _arr = np.copy(arr)
        for _ in range(n):
            for row in _arr:
                for coor in row:
                    coor[0], coor[1] = coor[1], max_dim - coor[0] - 1
        return _arr

    def _rot_1d_arr(self, coor, n, max_dim = 5):
        _coor = np.copy(coor)
        for _ in range(n):
            _coor[0], _coor[1] = _coor[1], max_dim - _coor[0] - 1
        return _coor

    def _flip_3d_arr(self, arr, max_dim = 5):
        # flip on y axis
        _arr = np.copy(arr)
        _shape = np.full(arr[:, :, 1].shape, max_dim)
        _arr[:, :, 1] = (_shape - arr[:, :, 1]) - 1
        _arr[[0,1]] = _arr[[1,0]] # swap left and right
        return _arr

    def _flip_1d_arr(self, arr, max_dim = 5):
        # flip on y axis
        _arr = np.array([arr[0], max_dim - arr[1] - 1])
        return _arr

    def edit_image(self, img, rot=0, flip=0):
        img.transpose([ROTATE_90, ROTATE_180, ROTATE_270][rot])
        return img


"""
dirs = os.scandir("NOT YET")
for dir in dirs:
    if os.path.isdir(dir):
        name = os.path.basename(dir)
        try:
            if os.path.isdir(dir):
                inp, out, num = name.split("_")
                inp = inp[0] + str(4 - int(inp[1]))
                out = out[0] + str(4 - int(out[1]))
                new_name = f"{inp}_{out}_{num}"
                files = os.scandir(dir)
                for file in files:
                    file_path = "NOT YET/" + name+"/"+os.path.basename(file)
                    ext = os.path.splitext(file)[-1].lower()
                    #os.rename(file_path, "NOT YET/" + name + "/" + new_name + ext)
                os.rename("NOT YET/" + name, "NOT YET/" + new_name)
        except:
            print(name)"""