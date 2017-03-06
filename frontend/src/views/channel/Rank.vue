<template>
  <div class="channel-rank">
    <div class="container" id="index_channel">
      <template v-for="n_item in Math.ceil(site.length / columnnum)">
        <div class="row" style="text-align: center;">
          <div v-for="item in site.slice((n_item - 1) * columnnum, n_item * columnnum)" class="col-lg-3 col-md-6">
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
        </div>
      </template>
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
      rank_num: 10,
      columnnum: 4
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