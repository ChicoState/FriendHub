document.addEventListener("DOMContentLoaded", function() {
    // Fetch the icons JSON data and initialize the carousel
    fetch('../static/json/pfps.json')
        .then(response => response.json())
        .then(data => {
            initializeCarousel(data);
        });
});

function initializeCarousel(data) {
    const carousel = document.getElementById('carousel');
    // Clear out any existing children just in case
    carousel.innerHTML = '';
    // loop over the json data and create the images
    Object.keys(data).forEach(key => {
        let div = document.createElement('div');
        div.className = 'carousel-cell';
        let img = document.createElement('img');
        img.src = data[key];
        img.dataset.iconId = key;
        if(key == getCurPfp()) {
            img.style.border = "3px groove black"
            img.style.background = "rgb(242, 242, 242)"
        }
        div.appendChild(img);
        carousel.appendChild(div);
    });
    // create carousel
    const Flick = new Flickity(carousel, {
      initialIndex: getCurPfp(),
      cellAlign: 'center',
      contain: true,
      wrapAround: true,
      selectedAttraction: .01,
      friction: .15
    });
    const allCells = document.querySelectorAll(".carousel-cell")
    // for each image, add a double click event listener, and if something is double clicked on handle the event in the handleEvent function
    allCells.forEach(cell => {
        cell.addEventListener('dblclick', (e) => handleEvent(e, Flick), false);
    });
}

function handleEvent(e, Flick) {
    // get form
    const iconForm = document.getElementById("id_icon");
    // get the img ID of the image that was doubel clicked
    const imgNum = e.currentTarget.querySelector('img').getAttribute("data-icon-id");
    // if the img ID is the current Pfp don't do anything
    if(imgNum == getCurPfp()) return;
    // put in the current imgID in the form
    iconForm.value = imgNum;
    // submit form :P
    document.getElementById("iconForm").submit();
}