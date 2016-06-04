###关于作者
***

**人生苦短，我用Python**

半路出家程序员(猿)，现居于鹭岛，爱好：美食、游戏、乃木坂46。

曾经被JAVA伤害很深，现已投入Python怀抱。

###关于项目 LiveTV Mining
***

####介绍

项目实现**爬虫**、**数据挖掘/分析**等功能。目前主要是扫描直播(战旗、熊猫、斗鱼)收集数据，后续会开发其他直播爬虫。

项目结构为Flask Blueprint，可嵌入Flask项目使用。

项目是在个人兴趣指引下用业余时间写的，技术还欠缺火候。使用中有问题或更新建议，欢迎提issue或用以下联系方式跟我交流：

* 邮件: zwtzjd@gmail.com
* QQ: 3084582097
* Github: [taogeT](https://github.com/taogeT)

####历程

* 2016-06-03 站点添加SSL证书，开启https，http失效。

* 2016-06-01 Flask-Celery插件开发改造，完成0.2版本。解决了需要手动启动应用上下文来初始化数据库、celery实例的问题。

* 2016-05-31 机器性能较差导致访问出现504 gateway time out错误，做了一定量分析和效率提升。

* 2016-05-29 发现站点有爬虫访问，封禁IP并使用nginx做简单反爬虫策略(UA)。

* 2016-05-27 改造站点为项目展示平台。

* 2016-05-16 修正房间切换频道导致数据重复错误。

* 2016-05-08 supervisord+celery配置错误，未设定优先级(priority)，导致beat无法分发任务到worker。supervisord config 添加priority设置优先级。

* 2016-04-30 完成爬虫重构，部署主机测试。

* 2016-04-28 Selenium+Phantomjs 存在资源无法完全释放的问题(too many files open)，查询未发现较妥善全面解决方式。采用定期重启的方式，同时尝试开发其他方式爬虫。

* 2016-04-18 测试效果不理想，频繁出现未获取全部respone时被访问服务器断开连接(ChunkedEncodingError)，恢复使用Selenium。纠正频道/房间唯一标识，过程导致部分数据作废。修改后台重试机制，可在出错频道继续遍历。

* 2016-04-17 重构爬虫模块，部分使用requests替换phantomjs，提升爬虫效率。部署主机测试。

* 2016-04-13 房间数据展示线型图：24小时内人气变化、一周人气走势、一周关注走势。

* 2016-04-10 完成数据库升级(Sqlite->Postgresql)，解决句柄占用无法释放问题。

* 2016-04-08 完成熊猫、战旗爬虫开发，上线进行数据收集。

* 2016-04-06 域名 [http://www.zhengwentao.com](http://www.zhengwentao.com) 申请完毕，正式建站。

* 2016-04-05 上线前解决网页BUG，调整样式撰写"关于"信息。开发完成搜索模块。

* 2016-04-03 解决内存泄露、Phantomjs执行缓慢超时的问题，爬虫运行稳定。完成房间统计表格自动生成绘制功能开发。

* 2016-03-29 主机申请完毕，采用Nginx+uwsgi部署试运行。

* 2016-03-28 选用Celery框架做后台任务执行。开发完成独立Flask插件 [Flask-Celery](https://github.com/taogeT/flask-celery) 适用于Python 3.4+，Celery 3.0+。

* 2016-03-26 调整重构爬虫模块，从其他模块中剥离独立。

* 2016-03-25 完成战旗、虎牙爬虫开发。

* 2016-03-24 完成斗鱼爬虫开发，采用python3+Selenium+Phantomjs直接读取斗鱼网站信息。使用Flask+Bootstrap开发网站。

* 2016-03-23 Github创建仓库，开始项目开发。

###感激
***

感谢以下项目的支持，排名不分先后

* [Flask](http://flask.pocoo.org/) 
* [Bootstrap](http://www.bootstrap.com/)
* [Requests](http://www.python-requests.org/)
* [Selenium](http://www.seleniumhq.org/)
* [Celery](http://www.celeryproject.org/)
