<template>
  <div class="channel-rank">
    <div class="container" id="index_channel">
      <div class="row">
        <template v-for="item in site">
          <div class="col-lg-3" style="text-align: center;">
            <site-header :site="item"></site-header>
            <span style="text-align: left;">
              <h3>频道房间数 TOP{{ rank_num }}</h3>
              <table class="table table-striped">
                <thead>
                  <th>排名</th>
                  <th>频道</th>
                  <th>房间数</th>
                </thead>
                <tbody>
                  <tr v-for="(channelitem, index) in item.channels">
                    <td>{{ index + 1 }}</td>
                    <td>
                      <router-link :to="{ name: 'channel', params: { id: channelitem.id } }">
                        {{ channelitem.name }}
                      </router-link>
                    </td>
                    <td>{{ channelitem.total }}</td>
                  </tr>
                </tbody>
              </table>
            </span>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import SiteHeader from 'components/SiteHeader.vue'
import { SiteRes } from 'resource'

export default {
  name: 'channel-rank',
  data () {
    return {
      site: [],
      rank_num: 15
    }
  },
  components: { SiteHeader },
  mounted () {
    SiteRes.query().then(
      (response) => {
        this.site = response.body
        for(const index in this.site){
          this.get_site_channels(index)
        }
      }, (response) => {
        console.log(response.body['message'])
      }
    )
  },
  methods: {
    get_site_channels: function(index){
      SiteRes.query({ id: this.site[index].id, subType: 'channel', per_page: this.rank_num }).then(
        (resp) => {
          this.$set(this.site[index], 'channels', resp.body)
        }, (resp) => {
          console.log(resp.body['message'])
        }
      )
    }
  }
}
</script>