function ShowLength( str ) {
    str = str.replace(/\r?\n/g,"");
    document.getElementById("inputlength").innerHTML = str.length + "文字";
 }