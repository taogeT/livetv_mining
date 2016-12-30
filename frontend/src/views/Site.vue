<template>
  <div class="site-detail">
    <div class="page-header">
      <table class="table">
        <tbody>
          <tr>
            <td width="20%"><img :src="site.image"></td>
            <td align="left">
              <h1>{{ site.name }}<small><a :href="site.url" target="_blank">官网</a></small></h1>
              <p><h4>频道数：{{ site.channel_total }}</p>
              <p><h4>正在直播房间数：{{ site.room_total }}</h4></p>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <h3>频道列表</h3>
    <channel-list :site-id="this.$route.params.id"></channel-list>
  </div>
</template>

<script>
import ChannelList from '../components/ChannelList.vue'

export default {
  name: 'site-detail',
  components: { ChannelList },
  data () {
    return { site: {} }
  },
  beforeCreate () {
    this.$http.get('http://localhost:5000/rest/site/' + this.$route.params.id).then(
      (response) => {
        this.site = response.body
      }, (response) => {
        console.log(response.body['message'])
      }
    )
  }
}
</script>