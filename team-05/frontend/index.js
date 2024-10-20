"use strict";

const buttonAbout = document.getElementById("about");
const buttonChecking = document.getElementById("checking");

buttonAbout.addEventListener("click", () => {
  location.href = "about.html";
});

buttonChecking.addEventListener("click", () => {
  location.href = "checking.html";
});
