"""
一个简单的Python爬虫, 用于抓取懂球帝世界杯球队队员信息
Anthor: 禹洋

"""
import re
import time
import pandas as pd

import random
import requests
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings('ignore')

# ----------------------------------------------------------------------------------------------------

# 球队信息, 放在类外面，可能会用到

# ----------------------------------------------------------------------------------------------------

team = {'A': ['俄罗斯', '沙特', '埃及', '乌拉圭'],
        'B': ['葡萄牙', '西班牙', '摩洛哥', '伊朗'],
        'C': ['法国', '澳大利亚', '秘鲁', '丹麦'],
        'D': ['阿根廷', '冰岛', '克罗地亚', '尼日利亚'],
        'E': ['巴西', '瑞士', '哥斯达黎加', '塞尔维亚'],
        'F': ['德国', '墨西哥', '瑞典', '韩国'],
        'G': ['比利时', '巴拿马', '突尼斯', '英格兰'],
        'H': ['波兰', '塞内加尔', '哥伦比亚', '日本']}

team_list = {
    '俄罗斯', '沙特', '埃及', '乌拉圭',
    '葡萄牙', '西班牙', '摩洛哥', '伊朗',
    '法国', '澳大利亚', '秘鲁', '丹麦',
    '阿根廷', '冰岛', '克罗地亚', '尼日利亚',
    '巴西', '瑞士', '哥斯达黎加', '塞尔维亚',
    '德国', '墨西哥', '瑞典', '韩国',
    '比利时', '巴拿马', '突尼斯', '英格兰',
    '波兰', '塞内加尔', '哥伦比亚', '日本'
}

# 懂球帝的 国家 id
team_id_list = [
    1878, 1897, 658, 2300,
    1772, 2137, 1509, 1178,
    944, 156, 1645, 643,
    132, 1143, 514, 1567,
    349, 2201, 477, 6816,
    1037, 1497, 2173, 1385,
    281, 1618, 2211, 774,
    1677, 1941, 473, 1348
]


