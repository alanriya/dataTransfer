from lib.publisher import Publisher
from lib.parser import Parser
import argparse
import sys, os
from lib.config import conn_arg

sys.path.append(os.getcwd())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='arg')
    parser.add_argument('--date', type=str)
    ns = parser.parse_args()
    publisher = Publisher(conn_arg)
    p = Parser(publisher, ns.date)
    p.process()

