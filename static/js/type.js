

//var myVar = setInterval(myTimer, 1000);
var time = 15;
function myTimer() {
    var d = new Date();
    
    if (time > 0 ) {
        time--;
    }

    document.getElementById("timer").innerHTML = time + 's';

    if (time == 0 && testOn == true) {
        alert((cChar-1)/15*60/5);
        testOn = false;
    }
}

var testOn = false; // test default state

let cChar = 0, // correct characters
    xChar = 0, // current character / variable
    tChar = document.querySelectorAll("#c");

function check(event){
    if (testOn == false ){
        testOn = true;

        setInterval(myTimer, 1000);
    }
    
    //console.log("Timer Start");

    // check first character
    let x = event.which;

    // console.log(event);
    if (x == ''){
        x = ' ';
    }

    if (String.fromCharCode(x) != t.charAt(xChar)){ // check if wrong key is entered
        console.log("no");
        tChar[xChar].style.color = "red";
        xChar++;
    } else{ // correct key entered
        console.log("correct");
        tChar[xChar].style.color = "green";
        cChar++;
        xChar++;
    }
}

function checkBackspace(event){
    let key = event.key;
    if (key == 'Backspace' && xChar > 0){
        
        tChar[xChar-1].style.color = "var(--lighter)";

        if (xChar == cChar){
            cChar--;
        }

        xChar--;
        console.log("backspace hit", xChar);
    } 
    console.log({"current":xChar,'correct':cChar,'event.which':String.fromCharCode(event.which),"test char":t.charAt(xChar),"event.key":event.key});

}
