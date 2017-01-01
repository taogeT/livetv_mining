<template>
  <div class="pagination">
    <div class="row">
      <a class="btn btn-nav btn-default" :class="{ disabled: currentPage == 1 }" v-on:click="seek(1)">
        <span>«</span>
      </a>
      <a class="btn btn-nav btn-default" :class="{ disabled: currentPage == 1 }" v-on:click="seek(currentPage - 1)">
        <span>&nbsp;‹</span>
      </a>
      <template v-for="ep in page_array">
        <a class="btn btn-default" :class="{ active: ep == currentPage }" v-on:click="seek(ep)">
          {{ ep }}
        </a>
      </template>
      <a class="btn btn-nav btn-default" :class="{ disabled: currentPage == totalPage }" v-on:click="seek(currentPage + 1)">
        <span>›&nbsp;</span>
      </a>
      <a class="btn btn-nav btn-default" :class="{ disabled: currentPage == totalPage }" v-on:click="seek(totalPage)">
        <span>»</span>
      </a>
    </div>
  </div>
</template>

<script>
export default {
  name: 'pagination',
  props: ['currentPage', 'totalPage'],
  computed: {
    page_array () {
      var compute_array = [this.currentPage]
      var leftnum = 2, rightnum = 2, leftstop = false, rightstop = false
      while((!leftstop && leftnum > 0) || (!rightstop && rightnum > 0)){
        if(!leftstop && leftnum > 0){
          if(compute_array[0] - 1 > 0){
            compute_array.splice(0, 0, compute_array[0] - 1)
            leftnum -= 1
          }else{
            leftstop = true
            rightnum += leftnum
            leftnum = 0
          }
        }
        if(!rightstop && rightnum > 0){
          if(compute_array[compute_array.length - 1] + 1 <= this.totalPage){
            compute_array.push(compute_array[compute_array.length - 1] + 1)
            rightnum -= 1
          }else{
            rightstop = true
            leftnum += rightnum
            rightnum = 0
          }
        }
      }
      return compute_array
    }
  },
  methods: {
    seek (pageNum) {
      this.$emit('seek', pageNum)
    }
  }
}
</script>

<style >
div.pagination {
    width: 100%;
    text-align: right;
    padding: 0px;
    margin: 0px;
}
</style>