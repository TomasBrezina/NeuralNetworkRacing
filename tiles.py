import numpy as np
from PIL import Image
from PIL.Image import ROTATE_90, ROTATE_180, ROTATE_270, FLIP_TOP_BOTTOM, FLIP_LEFT_RIGHT
import os
import pyglet
from core import Track

"""
LARGE_SIZE GRID
-- 12 --
01    21
-- 10 --
"""
LARGE_SIZE = 768
LARGE_DIM = 1

LARGE_GRID_SHIT = 5

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



class Tile:

    def __init__(self, arr, inp, out, image=None):
        self.inp = inp  # (x, y)
        self.out = out  # (x, y)
        self.arr = arr  # (left / right, n, x / y)
        self.image = image

    def inp_out_to_ndarray(self):
        return np.array([[self.inp, self.out]])

    def __str__(self):
        return "".join(str(char) for itr in (self.inp, self.out) for char in itr)


class TileManager:
    """
    00 10 20 30 40
    01 11 21 31 41
    02 12 22 32 42
    04 14 24 34 44
    03 13 23 33 43
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
                # 0 1 2 3 4
                # b       5
                # a 9 8 7 6
                [[0,0], [1,0], [2,0], [3,0], [4,0], [4,1], [4,2], [3,2], [2,2], [1,2], [0,2], [0,1]],
                # 0 1 2 3 4
                # d a 9 8 5
                # c b   7 6
                [[0,0], [1,0], [2,0], [3,0], [4,0], [4,1], [4,2], [3,2], [3,1], [2,1], [1,1], [1,2], [0,2], [0,1]],
                # 0 1 2 3 4
                # b a 9 8 5
                #       7 6
                [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0], [4, 1], [4, 2], [3, 2], [3, 1], [2, 1], [1, 1], [0, 1]]
            ]
        }

    def generate_track_from_medium_path(self, medium_path, shape=(5, 3), spawn_index=0):
        tile_grid = self.generate_tile_grid_from_medium_path(shape, medium_path)
        return self.generate_track(tile_grid, shape, spawn_index)

    def auto_generate_track(self, shape=(5, 3), spawn_index=0):
        tile_grid = self.generate_tile_grid(shape)
        return self.generate_track(tile_grid, shape, spawn_index)

    def generate_track(self, tile_grid, shape=(5, 3), spawn_index=0):
        nodes = np.array([])

        """image = pyglet.image.Texture.create(
            shape[0] * LARGE_SIZE,
            shape[1] * LARGE_SIZE,
            force_rectangle=True
        )"""
        size_x, size_y = shape[0] * LARGE_SIZE, shape[1] * LARGE_SIZE
        image = Image.new('RGBA', (
            size_x, size_y
        ))

        for grid_pos, tile in tile_grid:
            grid_pos = grid_pos + 1

            nodes = self.add_tile_to_arr(nodes, grid_pos, tile)
            # paste tiles to image - reverse y axis
            image.paste(tile.image, (grid_pos[0] * LARGE_SIZE, (shape[1] - grid_pos[1] - 1) * LARGE_SIZE))
            #image.blit_into(tile.image, grid_pos[0] * LARGE_SIZE, grid_pos[1] * LARGE_SIZE, 0)

        # convert PIL image to pyglet image from bytes
        image = image.transpose(FLIP_TOP_BOTTOM)
        pyglet_image = pyglet.image.ImageData(size_x, size_y, 'RGBA', image.tobytes())
        return Track(
            shape=shape,
            nodes=nodes,
            spawn_index=spawn_index,
            bg=pyglet_image
        )

    def _grid_to_path(self, grid_coords):
        # path of grid coordinates to direction path
        path = []
        first = grid_coords[0]
        prev = first
        for ind in range(1, len(grid_coords)):
            now = grid_coords[ind]
            path.append([1 + (now[0] - prev[0]), 1 - (now[1] - prev[1])])
            prev = now
        path.append([1 + (first[0] - prev[0]), 1 - (first[1] - prev[1])])
        return path

    def get_random_grid_path(self, shape):
        # choose one of defined grid paths
        return self.GRID_PATHS[shape][np.random.randint(len(self.GRID_PATHS[shape]))]

    def generate_tile_grid(self, shape=(5, 3)):
        """Generate array of track nodes."""
        return self.generate_tile_grid_from_large_path(shape, self._grid_to_path(self.get_random_grid_path(shape)))

    def generate_tile_grid_from_large_path(self, shape, out_path, inp_start=None):
        """
        path of LARGE_DIM grid coordinates (0-2, 0-2) - 4 sides
        -- 12 --
        01    21
        -- 10 --
        """
        if inp_start is None:
            inp_start = GRID_OUT_TO_INP(out_path[-1], size=3)
        def l_to_m(c):
            if c[0] == 1:
                return [np.random.randint(1,4), 4 if c[1] == 0 else 0]
            if c[1] == 1:
                return [0 if c[0] == 0 else 4, np.random.randint(1, 4)]
        m_path = []
        first = l_to_m(inp_start)
        m_inp = first
        for out in out_path:
            m_out = l_to_m(out)
            # input, output coords, tile index
            m_path.append([m_inp, m_out])
            m_inp = GRID_OUT_TO_INP(m_out, size=MEDIUM_DIM)
        m_path[-1][1] = GRID_OUT_TO_INP(first, size=MEDIUM_DIM)
        return self.generate_tile_grid_from_medium_path(shape, m_path)

    def generate_tile_grid_from_medium_path(self, shape, path):
        """
        input: path of MEDIUM_DIM grid coordinates (0-4, 0-4) - 12 points
        -- 14 24 34 --
        03          43
        02          42
        01          41
        -- 10 20 30 --
        output: array of [coordinates in a grid, tile]
        """
        tile_grid = []
        grid_pos = np.array([0, 0])
        for values in path:
            inp, out = values[0], values[1]
            index = values[2] if len(values) >= 3 else 0
            tile = self.tiles[COORDS_TO_STR(inp) + COORDS_TO_STR(out)][index]
            tile_grid.append((grid_pos.copy(), tile))
            grid_pos += GRID_SHIFT(out, size=MEDIUM_DIM)
        return tile_grid

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
        tiles = []
        dirs = os.scandir(root_dir) if root_dir else os.scandir()
        for dir in dirs:
            if os.path.isdir(dir):
                files = os.scandir(dir)

                is_tile = False
                arr, inp, out, num, img = None, None, None, None, None
                for file in files:
                    name = os.path.basename(file)[:-4]
                    ext = os.path.splitext(file)[-1].lower()
                    if ext == ".csv":
                        is_tile = True
                        arr = load_track(file)
                        # YX_YX_N ??
                        # "00_00_0" --> [0, 0] [0, 0] [0]
                        inp, out, num = map(lambda n: [int(s) for s in n], name.split("_"))
                    if ext == ".png":
                        #img = pyglet.image.load(os.path.abspath(file)).get_texture(rectangle=True)
                        img = Image.open(os.path.abspath(file))
                if is_tile:
                    try:
                        print(f"{os.path.basename(dir)} {img}")
                        tiles.append(Tile(arr, inp, out, image=img))
                    except:
                        print(f"Error loading {os.path.basename(dir)}")

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
        img = self._rot_img(tile.image, n)
        return Tile(arr=arr, inp=inp, out=out, image=img)

    def flip_tile(self, tile):
        arr = self._flip_3d_arr(tile.arr, LARGE_SIZE)
        inp = self._flip_1d_arr(tile.inp, MEDIUM_DIM)
        out = self._flip_1d_arr(tile.out, MEDIUM_DIM)
        img = self._flip_img(tile.image)
        return Tile(arr=arr, inp=inp, out=out, image=img)

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

    def _rot_img(self, img, n):
        return img.rotate(n * -90)
        # return img.get_transform(rotate=n * 90)

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

    def _flip_img(self, img):
        return img.transpose(FLIP_TOP_BOTTOM)
        # return img.get_transform(flip_x=True).get_texture(rectangle=True)

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