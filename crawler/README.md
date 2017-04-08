### 爬虫介绍
***

采用Scrapy开发爬虫，并使用redis替代进程管道进行管理(Scrapy-redis)。

目前20分钟获取一次数据。

#### 必备配置项

需要在 gather/settings.py 中修改。

* SQLALCHEMY_DATABASE_URI  数据库连接
* USER_AGENT_FILE  文件路径，随机选择文件中内容作为user-agent，不配置情况下默认使用USER_AGENT
* REDIS_URL  redis服务

#### 执行方式

可使用 run.py 文件输入参数执行，或直接使用 scrapy 命令行进行操作。