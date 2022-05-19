if (!document.querySelector("#bolOverlay")) {
	console.log("opened");
	const elementFromHtml = (html) => {
		const template = document.createElement("template");

		template.innerHTML = html.trim();

		return template.content.firstElementChild;
	};

	const bolElement = elementFromHtml(`
		<div id="bolOverlay">
			<div id="bolElement">
				<div id="bolElHeader">
					<div id="bolLogo">
						<p id="bolLogoMainText">Bol.com</p>
						<p id="bolLogoExtText">Extension</p>
					</div>
					<div id="bolSearchBar">
						<input id="bolSearchInput" class="noWrap" placeholder="Filter"/>
						<div id="bolSearchBtn"><p id="bolSearchIcon">🔍</p></div>
					</div>
					<div id="bolElCloseBtn">
						<svg width="15" height="15">
							<line x1="0" y1="0" x2="15" y2="15" stroke="#ffffff" stroke-width="2px"/>
							<line x1="15" y1="0" x2="0" y2="15" stroke="#ffffff" stroke-width="2px"/>
						</svg>
					</div>
				</div>
				<div id="bolElBody">
				</div>
			</div>
		</div>
	`);

	const elementArray = [
		{
			image: "./images/rivierkreeften.jpg",
			title: "Daar waar de rivierkreeften zingen.",
			mainCategory: "Boeken",
			subCategory: "Literatuur & Romans",
			match: "99.9%",
			description:
				"Kya Clark is in haar eentje opgegroeid in het moeras van Barkley Cove in North Carolina, afgesloten van de bewoonde wereld. Om zichzelf te onderhouden ruilt ze vis, en groenten uit haar moestuin voor andere levensmiddelen. Ze voelt zich er thuis, beschouwt de natuur als haar leerschool. Maar als ze in aanraking komt met twee jongemannen uit de stad ontdekt ze dat er ook een andere wereld is. Wanneer een van hen dood wordt gevonden, valt de verdenking onmiddellijk op Kya.",
		},
		{
			image: "./images/rivierkreeften.jpg",
			title: "Daar waar de rivierkreeften zingen.",
			mainCategory: "Boeken",
			subCategory: "Literatuur & Romans",
			match: "99.9%",
			description:
				"Kya Clark is in haar eentje opgegroeid in het moeras van Barkley Cove in North Carolina, afgesloten van de bewoonde wereld. Om zichzelf te onderhouden ruilt ze vis, en groenten uit haar moestuin voor andere levensmiddelen. Ze voelt zich er thuis, beschouwt de natuur als haar leerschool. Maar als ze in aanraking komt met twee jongemannen uit de stad ontdekt ze dat er ook een andere wereld is. Wanneer een van hen dood wordt gevonden, valt de verdenking onmiddellijk op Kya.",
		},
		{
			image: "./images/rivierkreeften.jpg",
			title: "Daar waar de rivierkreeften zingen.",
			mainCategory: "Boeken",
			subCategory: "Literatuur & Romans",
			match: "99.9%",
			description:
				"Kya Clark is in haar eentje opgegroeid in het moeras van Barkley Cove in North Carolina, afgesloten van de bewoonde wereld. Om zichzelf te onderhouden ruilt ze vis, en groenten uit haar moestuin voor andere levensmiddelen. Ze voelt zich er thuis, beschouwt de natuur als haar leerschool. Maar als ze in aanraking komt met twee jongemannen uit de stad ontdekt ze dat er ook een andere wereld is. Wanneer een van hen dood wordt gevonden, valt de verdenking onmiddellijk op Kya.",
		},
		{
			image: "./images/rivierkreeften.jpg",
			title: "Daar waar de rivierkreeften zingen.",
			mainCategory: "Boeken",
			subCategory: "Literatuur & Romans",
			match: "99.9%",
			description:
				"Kya Clark is in haar eentje opgegroeid in het moeras van Barkley Cove in North Carolina, afgesloten van de bewoonde wereld. Om zichzelf te onderhouden ruilt ze vis, en groenten uit haar moestuin voor andere levensmiddelen. Ze voelt zich er thuis, beschouwt de natuur als haar leerschool. Maar als ze in aanraking komt met twee jongemannen uit de stad ontdekt ze dat er ook een andere wereld is. Wanneer een van hen dood wordt gevonden, valt de verdenking onmiddellijk op Kya.",
		},
		{
			image: "./images/rivierkreeften.jpg",
			title: "Daar waar de rivierkreeften zingen.",
			mainCategory: "Boeken",
			subCategory: "Literatuur & Romans",
			match: "99.9%",
			description:
				"Kya Clark is in haar eentje opgegroeid in het moeras van Barkley Cove in North Carolina, afgesloten van de bewoonde wereld. Om zichzelf te onderhouden ruilt ze vis, en groenten uit haar moestuin voor andere levensmiddelen. Ze voelt zich er thuis, beschouwt de natuur als haar leerschool. Maar als ze in aanraking komt met twee jongemannen uit de stad ontdekt ze dat er ook een andere wereld is. Wanneer een van hen dood wordt gevonden, valt de verdenking onmiddellijk op Kya.",
		},
		{
			image: "./images/rivierkreeften.jpg",
			title: "Daar waar de rivierkreeften zingen.",
			mainCategory: "Boeken",
			subCategory: "Literatuur & Romans",
			match: "99.9%",
			description:
				"Kya Clark is in haar eentje opgegroeid in het moeras van Barkley Cove in North Carolina, afgesloten van de bewoonde wereld. Om zichzelf te onderhouden ruilt ze vis, en groenten uit haar moestuin voor andere levensmiddelen. Ze voelt zich er thuis, beschouwt de natuur als haar leerschool. Maar als ze in aanraking komt met twee jongemannen uit de stad ontdekt ze dat er ook een andere wereld is. Wanneer een van hen dood wordt gevonden, valt de verdenking onmiddellijk op Kya.",
		},
		{
			image: "./images/rivierkreeften.jpg",
			title: "Daar waar de rivierkreeften zingen.",
			mainCategory: "Boeken",
			subCategory: "Literatuur & Romans",
			match: "99.9%",
			description:
				"Kya Clark is in haar eentje opgegroeid in het moeras van Barkley Cove in North Carolina, afgesloten van de bewoonde wereld. Om zichzelf te onderhouden ruilt ze vis, en groenten uit haar moestuin voor andere levensmiddelen. Ze voelt zich er thuis, beschouwt de natuur als haar leerschool. Maar als ze in aanraking komt met twee jongemannen uit de stad ontdekt ze dat er ook een andere wereld is. Wanneer een van hen dood wordt gevonden, valt de verdenking onmiddellijk op Kya.",
		},
		{
			image: "./images/rivierkreeften.jpg",
			title: "Daar waar de rivierkreeften zingen.",
			mainCategory: "Boeken",
			subCategory: "Literatuur & Romans",
			match: "99.9%",
			description:
				"Kya Clark is in haar eentje opgegroeid in het moeras van Barkley Cove in North Carolina, afgesloten van de bewoonde wereld. Om zichzelf te onderhouden ruilt ze vis, en groenten uit haar moestuin voor andere levensmiddelen. Ze voelt zich er thuis, beschouwt de natuur als haar leerschool. Maar als ze in aanraking komt met twee jongemannen uit de stad ontdekt ze dat er ook een andere wereld is. Wanneer een van hen dood wordt gevonden, valt de verdenking onmiddellijk op Kya.",
		},
	];

	elementArray.forEach((el) => {
		const bolItem = elementFromHtml(`
			<div class="bolItem">
				<img class="bolItemImg" src="https://placeholder.pics/svg/75x100">
				<div class="bolItemBody">
					<div class="bolItemHeader">
						<div class="bolItemTitle titleWrap" title="${el.title}">${el.title}</div>
						<div class="bolItemDropdownBtn"></div>
					</div>
					<div class="bolItemDescription">
						<div class="bolItemDescImg"><img src="https://placeholder.pics/svg/75x100"></div>
						${el.description}
					</div>
					<div class="bolItemDetails">
						<div class="bolItemSubCategory noWrap" title="${el.subCategory}">${el.subCategory}</div>
						<div class="bolItemMatch">Match: ${el.match}</div>
					</div>
				</div>
			</div>
		`);

		bolElement.querySelector("#bolElBody").appendChild(bolItem);
	});

	// Appends the overlay element as a child element after the <head> element
	const htmlHead = document.querySelector("head");
	htmlHead.parentNode.insertBefore(bolElement, htmlHead.nextSibling);
	chrome.tabs;

	// Removes the overlay element from the html
	bolElement.querySelector("#bolElCloseBtn").addEventListener("click", () => {
		htmlHead.parentNode.removeChild(document.querySelector("#bolOverlay"));
		window.postMessage("closed", "*");
	});

	// Toggles the active class on the bol item to open it up or close it
	document.querySelectorAll(".bolItemDropdownBtn").forEach((btn) => {
		btn.addEventListener("click", () => {
			btn.parentNode.parentNode.parentNode.classList.toggle("active");
		});
	});
}
