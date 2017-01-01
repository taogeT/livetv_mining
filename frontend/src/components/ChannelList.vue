<template>
  <div class="channel-list">
    <template v-show="channels && channels.length > 0" v-for="n_item in Math.ceil(channels.length / columnnum)">
      <div class="row" style="text-align: center;">
        <div v-for="item in channels.slice((n_item - 1) * columnnum, n_item * columnnum)" class="col-lg-2 col-md-4">
          <router-link v-if="item.image" :to="{ name: 'channel', params: { id: item.id } }" :title="item.name">
            <img class="img-rounded" width="110%" :src="item.image">
          </router-link>
          <router-link :to="{ name: 'channel', params: { id: item.id } }">
            <template v-if="item.image">{{ item.name }}</template>
            <template v-else><h2>{{ item.name }}</h2></template>
          </router-link>
          <p>
            房间数 {{ item.total }}<br>
            {{ item.crawl_date | moment }} 更新<br>
          </p>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
export default {
  name: 'channel-list',
  props: ['channels'],
  data () {
    return { columnnum: 6 }
  }
}
</script>