window.onload = function() {
    var wpm = 0;
    var socket = io.connect('http://webtech-15.napier.ac.uk:5000');
    var public_indonesian = io('http://webtech-15.napier.ac.uk:5000/pub_id');

    var playerCount = 0;
    var players = [];
    socket.on('connect', function() {
        public_indonesian.send(name, wpm);
        for (var i = 0; players.length ; i++){
            let score = '<div class="lobby-user"><span class="t-dgrey">'+players[i]+'</span><div class="lobby-wpm"></div></div>';
            document.querySelector('.lobby').innerHTML += score;  
        }
    });

    // socket.on('message', function(msg) {
    //     chat.innerHTML += '<li>'+msg+'</li>';
    //     console.log("Message Recieved");
    // });

    public_indonesian.on('players', function(name){
        console.log(name);
        players.push(name);
    });

    public_indonesian.on('nPlayer', function(x){
        console.log(x);
        playerCount = x; 
    });
    
     
};