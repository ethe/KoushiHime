
function postrefreshmodalsuccess() {
    var success = "<div class='text-center'><span class='glyphicon glyphicon-ok' aria-hidden='true' font-size='50px'></span></div><p class='lead text-center'>操作成功</p><br /><div class='text-center'><small>条目将在下一次推送时被推送</small>"
    document.getElementById('ModalContent').innerHTML = success
}

function postrefreshmodalerror() {
    var error = "<div class='text-center'><span class='glyphicon glyphicon-remove' aria-hidden='true' font-size='50px'></span></div><p class='lead text-center'>错误-请检查本日剩余条目推送次数</p>"
    document.getElementById('ModalContent').innerHTML = error
}
function delrefreshmodalsuccess() {
    var success = "<div class='text-center'><span class='glyphicon glyphicon-ok' aria-hidden='true' font-size='50px'></span></div><p class='lead text-center'>操作成功</p><br /><div class='text-center'><small>条目已被删除</small>"
    document.getElementById('ModalContent').innerHTML = success
}
function delrefreshmodalerror() {
    var error = "<div class='text-center'><span class='glyphicon glyphicon-remove' aria-hidden='true' font-size='50px'></span></div><p class='lead text-center'>错误-请稍候重试</p>"
    document.getElementById('ModalContent').innerHTML = error
}

function pushbtnclick(id,csrftoken) {
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken)
            }
        }
    })
    var PostVal = {
        "title": id,
        "action": "post"
    }
    $.ajax({
        type: 'POST',
        contentType: 'application/json',
        url: '/update',
        data: JSON.stringify(PostVal),
        success: postrefreshmodalsuccess,
        error: postrefreshmodalerror
    })
}
function delbtnclick(id,csrftoken) {
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken)
            }
        }
    })
    var PostVal = {
        "title": id,
        "action": "del"
    }
    $.ajax({
        type: 'POST',
        contentType: 'application/json',
        url: '/update',
        data: JSON.stringify(PostVal),
        success: delrefreshmodalsuccess,
        error: delrefreshmodalerror
    })
}
$(function() {
    $('#loadingModal').on('hide.bs.modal', function() {
        location.reload()
    })
})