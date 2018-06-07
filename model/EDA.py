import numpy as np
import pandas as pd
from pprint import pprint

def main():
    players = pd.read_csv('../data/players_N.csv')
    print("player 信息")
    print(players.shape)
    print(players.columns)
    print(players.head())

    print("-"*30)

    keepers = pd.read_csv('../data/keepers_N.csv')
    print("keeper 信息")
    print(keepers.shape)
    print(keepers.columns)
    print(keepers.head())



if __name__ == '__main__':
    main()