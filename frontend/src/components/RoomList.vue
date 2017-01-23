<template>
  <div class="room-list">
    <template v-for="n_item in Math.ceil(rooms.length / columnnum)">
      <div class="row" style="text-align: center;">
        <div v-for="item in rooms.slice((n_item - 1) * columnnum, n_item * columnnum)" class="col-lg-3 col-md-6">
          <router-link v-if="item.image" :to="{ name: 'room', params: { id: item.id } }" :title="item.name">
            <img class="img-rounded" width="100%" :src="item.image">
          </router-link>
          <router-link :to="{ name: 'room', params: { id: item.id } }" :title="item.name">
            {{ item.name | except 34 }}
          </router-link>
          <p>
            主播 {{ item.host }}<br>
            人气 <span style="color: red;">{{ item.online }}</span> 更新 {{ item.crawl_date | moment }}
          </p>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
export default {
  name: 'room-list',
  props: ['rooms'],
  data () {
    return { columnnum: 4 }
  }
}
</script>
