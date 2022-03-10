async function fetchMeals(ordering) {
    let response = await sendRequest("GET", `${HOST}/api/meals/?ordering=${ordering}`);

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    } else {
        let data = await response.json();

        let meals = data.results;
        let container = document.getElementById('div-content');
        meals.forEach(meal => {
            let templateMeal = document.querySelector("#template-meal");
            let cloneMeal = templateMeal.content.cloneNode(true);

            let aMeal = cloneMeal.querySelector("a");
            aMeal.href = `meal.html?id=${meal.id}`;

            let h5 = aMeal.querySelector("h5");
            h5.textContent = meal.name;

            let localDate = new Date(meal.date);

            let table = aMeal.querySelector("table");
            let rows = table.querySelectorAll("tr");
            rows[0].querySelectorAll("td")[1].textContent = localDate.toLocaleDateString(); // Date
            rows[1].querySelectorAll("td")[1].textContent = localDate.toLocaleTimeString(); // Time
            rows[2].querySelectorAll("td")[1].textContent = meal.owner_username; //Owner

            container.appendChild(aMeal);
        });
        return meals;
    }
}

function createMeal() {
    window.location.replace("meal.html");
}

window.addEventListener("DOMContentLoaded", async () => {
    let createButton = document.querySelector("#btn-create-meal");
    createButton.addEventListener("click", createMeal);
    let ordering = "-date";

    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('ordering')) {
        let aSort = null;
        ordering = urlParams.get('ordering');
        if (ordering == "name" || ordering == "owner" || ordering == "date") {
                let aSort = document.querySelector(`a[href="?ordering=${ordering}"`);
                aSort.href = `?ordering=-${ordering}`;
        } 
    } 

    let currentSort = document.querySelector("#current-sort");
    currentSort.innerHTML = (ordering.startsWith("-") ? "Descending" : "Ascending") + " " + ordering.replace("-", "");

    let currentUser = await getCurrentUser();
    // grab username
    if (ordering.includes("owner")) {
        ordering += "__username";
    }
    let meals = await fetchMeals(ordering);
    
    let tabEls = document.querySelectorAll('a[data-bs-toggle="list"]');
    for (let i = 0; i < tabEls.length; i++) {
        let tabEl = tabEls[i];
        tabEl.addEventListener('show.bs.tab', function (event) {
            let mealAnchors = document.querySelectorAll('.meal');
            for (let j = 0; j < meals.length; j++) {
                // I'm assuming that the order of meal objects matches
                // the other of the meal anchor elements. They should, given
                // that I just created them.
                let meal = meals[j];
                let mealAnchor = mealAnchors[j];

                switch (event.currentTarget.id) {
                    case "list-my-meals-list":
                        if (meal.owner == currentUser.url) {
                            mealAnchor.classList.remove('hide');
                        } else {
                            mealAnchor.classList.add('hide');
                        }
                        break;
                    default :
                        mealAnchor.classList.remove('hide');
                        break;
                }
            }
        });
    }
});