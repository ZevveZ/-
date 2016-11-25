/**
 * Created by zev on 11/13/16.
 */
$(document).ready(function(){
    $('.zoom-in').fluidbox();
    twemoji.parse(document.getElementById('emoji-list'));
    $('.dianzan').click(function(){
        // 获取data-id，data-type
        var id = $(this).parent().data("id");
        var type = $(this).parent().data("type");
        // 发送数据给服务器
        $.getJSON("http://127.0.0.1:8000/scutmocc/bbs/dianzan", {"id":id,"type":type}, function(ret){
            if(ret!=undefined) {
                if (type === "theme") {
                    var update_i_list = $("[data-type=theme]").find(".dianzan i");
                    var update_span_list = $("[data-type=theme]").find(".dianzan span");

                    if (ret['res']) {
                        update_i_list.addClass("opts_active");
                        update_span_list.text(ret["dz_sum"] + "个赞").show();
                    } else {
                        update_i_list.removeClass("opts_active");
                        update_span_list.hide();
                    }
                } else if (type === "reply") {
                    var update_item = $("span[data-id=" + id + "][data-type=reply]");
                    var update_item_i = update_item.find(".dianzan i");
                    var update_item_span = update_item.find(".dianzan span");
                    if (ret['res']) {
                        update_item_i.addClass("opts_active");
                        update_item_span.text(ret["dz_sum"] + "个赞").show();
                    } else {
                        update_item_i.removeClass("opts_active");
                        update_item_span.hide();
                    }
                }
            }
        });
    });

    $("[data-type=attention]").click(function(){
        $.getJSON("http://127.0.0.1:8000/scutmocc/bbs/attention", {"ox_id":$(this).data("id")}, function(ret){
            if(ret["paid"]){
                $("[data-type=attention]").find("i").addClass("opts_active");
            }else{
                $("[data-type=attention]").find("i").removeClass("opts_active");
            }
        });
    });

    $("[data-type=collection]").click(function(){
       $.getJSON("http://127.0.0.1:8000/scutmocc/bbs/collection", {"theme_id": $(this).data("id")}, function(ret){
           if(ret["collected"]){
               $("[data-type=collection]").find("i").addClass("opts_active");
           }else{
               $("[data-type=collection]").find("i").removeClass("opts_active");
           }
       });
    });
});

function validate_reply_form(reply_form){
    with(reply_form){
        if(reply_content.value==""){
            if($(".alert").length == 0) {
                $(".reply-list").after('\
                                        <div class="alert alert-warning alert-dismissible" role="alert">\
                                            回复内容不能为空\
                                            <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>\
                                        </div>');
            }
            return false;
        }
    }
    return true;
}
