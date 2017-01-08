## 服务端介绍
***

采取Flask搭建后台服务。用户登录采用OAuth2的方式，目前仅允许使用github账号登录。

使用中有问题或更新建议，欢迎提issue或用以下联系方式跟我交流：

* 邮件: zwtzjd@gmail.com
* QQ: 3084582097

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
