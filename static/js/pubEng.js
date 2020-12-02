window.onload = function() {
    var wpm = 0;
    var socket = io.connect('http://webtech-15.napier.ac.uk:5000');
    var public_english = io('http://webtech-15.napier.ac.uk:5000/pub_eng');

    socket.on('connect', function() {
        public_english.send(name, wpm);
    });

    // socket.on('message', function(msg) {
    //     chat.innerHTML += '<li>'+msg+'</li>';
    //     console.log("Message Recieved");
    // });
    
    document.getElementById("sendBtn").onclick =  function() {
        socket.send(username + ': '+ input.value);
        input.value = "";
        console.log("button CLick");
    };
};