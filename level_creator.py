import gd
import asyncio
import time
import json
from numpy import arange

async def main():
    global new_level
    _x, _y = 1000, 1000
    client = gd.Client()
    memory = gd.memory.get_memory()
    await client.login(**json.load(open("login_details.json")))
    print (client.name)
    editor = gd.api.Editor()
    editor.add_objects(gd.api.Object(id = 1, x = _x, y = _y))
    editor.add_objects(gd.api.Object(id = 1, x = _x + 5000, y = _y))
    print (editor.dump())
    #new_level = await client.upload_level(name = "testt", unlisted = False, data = editor.dump(), description = "testtest")
    #print (new_level.id)
    input("waiting for gd to open..")
    x_offset = 500
    y_offset = 500
    bitmap = []
    for y in arange(_y - y_offset, _y + y_offset, 0.5):
        bitmap.append([])
        for x in arange(_x - x_offset, _x + x_offset, 0.5):
            print(x, y)
            memory.player_unfreeze()
            #time.sleep(0.01)
            memory.set_x_pos(x)
            memory.set_y_pos(y)
            #memory.player_freeze()
            print (memory.x_pos, memory.y_pos)
            #time.sleep(0.01)
            if memory.is_dead():
                bitmap[-1].append(True)
                while memory.is_dead():
                    pass
            else:
                bitmap[-1].append(False)

    f = open("bitmap.txt", "w")
    for Y in bitmap:
        for X in Y:
            f.write("X" if X else " ")
        f.write("\n")
    f.close()
    return 0

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
