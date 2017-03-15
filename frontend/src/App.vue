<template>
  <div id="app">
    <menu-navbar></menu-navbar>

    <div class="container">
      <transition>
        <router-view></router-view>
      </transition>
    </div>

    <intro></intro>
  </div>
</template>

<script>
import store from 'store'
import MenuNavbar from 'components/MenuNavbar'
import Intro from 'components/Intro'

export default {
  name: 'app',
  components: { MenuNavbar, Intro },
  mounted () {
    store.dispatch('verify')
  }
}
</script>