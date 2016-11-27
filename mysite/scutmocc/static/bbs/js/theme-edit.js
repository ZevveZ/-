/**
 * Created by zev on 11/27/16.
 */

$(document).ready(function (){
    tinymce.init({
        selector: '#editor',
        language: 'zh_CN',
        plugins: 'image, imagetools, advlist, code, media, link, colorpicker, paste, table, textcolor',
        width: '300',
        height: '300'
    });
});