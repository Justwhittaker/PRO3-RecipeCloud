// modal -- Core code https://www.w3schools.com/howto/howto_css_modals.asp
// Get the modal
var modal = document.getElementById("myModal");

// Get the button that opens the modal
var btn = document.getElementById("myBtn");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks on the button, open the modal
btn.onclick = function () {
    modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
span.onclick = function () {
    modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function (event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}


function mainMenu() {
$('.dropdown-toggle').dropdown();
}

$(document).ready(function() {
  $("#myButton").click(function() {
    $("#myButton").after('<input type="text" id="textInput" value="">');
  });
});

$(document).ready(mainMenu);