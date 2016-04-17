###LiveTV Mining
***

####介绍

此站点是为了实现**爬虫**、**数据挖掘/分析**等技术。目前主要是扫描斗鱼直播的数据进行统计，后续会加入其他直播网站(战旗、熊猫、twitch等)爬虫结果。

站点是在个人兴趣指引下用业余时间写的项目，可能技术还欠缺火候。使用中有问题或更新建议，欢迎直接提issue反馈给我，或可以用以下联系方式跟我交流：

* 邮件: zwtzjd@gmail.com
* QQ: 3084582097

####历程

* 2016-04-13 房间数据展示线型图：24小时内人气变化、一周人气走势、一周关注走势。

* 2016-04-10 完成数据库升级(Sqlite->Postgresql)，解决内存泄露问题。

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
* [Selenium](http://www.seleniumhq.org/)
* [Celery](http://www.celeryproject.org/)
