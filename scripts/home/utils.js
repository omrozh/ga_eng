window.pagination = 0

function constructPosts(data){
    if(data.length === 0 && window.pagination === 0){
        let newDiv = ""
        getPostsUnauth()
    }


    for(let i = 0; i < data.length; i++){
        let data_temp = data[i]
        let newDiv = ""
        if(data_temp["has_image"]){
            if(!data_temp["is_video"]){
                newDiv = `<div onclick="document.location = '/view-post/${data_temp["post_id"]}'" class="news-feed load-more" style="margin-top: 70px; padding-left: 15px;">
                  <div style="position: relative; top: 20px; float: right; margin-right: 15px; z-index: 0">
                      <i style="font-size: 1.5rem; margin-right: 10px; color: gray" class="fa-solid fa-arrow-trend-up"></i>
                      <span>${data_temp["net_votes"]}</span>
                        <i style="margin-left: 10px; font-size: 1.5rem; color: gray" class="fa-solid fa-arrow-trend-down"></i>
                  </div>
                    <p style="color: gray" onclick="document.location = '/account/${data["creator_username"]}'">@${data_temp["creator_username"]}</p>
                    <h1>${data_temp["title"]}</h1>
                  <p>${data_temp["text_body"]}</p>
                  <img src="${data_temp["image_uri"]}" style="width: 100%; border-radius: 15px" alt="">
                  <p style="color: gray">Devamını Oku</p>
              </div>`
            }
            else if(data_temp["is_video"]){
                newDiv = `<div class="news-feed load-more" style="margin-top: 70px; padding-left: 15px;">
                  <div  onclick="document.location = '/view-post/${data_temp["post_id"]}'" style="position: relative; top: 20px; float: right; margin-right: 15px; z-index: 0">
                      <i style="font-size: 1.5rem; margin-right: 10px; color: gray" class="fa-solid fa-arrow-trend-up"></i>
                      <span>${data_temp["net_votes"]}</span>
                        <i style="margin-left: 10px; font-size: 1.5rem; color: gray" class="fa-solid fa-arrow-trend-down"></i>
                  </div>
                    <p style="color: gray" onclick="document.location = '/account/${data["creator_username"]}'">@${data_temp["creator_username"]}</p>
                    <h1  onclick="document.location = '/view-post/${data_temp["post_id"]}'">${data_temp["title"]}</h1>
                  <p>${data_temp["text_body"]}</p>
                  <a onclick="document.location = '/view-post/${data_temp["post_id"]}'" style="color: dodgerblue; text-decoration: none">Videoyu izlemek için tıkla</a>
                  <p style="color: gray">Devamını Oku</p>
              </div>`
            }
        }
        else if(!data_temp["has_image"]){
            newDiv = `<div onclick="document.location = '/view-post/${data_temp["post_id"]}'" class="news-feed load-more" style="margin-top: 70px; padding-left: 15px;">
              <div style="position: relative; top: 20px; float: right; margin-right: 15px; z-index: 0">
                  <i style="font-size: 1.5rem; margin-right: 10px; color: gray" onclick="document.location = '/moonvote/${data_temp["post_id"]}'" class="fa-solid fa-arrow-trend-up"></i>
                  <span>${data_temp["net_votes"]}</span>
                    <i style="margin-left: 10px; font-size: 1.5rem; color: gray" onclick="document.location = '/hellvote/${data_temp["post_id"]}'" class="fa-solid fa-arrow-trend-down"></i>
              </div>
                <p style="color: gray">@${data_temp["creator_username"]}</p>
                <h1>${data_temp["title"]}</h1>
              <p>${data_temp["text_body"]}</p>
              <p style="color: gray">Devamını Oku</p>
          </div>`
        }
        if(data_temp["has_test"]){
            newDiv = `<div class="news-feed load-more" style="margin-top: 70px; padding-left: 15px;">
                  <div  onclick="document.location = '/view-post/${data_temp["post_id"]}'" style="position: relative; top: 20px; float: right; margin-right: 15px; z-index: 0">
                      <i style="font-size: 1.5rem; margin-right: 10px; color: gray" class="fa-solid fa-arrow-trend-up"></i>
                      <span>${data_temp["net_votes"]}</span>
                        <i style="margin-left: 10px; font-size: 1.5rem; color: gray" class="fa-solid fa-arrow-trend-down"></i>
                  </div>
                    <p style="color: gray" onclick="document.location = '/account/${data["creator_username"]}'">@${data_temp["creator_username"]}</p>
                    <h1  onclick="document.location = '/view-post/${data_temp["post_id"]}'">${data_temp["title"]}</h1>
                  <p>${data_temp["text_body"]}</p>
                  <img src="${data_temp["image_uri"]}" style="width: 100%; border-radius: 15px" alt="">
                  <a onclick="document.location = '/view-post/${data_temp["post_id"]}'" style="color: dodgerblue; text-decoration: none">Testi çözmek için tıkla</a>
                  <p style="color: gray">Devamını Oku</p>
              </div>`
        }
        document.body.innerHTML += newDiv
    }
}

