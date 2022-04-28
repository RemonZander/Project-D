// // Creates base overlay element
let overlay = document.createElement("div");
overlay.style.position = "fixed";
overlay.style.display = "block";
overlay.style.width = "100%";
overlay.style.height = "100%";
overlay.style.zIndex = "999";
overlay.style.pointerEvents = "none";
overlay.style.backgroundColor = "red";

// // Appends the overlay element as a child to the html element
document.querySelector("html").appendChild(overlay);

alert("Changed content");
