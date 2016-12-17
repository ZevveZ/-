/**
 * Created by zev on 11/13/16.
 */
$(document).ready(function(){
    // 为每个img标签添加a父标签以支持fluidbox
    $('article').find('img').each(function(){
        $(this).wrap("<a class='zoom-in' alt='' href="+$(this).attr('src')+"></a>");
    });
    $('.zoom-in').fluidbox();

    twemoji.parse($("#emoji-list")[0],{ext:'.svg',folder:'2/svg'});
    $('.dianzan').click(function(){
        // 获取data-id，data-type
        var id = $(this).parent().data("id");
        var type = $(this).parent().data("type");
        if(type == 'reply'){
            var reply_count=$('#reply_count').text()
        }
        // 发送数据给服务器
        $.getJSON("http://127.0.0.1:8000/scutmocc/bbs/dianzan", {"id":id,"type":type,"reply_count": reply_count}, function(ret){
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
    //转换content
    $(".content").each(function(){
        //判断是否需要处理
        if($(this).text().indexOf("!(")!=-1){
            $(this).html($(this).text().replace(/!\(/g, "<").replace(/!\)/g, ">"));
        }
        twemoji.parse($(this)[0], {ext:'.svg',folder:'2/svg'});
    });

    //处理回复时添加表情
    $("#emoji-list li").on("click",function(){
        $("textarea.markdown").val($("textarea.markdown").val()+$(this).children('img').attr('alt'));
    });
    //处理鼠标悬浮在表情
    $('#emoji-list li').on("mouseover mouseout",function(){
       if(event.type == "mouseover"){
           $(this).css("background-color","lightgray");
           $('.modal-footer').html($(this).html());
       }else if(event.type == "mouseout"){
            $(this).css("background-color","");
       }
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
};

//回复评论时调用
function reply_comment(item){
    $('textarea.markdown').focus();
    $('textarea.markdown').val($('textarea.markdown').val() + ' @' + $(item).parent().siblings().first().text() + ' ');
}

function focus_on_textarea(){
    $('textarea.markdown').focus();
}
