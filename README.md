#   世界杯球员信息
> 对[懂球帝](http://www.dongqiudi.com/)中世界杯球队的队员进行基本信息能力值等进行爬取，可视化展示

### 爬虫

- 总爬取数据量不到800
- 单线程
- 反爬措施基本只用到了 设置headers 增加等待时间
- 各种缺失都填充为None，方便后续分析处理
- 信息产生的过程：
```
        方法                  数据

        parse_player_id   -> players_national_data/keepers_national_data               每次函数运行新增23条信息
        parse_player_info -> players_data/keepers_data                                 每次函数运行新增1条信息

        start_spider      -> players_national_data + player_data         ->   save     链接两组信息并保存
                          -> keepers_national_data + keepers_data        ->   save 
```


