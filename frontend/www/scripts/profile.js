async function updateProfile(event) {
  let form = document.querySelector("#form-update-user");
  let formData = new FormData(form);
  let body = {
    username: formData.get("username"),
    phone_number: formData.get("phone_number"),
    country: formData.get("country"),
    city: formData.get("city"),
    street_address: formData.get("street_address"),
  };
  let response = await sendRequest(
    "PATCH",
    `${HOST}/api/users/` + sessionStorage.getItem("username") + "/",
    body
  );

  if (!response.ok) {
    let data = await response.json();
    let alert = createAlert("Save failed!", data);
    document.body.prepend(alert);
  } else {
    // TODO feedback
    console.log("updated");
    sessionStorage.setItem(
      "username",
      document.querySelector('input[name="username"]').value
    );
    let alert = createSuccessAlert("Save succeded!");
    document.body.prepend(alert);
  }
}

// Fill profile page
async function getProfile() {
  let response = await sendRequest(
    "GET",
    `${HOST}/api/users/` + sessionStorage.getItem("username")
  );
  let data = await response.json();
  document.querySelector('input[name="phone_number"]').value =
    data.phone_number;
  document.querySelector('input[name="username"]').value = data.username;
  document.querySelector('input[name="street_address"]').value =
    data.street_address;
  document.querySelector('input[name="country"]').value = data.country;
  document.querySelector('input[name="city"]').value = data.city;
  document.querySelector('input[name="email"]').value = data.email;
}

function openModal() {
  document.getElementById("backdrop").style.display = "block";
  document.getElementById("exampleModal").style.display = "block";
  document.getElementById("exampleModal").classList.add("show");
}
function closeModal() {
  document.getElementById("backdrop").style.display = "none";
  document.getElementById("exampleModal").style.display = "none";
  document.getElementById("exampleModal").classList.remove("show");
}
// Get the modal
var modal = document.getElementById("exampleModal");

// When the user clicks anywhere outside of the modal, close it
window.onclick = function (event) {
  if (event.target == modal) {
    closeModal();
  }
};

async function deleteProfile() {
  let form = document.querySelector("#form-update-user");
  let formData = new FormData(form);

  let response = await sendRequest(
    "DELETE",
    `${HOST}/api/users/` + sessionStorage.getItem("username") + "/",
    formData,
    ""
  );

  if (!response.ok) {
    let data = await response.json();
    let alert = createAlert("Delete failed!", data);
    document.body.prepend(alert);
  } else {
    // TODO feedback
    console.log("updated");
    sessionStorage.setItem(
      "username",
      document.querySelector('input[name="username"]').value
    );
    let alert = createSuccessAlert("Delete succeded!");
    document.body.prepend(alert);
    deleteCookie("access");
    deleteCookie("refresh");
    deleteCookie("remember_me");
    sessionStorage.removeItem("username");
    window.location.replace("index.html");
  }
}

document
  .querySelector("#btn-update-account")
  .addEventListener("click", async (event) => await updateProfile(event));

document
  .querySelector("#btn-delete-account")
  .addEventListener("click", async (event) => await openModal(event));

window.addEventListener("DOMContentLoaded", () => {
  getProfile();
});
