/**
 * Created by zev on 11/27/16.
 */

tinymce.init({
    selector:'textarea',
    language: 'zh_CN',
    menubar:false,
    plugins: 'image, imagetools, advlist, code, media, link, colorpicker, paste, table, textcolor, imageupload',
    width: 1000,
    height: 400,
    toolbar: 'insertfile undo redo | \
                 styleselect | \
                 bold italic | \
                 alignleft aligncenter alignright alignjustify | \
                 bullist numlist outdent indent | \
                 link image | \
                 print preview fullpage | \
                 forecolor backcolor emoticons |\
                 codesample fontsizeselect fullscreen| \
                 imageupload',
    imageupload_url: '',
    //解决tinymce显示覆盖了label标签
    setup:function(editor){
        editor.on('init',function(){
            $('.mce-tinymce').css('float','left');
        })
    }
});
