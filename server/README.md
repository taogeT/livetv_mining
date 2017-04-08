### RESTFul API资源
***

#### 抓取数据查询

* Site：站点信息，站点包含的频道/房间信息。
* Channel：频道信息，频道包含的房间信息。
* Room：房间信息。

#### 订阅

* Subscribe：登录用户订阅房间。

### 必备配置项
***

* SECRET_KEY  服务器密钥
* SQLALCHEMY_DATABASE_URI  数据库连接
* GITHUB_CONSUMER_KEY  Github OAuth2 Client ID
* GITHUB_CONSUMER_SECRET  Github OAuth2 Client Secret

完成以上配置项后才能开始部署。

### 部署
***

执行以下步骤前默认已经配置好必备配置项并建立数据库实例

1. 建立python3沙盒环境(minicomda or virtualenv)。若服务器上未存在python3，请参照[python官方文档](https://wiki.python.org/moin/BeginnersGuide/Download)安装。
1. 激活环境，执行 pip install -r requirements.txt 安装python package。
1. 使用ORM创建表，执行 python server/manage.py shell 激活python命令行，执行 db.create_all() 自动创建表。
1. 执行 python server/manage.py runserver 启动WEB服务。
