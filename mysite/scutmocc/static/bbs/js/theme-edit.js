/**
 * Created by zev on 11/29/16.
 */
$(document).ready(function(){
    tinymce.init({
        selector:"#editor",
        language: 'zh_CN',
        menubar:false,
        plugins: 'image, imagetools, advlist, code, media, link, colorpicker, paste, table, textcolor',
        paste_data_images: true,    //直接拖图片进编辑器
        images_upload_url: 'http://127.0.0.1:8000/scutmocc/bbs/image_upload',
        images_upload_base_path: '/media/bbs/theme',
        relative_urls: false
    });
});

 //检查必填的内容是否为空
function validate_editor_form(editor_form){
    with(editor_form){
        if(college_name.value==''||board_name.value==''||title.value==''||tinymce.activeEditor.getContent()==''){
            if($(".alert").length == 0) {
                $("#theme_form").prepend('<div class="alert alert-warning alert-dismissible" role="alert">\
                                            学院类型、板块类型、标题、内容不能为空\
                                            <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>');
            }
            return false;
        }
    }
    return true;
}
//点击学院和板块的下拉菜单时，更新对应input的内容
function update_input(item){
    $(item).parent().parent().parent().next().val($(item).text());
}