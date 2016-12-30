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
          <a class="navbar-brand" href="/">Tao蜘蛛</a>
        </div>
        <div class="navbar-collapse collapse">
          <ul class="nav navbar-nav">
            <li :class="{ active: ['index', 'roomrank', 'site'].indexOf(routername) >= 0 }">
              <router-link :to="{ name: 'roomrank'}">房间</router-link>
            </li>
            <li :class="{ active: routername == 'channelrank' }">
              <router-link :to="{ name: 'channelrank'}">频道</router-link>
            <li :class="{ active: routername == 'search' }">
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
                <li><a href="/">退出</a></li>
              </ul>
            </li>
            <li><a href="/">登录</a></li>
            <li><a href="/">关于站点</a></li>
            <li><a href="http://blog.zhengwentao.com/">作者博客</a></li>
          </ul>
        </div>
      </div>
    </nav>
  </div>
</template>

<script>
export default {
  name: 'menu',
  data () {
    return {
      routername: 'index'
    }
  },
  watch: {
    $route () {
      this.routername = this.$route.name
    }
  }
}
</script>