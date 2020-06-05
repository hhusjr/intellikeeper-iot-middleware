from reader import perform_duty, periodic_check
from multiprocessing import Process

if __name__ == '__main__':
    Process(target=perform_duty).start()
    Process(target=periodic_check).start()
