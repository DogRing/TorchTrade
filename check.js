function checkOne(element){
    const checkboxes = document.getElementsByName("cate");
    const nowchecked=element.checked;

    checkboxes.forEach((cb)=>{cb.checked = false;});
    
    element.checked = nowchecked;
}