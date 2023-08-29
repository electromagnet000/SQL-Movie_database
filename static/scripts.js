window.onload = function() {
      var color = sessionStorage.getItem('color');
      if (color) {
        if (color == "#FBFBFB" )
            document.body.style.color = "black";
        else
            document.body.style.color = "white";


        document.body.style.backgroundColor = color;
      }

    }

function changeBackgroundColor(color) {
    document.body.style.background = color;
    if (color == "#FBFBFB" )
            document.body.style.color = "black";
        else
            document.body.style.color = "white";
    sessionStorage.setItem('color', color);
    }

function logout() {
    sessionStorage.clear();
    window.location.href = "/"
}


var myInput = document.getElementById("password");
var letter = document.getElementById("letter");
var capital = document.getElementById("capital");
var number = document.getElementById("number");
var length = document.getElementById("length");

// When the user clicks on the password field, show the message box
myInput.onfocus = function() {
  document.getElementById("message").style.display = "grid";
}

// When the user clicks outside of the password field, hide the message box
myInput.onblur = function() {
  document.getElementById("message").style.display = "none";
}

// When the user starts to type something inside the password field
myInput.onkeyup = function() {
  // Validate lowercase letters
  var lowerCaseLetters = /[a-z]/g;
  if(myInput.value.match(lowerCaseLetters)) {
    letter.classList.remove("invalid");
    letter.classList.add("valid");
  } else {
    letter.classList.remove("valid");
    letter.classList.add("invalid");
}

  // Validate capital letters
  var upperCaseLetters = /[A-Z]/g;
  if(myInput.value.match(upperCaseLetters)) {
    capital.classList.remove("invalid");
    capital.classList.add("valid");
  } else {
    capital.classList.remove("valid");
    capital.classList.add("invalid");
  }

  // Validate numbers
  var numbers = /[0-9]/g;
  if(myInput.value.match(numbers)) {
    number.classList.remove("invalid");
    number.classList.add("valid");
  } else {
    number.classList.remove("valid");
    number.classList.add("invalid");
  }

  // Validate length
  if(myInput.value.length >= 8) {
    length.classList.remove("invalid");
    length.classList.add("valid");
  } else {
    length.classList.remove("valid");
    length.classList.add("invalid");
  }
}

//
//var background = {
//
//white: #fff,
//reset: #1e1e1e
//
//}
//
//
//
//var key = sessionStorage.getItem ('key');
//var obj = JSON.parse(key);
//
//
//var settings = load_settings();
//setBackground(settings.background);
//
//document.getElementById("button_test").addEventListener("click", white_background)
//document.getElementById("button_reset").addEventListener("click", reset)
//
//function setBackground(background) {
//$('body').css("background-color", "background")
//localStorage.setItem("settings.background", background);
//}
//




