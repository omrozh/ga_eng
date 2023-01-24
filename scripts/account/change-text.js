window.previous = 0
function getRandomInt(max) {
    let random_out = Math.floor(Math.random() * max)

    while(random_out === window.previous){
        random_out = Math.floor(Math.random() * max)
    }

    return random_out
}
slogan_words = [" share ", " discuss ", " chat "]
function changeSlogan(){
    let random_text = getRandomInt(3)
    window.previous = random_text
    document.getElementById("slogan-word").innerText = slogan_words[random_text]
    document.getElementById("slogan-word").style.color = "#007de0"
    setTimeout(resetBgSlogan, 1000)
}
function resetBgSlogan(){
    document.getElementById("slogan-word").style.color = "black"
}
setInterval(changeSlogan, 3000)
