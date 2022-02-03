import sys, os
from lib.consumer import Consumer
from lib.config import conn_arg

sys.path.append(os.getcwd())

if __name__ == "__main__":
    c = Consumer(conn_arg)
    c.start_consuming()
