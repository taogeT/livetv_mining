<template>
  <div class="channel-detail">
    <div class="row">
      <div v-if="channel.image" class="col-lg-3 col-md-4">
        <img class="img-rounded" width="100%" :src="channel.image">
      </div>
      <div :class="channel.image ? 'col-lg-9 col-md-8' : 'col-lg-12 col-md-12'" style="text-align: left;">
        <h1>{{ channel.name }}<small><a :href="channel.url" target="_blank">官网</a></small></h1>
        <p>
          <h4>
            从属站点：<router-link :to="{ name: 'site', params: { id: channel.site_id } }">{{ channel.site }}</router-link>
            当前直播房间数：{{ channel.total }}
          </h4>
          <h4>更新时间：{{ channel.crawl_date | moment }}</h4>
        </p>
      </div>
    </div>
    <h3>房间列表</h3>
    <room-list :channel-id="this.$route.params.id"></room-list>
  </div>
</template>

<script>
import RoomList from '../../components/RoomList.vue'

export default {
  name: 'channel-detail',
  data () {
    return { channel: {} }
  },
  components: { RoomList },
  mounted () {
    this.$http.get('http://localhost:5000/rest/channel/' + this.$route.params.id).then(
      (response) => {
        this.channel = response.body
      }, (response) => {
        console.log(response.body['message'])
      }
    )
  }
}
</script>