function addTags(data){
    let tags_ul = document.getElementById("tags-trending")
    for(let i = 0; i < data.length; i++){
        tags_ul.innerHTML += `<li onclick="document.location = '/tags/${data[i].replace('#', '')}'">${data[i]}</li><br>`
    }
}

function topHeaders(data){
    let tags_ul = document.getElementById("top-headers")
    for(let i = 0; i < data.length; i++){
        tags_ul.innerHTML += `<li><a style="color: white; text-decoration: none" href="/view-post/${data[i]["post_id"]}"><strong>${data[i]["title"]}</strong></a></li><br>`
    }
}

function getPostsUnauth(){
    fetch('/unauthenticated/load-post-batch')
  .then((response) => response.json())
  .then((data) => constructPosts(data));
}

function getPostsFromTag(tag_name){
    fetch('/view-tag/' + tag_name)
  .then((response) => response.json())
  .then((data) => constructPosts(data));
}

function getPostsTopPosts(){
    fetch('/top_headers/load-post-batch')
  .then((response) => response.json())
  .then((data) => topHeaders(data));
}


function getPostsAuth(){
    window.onscroll = function(ev) {
        if ((window.innerHeight + window.pageYOffset) >= document.body.offsetHeight) {
            window.pagination += 1
            getPostsAuth()
        }
    };
    fetch('/authenticated/load-post-batch/' + window.pagination)
  .then((response) => response.json())
  .then((data) => constructPosts(data));
}


function getTrendingTags(){
    fetch('/get_trending_tags')
  .then((response) => response.json())
  .then((data) => addTags(data));
}

function clearSearch(){
    document.getElementById("search-results").innerHTML = ""
    document.getElementById("search-results").style.display = "none"
}

function searchTags(){
    let searchTerm = document.getElementById("search-input").value;
    clearSearch()
    document.getElementById("search-results").style.display = "block"
    if(searchTerm.length > 2){
        searchFetch(searchTerm)
    }
    else{
        clearSearch()
    }
}

function adSearch(){
    let searchTerm = document.getElementById("search-input").value;
    clearSearch()
    document.getElementById("search-results").style.display = "block"
    if(searchTerm.length > 2){
        adSearchFetch(searchTerm)
    }
    else{
        clearSearch()
    }
}

function adSearchFetch(tag_name){
    fetch('/tags/search/' + tag_name)
  .then((response) => response.json())
  .then((data) => adAddSearchTerms(data));
}


function adAddSearchTerms(data){
    for(let i = 0; i < data.length; i++){
        if(data[i].includes("@")){
            document.getElementById("search-results").innerHTML += `<li onclick="advert_include('${data[i]}')">${data[i]}</li>`
        }
    }
}

function advert_include(username){
    document.getElementById("creators-alike").value += username + "&&"
    document.getElementById("search-input").value = ""
    document.getElementById("selected-creators").innerHTML += `<li class="remove-creator" onclick="removeCreator('${username}')">${username}</li>`
    clearSearch()
}

function removeCreator(username){
    document.getElementById("selected-creators").innerHTML = document.getElementById("selected-creators").innerHTML.replace(`<li class="remove-creator" onclick="removeCreator('${username}')">${username}</li>`, '')
    document.getElementById("creators-alike").value = document.getElementById("creators-alike").value.replace(username + "&&", '')
}


function addSearchTerms(data){
    for(let i = 0; i < data.length; i++){
        if(data[i].includes("@")){
            document.getElementById("search-results").innerHTML += `<li onclick="document.location = '/account/' + '${data[i].replace('@', '')}'">${data[i]}</li>`
        }
        else{
            document.getElementById("search-results").innerHTML += `<li onclick="document.location = '/tags/' + '${data[i].replace('#', '')}'">${data[i]}</li>`
        }
    }
}

function searchFetch(tag_name){
    fetch('/tags/search/' + tag_name)
  .then((response) => response.json())
  .then((data) => addSearchTerms(data));
}