class DongQiuDiSpider(object):
    """类的简要说明
    本类主要用于抓取懂球帝世界杯球队队员信息

    Attributes:
        header: 用于保存header信息
        proxies: 代理列表

        country_url: 国家url格式
        player_url: 队员url格式

        country_list: 懂球帝国家id
        country_test_list: 测试爬虫时候的国家id

        players_data: 用于记录每次解析出的普通球员详细信息
        keepers_data: 用于记录每次解析出的守门员详细信息

        players_national_data: 用于记录每次解析的国家队球员信息 id 位置 号码
        keepers_national_data: 用于记录每次解析的国家队守门员信息 id 位置 号码

    信息产生的过程：

        方法                  数据

        parse_player_id   -> players_national_data/keepers_national_data               每次函数运行新增23条信息
        parse_player_info -> players_data/keepers_data                                 每次函数运行新增1条信息

        start_spider      -> players_national_data + player_data         ->   save     链接两组信息并保存
                          -> keepers_national_data + keepers_data        ->   save
    """

    def __init__(self):

        self.headers = {"User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1 Trident/5.0;"}

        # 代理列表 最后没用，失效的太多有空加个筛选机制
        self.proxies = {
            'http': 'http://140.240.81.16:8888',
            'http': 'http://185.107.80.44:3128',
            'http': 'http://203.198.193.3:808',
            'http': 'http://125.88.74.122:85',
            'http': 'http://125.88.74.122:84',
            'http': 'http://125.88.74.122:82',
            'http': 'http://125.88.74.122:83',
            'http': 'http://125.88.74.122:81',
            'http': 'http://123.57.184.70:8081'
        }

        # team player 的url模式
        self.team_url = "http://www.dongqiudi.com/team/{}.html"
        self.player_url = "http://www.dongqiudi.com/player/{}.html"

        self.country_list = [
            1878, 1897, 658, 2300,
            1772, 2137, 1509, 1178,
            944, 156, 1645, 643,
            132, 1143, 514, 1567,
            349, 2201, 477, 6816,
            1037, 1497, 2173, 1385,
            281, 1618, 2211, 774,
            1677, 1941, 473, 1348
        ]

        self.country_test_list = [
            1878, 1897, 658, 2300,
        ]

        self.players_data = pd.DataFrame(columns=['id', '姓名', '英文名', '国家', '俱乐部', '年龄',
                                                  '生日', '身高', '体重', '惯用脚', '综合能力', '速度',
                                                  '力量', '防守', '盘带', '传球', '射门'])

        self.keepers_data = pd.DataFrame(columns=['id', '姓名', '英文名', '国家', '俱乐部', '年龄',
                                                  '生日', '身高', '体重', '惯用脚', '综合能力', '扑救',
                                                  '站位', '速度', '反应', '开球', '手型'])

        self.players_national_data = pd.DataFrame(columns=['id', '位置', '号码'])
        self.keepers_national_data = pd.DataFrame(columns=['id', '位置', '号码'])

        print("懂球帝世界杯球员爬虫准备就绪, 准备爬取数据...")

    def get_country_html(self, country_id):
        """根据当前页码爬取网页HTML
        Args:
            country_id: 表示当前所抓取的国家队id
        Returns:
            返回抓取到整个页面的HTML(unicode编码)
        Raises:
            RequestException: 爬取过程中 requests 报出的各种异常
        """
        url = self.team_url.format(country_id)
        try:
            response = requests.get(url, headers=self.headers)     # , proxies=self.proxies[random.randint(0, len(self.proxies))])

            print("国家:  {} \n状态:  {}".format(country_id, response.status_code))
            second = random.randint(1, 8)
            print("休息 {} s".format(second))
            time.sleep(second)


        except requests.exceptions.RequestException as e:
            # A serious problem happened, like an SSLError or InvalidURL
            print("Error: {}".format(e))

        return response.text

    def parse_player_id(self, country_page):
        """
        通过国家队HTML, 匹配国家队成员id 位置 号码
        添加到 player(keepers)_national_data

        Args:
            country_page: 传入国家队的HTML文本用于匹配队员id，position 等信息

        Return:
            国家队成员的id position 信息： (id, position) 形式的 zip 对象
        """

        soup = BeautifulSoup(country_page, "lxml")
        # print(soup.prettify())
        player_table = soup.find('table', attrs={'class': "teammates_list"})

        # print(type(player_table))     # <class 'bs4.element.Tag'>

        tr_list = player_table.find_all('tr')
        # print(type(tr_list[1]))  # <class 'bs4.element.Tag'>

        id_list = []
        pos_list = []

        columns = ['id', '位置', '号码']
        keepers_df = pd.DataFrame(columns=columns)
        players_df = pd.DataFrame(columns=columns)
        assert 25 <= len(tr_list) < 30

        # 这里因为各队助理教练的数量不同，所以从下到上匹配23个队员信息，range的范围仔细推敲一下
        for i in range(len(tr_list)-1, len(tr_list)-24, -1):
            td_list = tr_list[i].find_all('td')

            try:
                position = td_list[0].contents[0]
            except:
                print("不会真的连个位置信息都没有吧。。。。")
                position = None

            pos_list.append(position)

            try:
                number = td_list[1].contents[0]
            except:
                print("没有号码？同情这位兄弟")
                number = None

            href = td_list[2].a['href']
            id = re.findall(r'https://www.dongqiudi.com/player/(.*?).html', href, re.S)[0]
            id_list.append(id)

            # 根据位置对不同对不同队员的记录位置做出选择
            if position != "守门员":
                players_df = pd.DataFrame([[id, position, number]], columns=columns)
                self.players_national_data = self.players_national_data.append(players_df, ignore_index=True)
            else:
                keeper_df = pd.DataFrame([[id, position, number]], columns=columns)
                self.keepers_national_data = self.keepers_national_data.append(keeper_df, ignore_index=True)

        id_pos = zip(id_list, pos_list)

        return id_pos

    def get_player_html(self, player_id):
        """根据球员id爬取网页HTML
                Args:
                    player_id: 表示当前所抓取的队员id
                Returns:
                    返回抓取到整个页面的HTML(unicode编码)
                Raises:
                    RequestException: 爬取过程中 requests 报出的各种异常
                """

        url = self.player_url.format(player_id)
        try:
            response = requests.get(url, headers=self.headers)
            print("球员:  {} \n状态:  {}".format(player_id, response.status_code))
            second = random.randint(1, 3)
            print("休息 {} s".format(second))
            time.sleep(second)
        except requests.exceptions.RequestException as e:
            # A serious problem happened, like an SSLError or InvalidURL
            print("Error: {}".format(e))

        return response.text

    def parse_player_info(self, id, position, player_page):
        """用于解析球员具体能力值等信息
        Args:
            player_page: 需要解析的球员html

        Return:
            无返回值

        SideEffect:
            向self.datas添加球员信息
        """
        soup = BeautifulSoup(player_page, 'lxml')

        # 姓名

        name = soup.find('h1', attrs={"class": "name"}).contents[0]
        print(name)

        en_name = soup.find('span', attrs={"class": "en_name"}).contents[0]


        # 基本信息

        info_ul = soup.find('ul', attrs={"class": "detail_info"})
        li_list = info_ul.find_all('li')

        try:
            club = li_list[0].find_all('span')[1].contents[0]
        except:
            print("没有club信息")
            club = None

        national = li_list[3].find_all('span')[1].contents[0]

        try:
            age = li_list[4].find_all('span')[1].contents[0]
            age = re.findall(r'(\d+).*?', age)[0]
        except:
            print("没有年龄信息")
            age = None

        try:
            birth = li_list[5].find_all('span')[1].contents[0]
        except:
            print("没有生日信息")
            birth = None

        try:
            height = li_list[6].find_all('span')[1].contents[0]
            height = re.findall(r'(\d+).*?', height)[0]
        except:
            print("没有身高信息")
            height = None

        try:
            weight = li_list[7].find_all('span')[1].contents[0]
            weight = re.findall(r'(\d+).*?', weight)[0]
        except:
            print("没有体重信息")
            weight = None

        try:
            foot = li_list[8].find_all('span')[1].contents[0]
        except IndexError as e:
            print("没有惯用脚信息")
            foot = None

        # 能力值信息

        if position != '守门员':
            try:
                ability = soup.find('div', attrs={"id": "title"}).span.contents[0]
            except:
                print("没有能力值信息！")
                ability = None

            # 根据综合能力是否有就能确定是否包含详细能力信息
            if ability is not None:
                speed = soup.find('div', attrs={"class": "item item0"}).span.contents[0]
                strength = soup.find('div', attrs={"class": "item item1"}).span.contents[0]
                defence = soup.find('div', attrs={"class": "item item2"}).span.contents[0]
                dribbling = soup.find('div', attrs={"class": "item item3"}).span.contents[0]
                passball = soup.find('div', attrs={"class": "item item4"}).span.contents[0]
                shoot = soup.find('div', attrs={"class": "item item5"}).span.contents[0]
            else:
                speed = None
                strength = None
                defence = None
                dribbling = None
                passball = None
                shoot = None

            print(en_name)
            print(club, position, national, age, birth, height, weight, foot)
            print("能力值：{0} {1} {2} {3} {4} {5} {6}".format(ability, speed, strength,
                                                           defence, dribbling, passball, shoot))

            columns = ['id', '姓名', '英文名', '国家', '俱乐部', '年龄',
                       '生日', '身高', '体重', '惯用脚', '综合能力', '速度',
                       '力量', '防守', '盘带', '传球', '射门']

            info_list = [id, name, en_name, national, club, age, birth,
                         height, weight, foot, ability, speed, strength,
                         defence, dribbling, passball, shoot]

            df = pd.DataFrame([info_list], columns=columns)
            self.players_data = self.players_data.append(df, ignore_index=True)

        else:
            try:
                ability = soup.find('div', attrs={"id": "title"}).span.contents[0]
            except:
                print("没有能力值信息！")
                ability = 0

            if ability != 0:
                speed = soup.find('div', attrs={"class": "item item0"}).span.contents[0]
                strength = soup.find('div', attrs={"class": "item item1"}).span.contents[0]
                defence = soup.find('div', attrs={"class": "item item2"}).span.contents[0]
                dribbling = soup.find('div', attrs={"class": "item item3"}).span.contents[0]
                passball = soup.find('div', attrs={"class": "item item4"}).span.contents[0]
                shoot = soup.find('div', attrs={"class": "item item5"}).span.contents[0]
            else:
                speed = None
                strength = None
                defence = None
                dribbling = None
                passball = None
                shoot = None

            print(en_name)
            print(club, position, national, age, birth, height, weight, foot)
            print("能力值：{0} {1} {2} {3} {4} {5} {6}".format(ability, speed, strength,
                                                           defence, dribbling, passball, shoot))

            columns = ['id', '姓名', '英文名', '国家', '俱乐部', '年龄',
                       '生日', '身高', '体重', '惯用脚', '综合能力', '扑救',
                       '站位', '速度', '反应', '开球', '手型']

            info_list = [id, name, en_name, national, club, age, birth,
                         height, weight, foot, ability, speed, strength,
                         defence, dribbling, passball, shoot]

            df = pd.DataFrame([info_list], columns=columns)
            self.keepers_data = self.keepers_data.append(df, ignore_index=True)

    def start_spider(self):
        """爬虫空值方法

        信息产生的过程：

        方法                  数据

        parse_player_id   -> players_national_data/keepers_national_data               每次函数运行新增23条信息
        parse_player_info -> players_data/keepers_data                                 每次函数运行新增1条信息

        start_spider      -> players_national_data(640) + player_data(640)  ->   save  链接两组信息并保存(数据量)
                          -> keepers_national_data(96)  + keepers_data(96)  ->   save


        """
        for country in self.country_list:
            country_html = self.get_country_html(country)
            id_pos = self.parse_player_id(country_html)

            for id, position in id_pos:
                player_html = self.get_player_html(id)
                self.parse_player_info(id, position, player_html)

        self.players_data = pd.concat([self.players_national_data, self.players_data.drop(columns='id')], axis=1)
        self.keepers_data = pd.concat([self.keepers_national_data, self.keepers_data.drop(columns='id')], axis=1)

        self.players_data.to_csv('../data/players_N.csv', index=False)
        self.keepers_data.to_csv('../data/keepers_N.csv', index=False)


    def start_test(self):
        """测试start_spider 的小量数据，功能相同，只爬取一个国家"""
        for country in self.country_list[3: 4]:
            country_html = self.get_country_html(country)
            id_pos = self.parse_player_id(country_html)

            for id, position in id_pos:
                player_html = self.get_player_html(id)
                self.parse_player_info(id, position, player_html)

        self.players_data = pd.concat([self.players_national_data, self.players_data.drop(columns='id')], axis=1)
        self.keepers_data = pd.concat([self.keepers_national_data, self.keepers_data.drop(columns='id')], axis=1)

        self.players_data.to_csv('../data/players_test.csv', index=False)
        self.keepers_data.to_csv('../data/keepers_test.csv', index=False)


def main():
    print(
    """
        ###############################
            一个简单的懂球帝爬虫
            Author: yuyang
            Version: 0.0.1
            Date: 2018-06-04
        ###############################
    """)
    my_spider = DongQiuDiSpider()
    my_spider.start_spider()
    # my_spider.start_test()


if __name__ == '__main__':
    main()