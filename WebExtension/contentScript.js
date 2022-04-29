// Creates base overlay element
let overlay = document.createElement("div");
overlay.style.position = "fixed";
overlay.style.display = "block";
overlay.style.width = "100%";
overlay.style.height = "100%";
overlay.style.zIndex = "998";
overlay.style.pointerEvents = "none";
overlay.setAttribute("id", "bolOverlay");

// Appends the overlay element as a child element after the <head> element
let htmlHead = document.querySelector("head");
htmlHead.parentNode.insertBefore(overlay, htmlHead.nextSibling);

let bolElement = document.createElement("div");
bolElement.style.position = "absolute";
bolElement.style.display = "block";
bolElement.style.width = "400px";
bolElement.style.height = "450px";
bolElement.style.right = "0";
bolElement.style.top = "25px";
bolElement.style.zIndex = "999";
bolElement.style.pointerEvents = "auto";
bolElement.style.backgroundColor = "#0000A4";
bolElement.setAttribute("id", "bolElement");

document.querySelector("#bolOverlay").appendChild(bolElement);
