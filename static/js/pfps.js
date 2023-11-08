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
    const Flick = new Flickity(carousel, {
      initialIndex: getCurPfp(),
      cellAlign: 'center',
      contain: true,
      wrapAround: true,
      selectedAttraction: .01,
      friction: .15
    });
    const allCells = document.querySelectorAll(".carousel-cell")
    allCells.forEach(cell => {
        // cell.addEventListener('click', (e) => handleEvent(e, Flick), false);
        cell.addEventListener('dblclick', (e) => handleEvent(e, Flick), false);
    });
}

function handleEvent(e, Flick) {
    const iconForm = document.getElementById("id_icon");
    const imgNum = e.currentTarget.querySelector('img').getAttribute("data-icon-id")
    Flick.select(imgNum);
    Flick.reloadCells()
    iconForm.value = imgNum
    document.getElementById("iconForm").submit();
}