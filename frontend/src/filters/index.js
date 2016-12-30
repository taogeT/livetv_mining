import momentjs from 'moment'

export function moment (value) {
    return momentjs.utc(value).local().format("MM-DD HH:mm")
}

export function except (value, number) {
    var real_length = value.replace(/[^\x00-\xff]/g,"01").length
    if(real_length > number){
        var append_str = "..."
        ret_value = ""
        ret_length = 0
        for(var i=0; i < value.length; i++){
            ret_length += (value[i].charCodeAt(0) < 299 ? 1 : 2)
            ret_value += value[i]
            if(ret_length > number - append_str.length){
                break
            }
        }
        return ret_value + append_str
    }else{
        return value
    }
}
