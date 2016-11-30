/**
 * Created by zev on 11/29/16.
 */
$(document).ready(function(){
    tinymce.init({
        selector:"#editor",
        language: 'zh_CN',
        plugins: 'image, imagetools, advlist, code, media, link, colorpicker, paste, table, textcolor, imageupload',
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
        imageupload_url: ''
    });
});
