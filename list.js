const listForm = document.querySelector(".listarea"),
    shopList = document.querySelector(".list"),
    searchB = document.querySelector(".search"),
    maparea = document.querySelector(".map");

let data = [
    // 맛 서비스 분위기 청결도 가격
    {Lan : 37.507106, Lon : 126.95881, name : "Rice and Potato",    1:5, 2:3, 3:2, 4:3, 5:4},
    {Lan : 37.507403, Lon : 126.958866, name : "junhone",           1:3, 2:4, 3:3, 4:3, 5:4},
    {Lan : 37.507279, Lon : 126.959083, name : "yangchef",          1:4, 2:3, 3:3, 4:3, 5:3},
    {Lan : 37.507633, Lon : 126.959831, name : "appletree",         1:2, 2:2, 3:2, 4:2, 5:2},
    {Lan : 37.504896, Lon : 126.953254, name : "gogopocha",         1:3, 2:3, 3:4, 4:2, 5:2},
    {Lan : 37.505154, Lon : 126.951959, name : "cheahong",          1:5, 2:2, 3:4, 4:4, 5:2},
    {Lan : 37.504749, Lon : 126.951411, name : "bonggous",         1:2, 2:2, 3:2, 4:2, 5:2},
    {Lan : 37.504729, Lon : 126.950804, name : "nurungzi",         1:2, 2:2, 3:2, 4:2, 5:2}
]

function refreshList(){
    deleteList();
    sortList();
    paintList();
}

function deleteList(){
    for(var i =0;i<data.length;i++){
        let item = document.getElementById(i);
        shopList.removeChild(item);
    }
}

function sortList(){
    let obj_length = document.getElementsByName("cate").length;

    let selected=0;
    for (var i=0; i<obj_length; i++) {
        if (document.getElementsByName("cate")[i].checked == true) {
            selected = document.getElementsByName("cate")[i].value;
        }
    }
    if (selected === 0){
        return ;
    }
    data.sort(function(a,b){
        return a[selected] > b[selected] ? -1 : a[selected] < b[selected] ? 1 : 0;
    });
}

function deleteDetail(event){
    const btn = event.target;
    const page = btn.parentNode;
    maparea.removeChild(page);
    nowOpen = null;
}

function showDetail(i){
    let nowOpen = maparea.querySelector(".detail");
    if(nowOpen !== null){
        maparea.removeChild(nowOpen);
    }
    const h2 = document.createElement("h2");
    h2.innerText = data[i].name;
    const delbtn = document.createElement("button");
    delbtn.addEventListener("click",deleteDetail);
    delbtn.innerText = "X";
    const div = document.createElement("div");
    div.className = "detail";
    div.appendChild(h2);
    div.appendChild(delbtn);
    maparea.appendChild(div);
}

function paintList(){
    for(let i=0;i< data.length;i++){
        const li = document.createElement("div");
        li.innerText = data[i].name;
        li.id = i;
        li.addEventListener("click",function(text){showDetail(i);});
        li.className = "shop";
        shopList.appendChild(li);
    }
}

function makeMarker(){
    for(var i=0;i<data.length;i++){
    
        let marker = new kakao.maps.Marker({
            position: new kakao.maps.LatLng(data[i].Lan, data[i].Lon), // 마커의 좌표
            map: map // 마커 표시
        });
        let infocontent = `<div class = "mapinfo">${data[i].name}</div>`;
        let infowindow = new kakao.maps.InfoWindow({content:infocontent});
        kakao.maps.event.addListener(marker,'mouseover',overListener(map,marker,infowindow));
        kakao.maps.event.addListener(marker,'mouseout',outListener(infowindow));
    }
}

function overListener(map,marker,infowindow){
    return function(){
        infowindow.open(map,marker);
    };
}
function outListener(infowindow){
    return function(){
        infowindow.close();
    };
}

makeMarker();
searchB.addEventListener("click", refreshList);
paintList();