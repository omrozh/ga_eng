function constructPosts(data){
    if(data.length === 0){
        let newDiv = ""
        getPostsUnauth()
    }


    for(let i = 0; i < data.length; i++){
        let data_temp = data[i]
        let newDiv = ""
        if(data_temp["has_image"]){
            newDiv = `<div onclick="document.location = '/view-post/${data_temp["post_id"]}'" class="news-feed load-more" style="margin-top: 90px; padding-left: 15px;">
              <div style="position: relative; top: 20px; float: right; margin-right: 15px; z-index: 0">
                  <i style="font-size: 1.5rem; margin-right: 10px; color: gray" class="fa-solid fa-rocket"></i>
                  <span>${data_temp["net_votes"]}</span>
                    <i style="margin-left: 10px; font-size: 1.5rem; color: gray" class="fa-solid fa-fire-flame-simple"></i>
              </div>
                <p style="color: gray">@${data_temp["creator_username"]}</p>
                <h1>${data_temp["title"]}</h1>
              <p>${data_temp["text_body"]}</p>
              <img src="${data_temp["image_uri"]}" style="width: 100%;" alt="">
          </div>`
        }
        else if(!data_temp["has_image"]){
            newDiv = `<div onclick="document.location = '/view-post/${data_temp["post_id"]}'" class="news-feed load-more" style="margin-top: 90px; padding-left: 15px;">
              <div style="position: relative; top: 20px; float: right; margin-right: 15px; z-index: 0">
                  <i style="font-size: 1.5rem; margin-right: 10px; color: gray" onclick="document.location = '/moonvote/${data_temp["post_id"]}'" class="fa-solid fa-rocket"></i>
                  <span>${data_temp["net_votes"]}</span>
                    <i style="margin-left: 10px; font-size: 1.5rem; color: gray" onclick="document.location = '/hellvote/${data_temp["post_id"]}'" class="fa-solid fa-fire-flame-simple"></i>
              </div>
                <p style="color: gray">@${data_temp["creator_username"]}</p>
                <h1>${data_temp["title"]}</h1>
              <p>${data_temp["text_body"]}</p>
          </div>`
        }
        document.body.innerHTML += newDiv
    }
}

function addTags(data){
    let tags_ul = document.getElementById("tags-trending")
    for(let i = 0; i < data.length; i++){
        tags_ul.innerHTML += `<li onclick="document.location = '/tags/${data[i].replace('#', '')}'">${data[i]}</li>`
    }
}

function topHeaders(data){
    let tags_ul = document.getElementById("top-headers")
    for(let i = 0; i < data.length; i++){
        tags_ul.innerHTML += `<li><a style="color: black" href="/view-post/${data[i]["post_id"]}"><strong>${data[i]["title"]}</strong></a></li>`
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
    fetch('/unauthenticated/load-post-batch')
  .then((response) => response.json())
  .then((data) => topHeaders(data));
}

function getPostsAuth(){
    fetch('/authenticated/load-post-batch/0')
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
}

function searchTags(){
    let searchTerm = document.getElementById("search-input").value;
    if(searchTerm.length > 2){
        searchFetch(searchTerm)
    }
    else{
        clearSearch()
    }
}


function addSearchTerms(data){
    for(let i = 0; i < data.length; i++){
        document.getElementById("search-results").innerHTML = `<li onclick="document.location = '/tags/' + '${data[i].replace('#', '')}'">${data[i]}</li>`
    }
}

function searchFetch(tag_name){
    fetch('/tags/search/' + tag_name)
  .then((response) => response.json())
  .then((data) => addSearchTerms(data));
}