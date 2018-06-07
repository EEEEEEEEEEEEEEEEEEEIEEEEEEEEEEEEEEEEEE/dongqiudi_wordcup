import numpy as np
import pandas as pd
from pprint import pprint
import warnings
warnings.filterwarnings('ignore')

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

def main():
    players = pd.read_csv('../data/players_N.csv')
    print("player 信息")
    print(players.shape)
    print(players.columns)
    # print(players.head())

    print("-"*30)

    keepers = pd.read_csv('../data/keepers_N.csv')
    print("keeper 信息")
    print(keepers.shape)
    print(keepers.columns)
    # print(keepers.head())


    player_cols = ['速度', '力量', '防守', '盘带', '传球', '射门']
    keeper_cols = ['扑救', '站位', '速度', '反应', '开球', '手型']

    df_all = pd.concat([players.drop(columns=player_cols), keepers.drop(columns=keeper_cols)], axis=0)
    print(df_all.shape)
    print(df_all.info())
    pprint(df_all.describe(include='all'))

    # ----------------------------------------------------------------------------------------------------

    # 空值处理

    # ----------------------------------------------------------------------------------------------------
    print("空值情况：")
    print(df_all.isnull().sum().sort_values(ascending=False))

    pprint(df_all.groupby(['国家'])[['综合能力']].agg(['mean', 'median', 'count']))

    print("空值情况：")
    print(df_all.isnull().sum().sort_values(ascending=False))





if __name__ == '__main__':
    main()