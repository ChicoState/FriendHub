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
        div.appendChild(img);
        carousel.appendChild(div);
    });
    new Flickity(carousel, {
      initialIndex: getCurPfp(),
      cellAlign: 'center',
      contain: true,
      wrapAround: true,
      selectedAttraction: .01,
      friction: .15
    });
    const allCells = document.querySelectorAll(".carousel-cell")
    allCells.forEach(cell => {
        cell.addEventListener("dblclick", (e) => {
            // remove the 'is-selected' class from all cells
            allCells.forEach(cell => {
                cell.classList.remove("is-selected");
            });
            // Add the 'is-selected' class to the clicked cell
            e.currentTarget.classList.add("is-selected");
            const iconForm = document.getElementById("id_icon");
            iconForm.value = e.currentTarget.querySelector('img').getAttribute("data-icon-id")
            document.getElementById("iconForm").submit();
        });
    });
}

$(".iconForm").sumit(function(e) {
    e.preventDefault();
});
// submit pfp selection
document.getElementById("pfpSubmit").addEventListener("click", () => {
    const selectedDiv = document.querySelector('.is-selected');
    if (selectedDiv) {
        const img = selectedDiv.querySelector('img');
        if(img) {
            const iconId = img.getAttribute("data-icon-id");
            const iconForm = document.getElementById("id_icon");
            iconForm.value = iconId
            document.getElementById("iconForm").submit();
        }
    } else {
        console.log('No selected element found.');
    }
})