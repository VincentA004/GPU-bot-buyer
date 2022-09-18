import bestbuy as bb
import time
import multiprocessing as mp
from multiprocessing import Pool
import csv

num_bought = 0
list_of_process = []

def bot(sku):
    inst = bb.BestBuyHandler(sku, num_to_buy = 2)

    while (inst.in_stock() == 0):
        time.sleep(3)
        
    inst.add_to_cart()
    #inst.checkout()
    #inst.login()
    #inst.payment()
    #inst.buy()
    #inst.screenshot()
    return sku
    
def set_new_process(result):
    global num_bought
    global list_of_process
    num_bought += 1

    if(num_bought < 2):
        list_of_process.append(p.apply_async(bot, args= (int(result),), callback = set_new_process))

    if(num_bought >= 2):
        p.terminate()


if __name__ == '__main__':

    in_file = open('list_skus.csv', 'r')
    read_file = csv.reader(in_file, delimiter = ',')

    list_skus = list(read_file)

    with Pool(processes = mp.cpu_count()-1) as p:
    
        for x in list_skus:
          
            list_of_process.append(p.apply_async(bot, args= (x[0],), callback = set_new_process))

        for x in list_of_process:
            if(num_bought < 2):
                print(x.ready())
                x.wait()
                x.ready()
            if(num_bought >= 2):
                p.terminate()
            
