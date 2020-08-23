import gd
import asyncio
import json
from PIL import Image

client = gd.Client()
COLLISION_FILENAME = "full_object_collisions.json"

class ObjectCollision:
    COLOR_KILL = (255, 0, 0)
    COLOR_WALL = (0, 0, 0)
    COLOR_DEFAULT = (255, 255, 255)
    PRIORITY_COLOR = {
        COLOR_DEFAULT : 0,
        COLOR_WALL : 1,
        COLOR_KILL : 2
    }
    with open("objects_with_collisions.json") as f:
        VALID_OBJECTS = json.load(f)
    def __init__(self, input):
        if type(input) is ObjectCollision:
            input_obj = input
            self.id = input_obj.id
            self.kills = input_obj.kills
            self.color = input_obj.color
            self.hitbox_type = input_obj.hitbox_type
            self.x1 = input_obj.x1
            self.x2 = input_obj.x2
            self.y1 = input_obj.y1
            self.y2 = input_obj.y2
        else:
            input_list = input
            assert len(input_list) >= 3
            self.id = input_list[0]
            self.kills = input_list[1]
            self.color = self.COLOR_KILL if self.kills else self.COLOR_WALL
            self.hitbox_type = input_list[2]
            assert len(input_list) == 3 + 6
            self.x1 = round(input_list[3] + input_list[8]) - 15
            self.x2 = round(input_list[3] + input_list[6]) + 15
            assert self.x1 < self.x2
            self.y1 = round(input_list[4] + input_list[7]) - 15
            self.y2 = round(input_list[4] + input_list[5]) + 15
            assert self.y1 < self.y2
    def draw_pixels(self, pix, x_loc, y_loc):
        x_loc = round(x_loc)
        y_loc = round(y_loc)
        for x in range(self.x1, self.x2):
            for y in range(self.y1, self.y2):
                #print (f"DRAWING AT {x+x_loc}, {y+y_loc}")
                if x + x_loc < 0:
                    print("OBJECT HITBOX IN NEGATIVE X")
                #assert x + x_loc >= 0
                assert y + y_loc + 100 >= 0
                if self.can_override_color(pix[x+x_loc, y+y_loc+100]):
                    pix[(x+x_loc, y+y_loc+100)] = self.color

    def can_override_color(self, other_color):
        return self.PRIORITY_COLOR[self.color] > self.PRIORITY_COLOR[other_color]
def print_object(obj):
    print (f"X = {obj.x}, Y = {obj.y}, ID = {obj.id}")

async def print_level(level_id, limit = 99999999):
    level = await client.get_level(level_id)
    print(f"PRINTING LEVEL NAME = {level.name} ID = {level.id} START")
    editor = level.open_editor()
    objects = editor.get_objects()
    objects.sort(key = lambda obj : obj.x)
    for i, obj in enumerate(objects):
        if i >= limit:
            break
        print_object(obj)
    print(f"PRINTING LEVEL NAME = {level.name} ID = {level.id} END")
    return level.id

async def upload_level_with_objects(object_ids):
    editor = gd.api.Editor()
    for i, obj_id in enumerate(object_ids):
        editor.add_objects(gd.api.Object(id = obj_id, x = 200 + i * 90, y = 115))
    level = gd.Level(name = "basic level", data = editor.dump(), client = client)
    await level.upload()
    return level.id

def get_collisions_basic():
    with open(COLLISION_FILENAME, "r") as f:
        data = json.load(f)
    return data

def get_collisions():
    with open(COLLISION_FILENAME, "r") as f:
        data = json.load(f)
    id_map = {}
    for obj in data:
        if obj[0] in id_map:
            print (f"DUPLICATE ID - {obj[0]}")
            continue
        id_map[obj[0]] = ObjectCollision(obj)
    return id_map

def update_collisions(extra_data):
    with open(COLLISION_FILENAME, "r") as f:
        data = json.load(f)
    with open(COLLISION_FILENAME, "w") as f:
        data += extra_data
        json.dump(data, f, indent = 4)


async def do_level_json_collisions(level_id, json_filename, first_obj_x):
    print(f"READING FILE \"{json_filename}\" with id {level_id}")
    level = await client.get_level(level_id)
    e = level.open_editor()
    e.get_objects().sort(key = lambda obj : obj.x)
    print (len(e.get_objects()))
    with open(json_filename) as f:
        from_list = json.load(f)
    to_list = []
    assert (len(e.get_objects()) == len(from_list))
    #for obj in e.get_objects():
    #    print (f"X = {obj.x}, Y = {obj.y}, ID = {obj.id}")
    target = first_obj_x
    for obj, in_data in zip(e.get_objects(), from_list):
        print_object(obj)
        to_list.append([obj.id, in_data[1], 0, target - obj.x, 15 - obj.y] + in_data[3:7])
        target += 30
    update_collisions(to_list)

