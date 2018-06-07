import pandas as pd
from translate import Translator

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


def connect_id_search():
    translator = Translator(to_lang="zh")

    players = pd.read_csv('../data/players_N.csv')
    fifa = pd.read_csv('../data/PlayerPersonalData.csv')

    print(players.shape)
    print(fifa.shape)

    print(players.columns)
    print(fifa.columns)

    # print(players['英文名'].apply(lambda x: x.split()[-1]))

    connect_id_df = pd.DataFrame(columns=['name', 'fifa_id', 'mark', 'Nationality'])

    print("循环次数:{}".format(len(list(zip(players['英文名'].apply(lambda x: x.split()[-1]),
                                        players['英文名'].apply(lambda x: x.split()[0][0].upper()),
                                        players['年龄'])))))

    for name, first_name, age, nationality in list(zip(players['英文名'].apply(lambda x: x.split()[-1]),
                                                       players['英文名'].apply(lambda x: x.split()[0][0].upper()),
                                                       players['年龄'],
                                                       )):
        print(name, first_name, age)

        df = fifa[(fifa.Name.str.contains(name)) & (fifa['Age'] == age - 1)].loc[:, ['ID', 'Name']]

        if len(df.values) == 0:
            id, fifa_name, mark = None, None, -1
        elif len(df.values) == 1:
            id, fifa_name, mark = *df.values[0], 'Right'
        else:
            mark = 0
            for id_0, fifa_name_0 in df.values:

                if first_name in fifa_name_0:
                    id, fifa_name = id_0, fifa_name_0
                    mark += 1



        connect_df_0 = pd.DataFrame([[id, fifa_name, mark]], columns=['name', 'fifa_id', 'mark'])
        connect_id_df = connect_id_df.append(connect_df_0, ignore_index=True)

    print(connect_id_df)
    print(connect_id_df.groupby(['mark']).count())
    print(connect_id_df.isnull().sum())
    connect_id_df.to_csv('../data/connect_id_player_2.csv', index=False)

def concat_dqd_fifa():
    """链接两个表"""

    connect_df = pd.read_csv('../data/connect_id_player.csv')
    players = pd.read_csv('../data/players_N.csv')
    fifa = pd.read_csv('../data/PlayerPersonalData.csv')



def main():

    connect_id_search()

    # players = pd.concat([players, connect_id_df], axis=1, ignore_index=True)
    # print

if __name__ == '__main__':
    main()