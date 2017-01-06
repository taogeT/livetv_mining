<template>
  <div class="menu">
    <nav class="navbar navbar-default navbar-fixed-top" role="navigation">
      <div class="container">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <router-link class="navbar-brand" :to="{ name: 'index' }">Tao蜘蛛</router-link>
        </div>
        <div class="navbar-collapse collapse">
          <ul class="nav navbar-nav">
            <li :class="{ active: ['index', 'roomrank', 'site', 'room'].indexOf(this.$route.name) >= 0 }">
              <router-link :to="{ name: 'roomrank'}">房间</router-link>
            </li>
            <li :class="{ active: ['channelrank', 'channel'].indexOf(this.$route.name) >= 0 }">
              <router-link :to="{ name: 'channelrank'}">频道</router-link>
            <li :class="{ active: this.$route.name == 'search' }">
              <router-link :to="{ name: 'search'}">搜索</router-link>
            </li>
          </ul>
          <ul class="nav navbar-nav navbar-right">
            <li class="dropdown">
              <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">
                用户名 <span class="caret"></span>
              </a>
              <ul class="dropdown-menu">
                <li><a href="/">订阅房间</a></li>
                <li role="separator" class="divider"></li>
                <li><a href="/auth/logout">退出</a></li>
              </ul>
            </li>
            <li :class="{ active: this.$route.name == 'login' }">
              <router-link :to="{ name: 'login' }">登录</router-link>
            </li>
            <li :class="{ active: this.$route.name == 'about' }">
              <router-link :to="{ name: 'about' }">关于站点</router-link>
            </li>
            <li><a href="http://blog.zhengwentao.com/" target="_blank">作者博客</a></li>
          </ul>
        </div>
      </div>
    </nav>
  </div>
</template>

<script>
export default {
  name: 'menu'
}
</script>