async def visualize_level(level_id, filename = None):
    level = await client.get_level(level_id)
    objects = level.open_editor().get_objects()
    objects.sort(key = lambda obj : obj.x)
    max_x = round(objects[-1].x) + 500 
    max_y = 2600 # real max is 2415
    img = Image.new("RGB", size = (max_x, max_y), color = "white")
    pix = img.load()
    object_collisions = get_collisions()
    missing_ids = []
    for obj in objects:
            if obj.id not in object_collisions:
                if obj.id in ObjectCollision.VALID_OBJECTS:
                    missing_ids.append(obj.id)
                    print (f"OBJECT MISSING:")
                    print_object(obj)
                continue
            if obj.id not in ObjectCollision.VALID_OBJECTS:
                print (f"OBJECETC WITH ID {obj.id} SHOULDN'T HAVE A HITBOX")
            object_collisions[obj.id].draw_pixels(pix, obj.x, obj.y)
    for x in range(0, max_x):
        for y in range(0, 100):
            pix[x, y] = ObjectCollision.COLOR_WALL
        for y in range(2415+1, 2600):
            pix[x, y] = ObjectCollision.COLOR_KILL
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    if filename != None:
        img.save(filename)
    return img, missing_ids

def compress_level_image(img, scale, filename = None):
    scale = round(scale)
    new_size = (round(img.size[0] / scale), round(img.size[1] / scale))
    #new_img = Image.new("RGB", size = new_size) 
    #pix = img.load()
    #new_pix = new_img.load()
    #scale_half = round(scale / 2)
    new_img = img.resize(new_size, resample = 0)
    """
    for y in range(new_size[1]):
        print(f"\rSaving {round(y / new_size[1] * 100.0, 2)}%..", end = "")
        for x in range(new_size[0]):
            for _y in range(max(y * scale - scale_half, 0), min(y * scale + scale_half, img.size[1])):
                for _x in range(max(x * scale - scale_half, 0), min(x * scale + scale_half, img.size[0])):
                    if ObjectCollision.PRIORITY_COLOR[pix[_x, _y]] > ObjectCollision.PRIORITY_COLOR[new_pix[x, y]]:
                        new_pix[x, y] = pix[_x, _y]
    """
    print("")
    if filename != None:
        new_img.save(filename)
    return new_img

async def do_block_collisions():
    print("DO BLOCK COLLISIONS")
    level = await client.get_level(63582874)
    objects = level.open_editor().get_objects()
    objects.sort(key = lambda obj : obj.x)
    to_list = []
    target = 105
    for obj in objects:
        print (f"X = {obj.x}, Y = {obj.y}, ID = {obj.id}")
        assert target == obj.x
        to_list.append([obj.id, False, 0,  0, 0,  0, 0, 0, 0])
        target += 30
    update_collisions(to_list)

def get_collision_copy(prev_id, new_id):
    prev_list = list(filter(lambda l : l[0] == prev_id, get_collisions_basic()))
    assert(len(prev_list) == 1)
    new_list = prev_list[0].copy()
    new_list[0] = new_id
    return new_list

async def redo_collisions():
    with open(COLLISION_FILENAME, "w") as f:
        f.write("[]\n")
    await do_block_collisions()
    await do_level_json_collisions(63579679,"spike_sizes.json", 255)
    await do_level_json_collisions(63590510, "rectangle_size.json", 225)
    extra_list = []
    extra_list.append(get_collision_copy(1715, 9))
    extra_list.append(get_collision_copy(1903, 40))
    update_collisions(extra_list)


async def main():
    #await client.login(**json.load(open("login_details.json")))
    #await redo_collisions()
    stereo_madness_id = 20424353
    coll_spikes_test_id = 63583430
    coll_spikes1_id = 63579679
    bloodbath_id = 10565740
    coll_rect1_id = 63590510
    my_stereo_madness_id = 63590811
    await print_level(my_stereo_madness_id, limit = 50)
    #img, missing_ids = await visualize_level(stereo_madness_id, "basic_level_test.png")
    #compress_level_image(img, 8, "ai_view.png")
    #if len(missing_ids) != 0:
     #   print (await upload_level_with_objects(missing_ids))


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())