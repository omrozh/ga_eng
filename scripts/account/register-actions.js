window.registration_step = 0

function proceedRegistration(){
    document.getElementById("form-inputs-1").style.display = "none"
    document.getElementById("form-inputs-2").style.display = "block"
    if(window.registration_step === 1){
        const xhr = new XMLHttpRequest();
        xhr.open("POST", '/post/register', true);
        xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        xhr.onreadystatechange = () => {
          if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
              if(xhr.responseText === "Registered"){
                  document.location = "/account/login"
              }
              document.getElementById("alerts-div").innerText = xhr.responseText
          }
        }
        let username = document.getElementById('username').value
        let password = document.getElementById('password').value
        let email = document.getElementById('email').value
        let phone_number = document.getElementById('phone_number').value

        xhr.send(`username=${username}&password=${password}&email=${email}&phone_number=${phone_number}`);
    }
    else{
        window.registration_step++
    }
}
