


window.onload = function(){
    const fsLibrary  = require('fs')
 
    fsLibrary.readFile('ind.txt', (error, txtString) => {
     
        if (error) throw err;
     
        console.log(txtString.toString());
     
    })
};
