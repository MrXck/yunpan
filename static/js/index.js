let instance = axios.create();
instance.defaults.headers['Content-Type'] = 'multipart/form-data';
instance.defaults.transformRequest = (data, headers) => {
    const contentType = headers['Content-Type'];
    if (contentType === "application/x-www-form-urlencoded") return Qs.stringify(data);
    return data;
};
instance.interceptors.response.use(response => {
    return response.data;
});


window.addEventListener('click', () => {
    vm.operationListShow = false;
})

$('body')[0].addEventListener('dragover', function (ev) {
    ev.preventDefault();
});


$('body')[0].addEventListener('drop', function (ev) {
    ev.preventDefault();
    for (var i = 0; i < ev.dataTransfer.items.length; i++) {
        var item = ev.dataTransfer.items[i];
        if (item.kind === "file" && item.webkitGetAsEntry().isFile) {
            if (item.getAsFile().size > 1024 * 1024 * 100) {
                vm.bigFile(item.getAsFile())
            } else {
                vm.upload_file(item.getAsFile());
            }
        } else if (item.kind === "file" && item.webkitGetAsEntry().isDirectory) {
            scan_dir(item.webkitGetAsEntry())
        }
    }
});

function scan_dir(item) {
    let dirReader = item.createReader()
    dirReader.readEntries(entries => {
        for (let i = 0; i < entries.length; i++) {
            if (entries[i].isFile) {
                entries[i].file(file => {
                    if (file.size > 1024 * 1024 * 100) {
                        vm.bigFile(file)
                    } else {
                        vm.upload_file(file);
                    }
                })
            } else if (entries[i].isDirectory) {
                scan_dir(entries[i])
            }
        }
    })
}


let mouseDown = false;
(function () {
    let main = $('.main')
    main[0].onmousedown = function () {
        mouseDown = true
        var selList = [];
        var fileNodes = document.getElementsByClassName("item");
        for (var i = 0; i < fileNodes.length; i++) {
            if (fileNodes[i].className.indexOf("item") !== -1) {
                fileNodes[i].className = "item";
                selList.push(fileNodes[i]);
            }
        }
        var isSelect = true;
        var evt = window.event || arguments[0];
        var startX = (evt.x || evt.clientX);
        var startY = (evt.y || evt.clientY);
        var selDiv = document.createElement("div");
        selDiv.style.cssText = "position:absolute;width:0px;height:0px;font-size:0px;margin:0px;padding:0px;border:1px solid #0099FF;background-color:#C3D5ED;z-index:1000;filter:alpha(opacity:60);opacity:0.6;display:none;";
        selDiv.id = "selectDiv";
        document.body.appendChild(selDiv);
        selDiv.style.left = startX + "px";
        selDiv.style.top = startY + "px";
        var _x = null;
        var _y = null;
        clearEventBubble(evt);
        document.onmousemove = function () {
            if (mouseDown) {
                evt = window.event || arguments[0];
                if (isSelect) {
                    if (selDiv.style.display === "none") {
                        selDiv.style.display = "";
                    }
                    _x = (evt.x || evt.clientX);
                    _y = (evt.y || evt.clientY);
                    selDiv.style.left = Math.min(_x, startX) + "px";
                    selDiv.style.top = Math.min(_y, startY) + "px";
                    selDiv.style.width = Math.abs(_x - startX) + "px";
                    selDiv.style.height = Math.abs(_y - startY) + "px";
                    // ---------------- 关键算法 ---------------------
                    let selDivRect = selDiv.getBoundingClientRect();
                    const left1 = selDivRect.left;
                    const right1 = selDivRect.left + selDivRect.width;
                    const top1 = selDivRect.top;
                    const bottom1 = selDivRect.top + selDivRect.height;
                    const width1 = selDivRect.width;
                    const height1 = selDivRect.height;
                    for (let i = 0; i < selList.length; i++) {
                        const itemRect = selList[i].getBoundingClientRect()
                        const left2 = itemRect.left;
                        const right2 = itemRect.left + itemRect.width;
                        const top2 = itemRect.top;
                        const bottom2 = itemRect.top + itemRect.height;
                        const width2 = itemRect.width;
                        const height2 = itemRect.height;
                        if (!(left2 > right1 || left1 > right2 || bottom1 < top2 || bottom2 < top1 || width1 <= 0 || width2 <= 0 || height1 <= 0 || height2 <= 0)) {
                            if (selList[i].className.indexOf("seled") === -1) {
                                selList[i].className = selList[i].className + " seled";
                            }
                        } else {
                            if (selList[i].className.indexOf("seled") !== -1) {
                                selList[i].className = "item";
                            }
                        }
                    }
                }
                clearEventBubble(evt);
            }
        }
        document.onmouseup = function () {
            mouseDown = false
            isSelect = false;
            if (selDiv) {
                document.body.removeChild(selDiv);
                showSelDiv(selList);
            }
            selList = null, _x = null, _y = null, selDiv = null, startX = null, startY = null, evt = null;
        }
    }
})();

function clearEventBubble(evt) {
    if (evt.stopPropagation)
        evt.stopPropagation();
    else
        evt.cancelBubble = true;
    if (evt.preventDefault)
        evt.preventDefault();
    else
        evt.returnValue = false;
}

function showSelDiv(arr) {
    vm.dragMoveList = []
    vm.operationList = []
    for (var i = 0; i < arr.length; i++) {
        if (arr[i].className.indexOf("seled") !== -1) {
            vm.dragMoveList.push($(arr[i]).find('input').val())
            vm.operationList.push($(arr[i]).find('input').val())
        }
    }
}


document.body.addEventListener('keyup', (e)=>{
    if (e.key === 'Delete'){
        vm.deleteModal = true
    }
})


$(function (){
    $('.main').css('min-height', document.documentElement.clientHeight - parseInt($('.navbar-dark').css('height').replace('px', '')) - 50 - 36)
})
window.onresize = () => {
    return (() => {
        $('.main').css('min-height', document.documentElement.clientHeight - parseInt($('.navbar-dark').css('height').replace('px', '')) - 50 - 36)
    })()
}
