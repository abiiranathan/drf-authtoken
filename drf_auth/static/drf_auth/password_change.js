var form = document.getElementById("password-form");
var password1 = document.getElementById("password1");
var password2 = document.getElementById("password2");
var successOutput = document.getElementById("success-output");
var errorOutput = document.getElementById("error-output");

var endpoint = window.location.href;

form.addEventListener("submit", function (e) {
  e.preventDefault();

  var pswd1 = password1.value;
  var pswd2 = password2.value;

  if (pswd1 === pswd2) {
    successOutput.innerHTML = "";
    errorOutput.innerHTML = "";

    fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        password: pswd1,
      }),
    })
      .then(function (res) {
        if (res.status == 200) {
          return res.json();
        }
        throw new Error(res.statusText);
      })
      .then(handleSuccess)
      .catch(handleError);
  } else {
    alert("Passwords do not match!");
  }
});

function handleSuccess(data) {
  successOutput.innerHTML = "Your password has been reset. Go ahead and login!";
  errorOutput.innerHTML = "";
}

function handleError(err) {
  successOutput.innerHTML = "";
  errorOutput.innerHTML =
    "Password token has expired or is already used! Try resetting your password again";
}
