async function updateProfile(event) {
  let form = document.querySelector("#form-update-user");
  let formData = new FormData(form);

  let response = await sendRequest(
    "PATCH",
    `${HOST}/api/users/` + sessionStorage.getItem("username") + "/",
    formData,
    ""
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
  .addEventListener("click", async (event) => await deleteProfile(event));

window.addEventListener("DOMContentLoaded", () => {
  getProfile();
});
