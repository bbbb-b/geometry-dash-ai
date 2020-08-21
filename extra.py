import gd
import asyncio
import time

async def main():
    mem = gd.memory.get_memory()
    """
    while True:
        t1 = time.time()
        print ("Second start")
        last_x = mem.x_pos
        last_y = mem.y_pos
        x_change_count  = 0
        y_change_count = 0
        test_count = 0
        while t1 + 1.0 >= time.time():
            tmp_x = mem.x_pos
            tmp_y = mem.y_pos
            if last_x != tmp_x:
                #print(last_x, tmp_x)
                x_change_count += 1
            if last_y != tmp_y:
                #print(last_y, tmp_y)
                y_change_count += 1
            last_x = tmp_x
            last_y = tmp_y 
            test_count += 1
        print ("Second end")
        print ("X changed {}/{} times".format(x_change_count, test_count))
        print ("Y changed {}/{} times".format(y_change_count, test_count))"""

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())