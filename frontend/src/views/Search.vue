<template>
  <div class="search">
    <form class="form form-horizontal" onsubmit="return false">
      <div class="form-group">
        <label class="control-label col-lg-2">站点</label>
        <div class="col-lg-6">
          <div class="checkbox">
            <label v-for="(item, index) in site">
              <input type="checkbox" :value="index" v-model="checksite">
              <img width="120px" height="50px" :src="item.image" :title="item.name">
            </label>
          </div>
        </div>
      </div>
      <div class="form-group">
        <label class="control-label col-lg-2">房间名</label>
        <div class="col-lg-5">
          <input class="form-control" type="text" v-model="name" placeholder="房间名">
        </div>
      </div>
      <div class="form-group">
        <label class="control-label col-lg-2">主播名</label>
        <div class="col-lg-5">
          <input class="form-control" type="text" v-model="host" placeholder="主播名">
        </div>
      </div>
      <div class="form-group">
        <label class="control-label col-lg-2"></label>
        <div class="col-lg-5">
          <button class="btn btn-primary" v-on:click="submit">搜索</button>
        </div>
      </div>
    </form>
    <template v-for="siteitem in site">
      <h3 v-if="siteitem.rooms && siteitem.rooms.length > 0">{{ siteitem.name }}</h3>
      <room-list v-if="siteitem.rooms" :rooms="siteitem.rooms"></room-list>
      <div v-if="siteitem.rooms && siteitem.rooms.length >= per_page" class="alert alert-warning" role="alert">
        若搜索结果较多，请输入更精确查询条件！
      </div>
    </template>
  </div>
</template>

<script>
import RoomList from 'components/RoomList.vue'
import { SiteRes } from 'resource'

export default {
  name: 'search',
  data () {
    return { site: [], name: "", host: "", checksite: [], per_page: 8}
  },
  components: { RoomList },
  mounted () {
    SiteRes.query().then(
      (response) => {
        this.site = response.body
        for(var si in this.site){
          this.checksite.push(si)
        }
      }, (response) => {
        console.log(response.body['message'])
      }
    )
  },
  methods: {
    submit: function(){
      for(var csi in this.checksite){
        this.get_site_rooms(this.checksite[csi])
      }
    },
    get_site_rooms: function(index){
      var data = {
        id: this.site[index].id,
        subType: 'room',
        name: this.name,
        host: this.host,
        per_page: this.per_page
      }
      SiteRes.query(data).then(
        (resp) => {
          this.$set(this.site[index], 'rooms', resp.body)
        }, (resp) => {
          console.log(resp.body['message'])
        }
      )
    }
  }
}
</script>