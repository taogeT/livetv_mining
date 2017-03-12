<template>
  <div class="site-detail">
    <div class="page-header">
      <table class="table">
        <tbody>
          <tr>
            <td width="20%"><img :src="site.image"></td>
            <td align="left">
              <h1>{{ site.name }}<small><a :href="site.url" target="_blank">官网</a></small></h1>
              <p><h4>频道数：{{ site.channel_total }}</h4></p>
              <p><h4>正在直播房间数：{{ site.room_total }}</h4></p>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <h3>频道列表</h3>
    <channel-list :channels="this.channels"></channel-list>
  </div>
</template>

<script>
import ChannelList from 'components/ChannelList.vue'
import { SiteRes } from 'resource'

export default {
  name: 'site-detail',
  components: { ChannelList },
  data () {
    return { site: {}, channels: [] }
  },
  mounted () {
    SiteRes.query({ id: this.$route.params.id }).then(
      (response) => {
        this.site = response.body
        SiteRes.query({ id: this.site.id, subType: 'channel', per_page: 1000 }).then(
          (response) => {
            this.channels = response.body
          }, (response) => {
            console.log(response.body['message'])
          }
        )
      }, (response) => {
        console.log(response.body['message'])
      }
    )
  }
}
</script>