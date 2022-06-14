if (!document.querySelector("#bolOverlay")) {
	const createOverlay = async () => {
		// Function that create a html element from a string.
		const elementFromHtml = (html) => {
			const template = document.createElement("template");

			template.innerHTML = html.trim();

			return template.content.firstElementChild;
		};

		// Function that create the base extension overlay.
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

		const getBolItems = async (key) => {
			return new Promise((resolve, reject) => {
				if (!key) reject;

				chrome.storage.local.get(key, (res) => {
					resolve(res.bolItems);
				});
			});
		};

		let elementArray = await getBolItems("bolItems");

		elementArray.sort((a, b) => {
			return b.match - a.match;
		});

		// Function that removes all the <mark></mark> tags from a string.
		const removeMarks = (string) => {
			const removeMarkRegex = new RegExp(
				/(<mark class="markedText">|<\/mark>)/,
				"gim"
			);
			string = string.replace(removeMarkRegex, "");

			return string;
		};

		// Function that adds <mark></mark> tags to all the substrings that match the RegEx.
		const markSubstring = (string, input) => {
			if (!string || !input) return;

			string = removeMarks(string);

			const markRegex = new RegExp(input, "gim");
			return string.replace(
				markRegex,
				'<mark class="markedText">$&</mark>'
			);
		};

		// Function that creates a bolItem element and adds it as a child element to the extension.
		const createItem = (item) => {
			// Gets the correct image url to display the image in the extension
			const imgLink = chrome.runtime.getURL(`images/${item.image}`);
			console.log(item);

			const bolItem = elementFromHtml(`
				<div class="bolItem" data-link="${item.link}">
					<img class="bolItemImg" src="${imgLink}">
					<div class="bolItemBody">
						<div class="bolItemHeader">
							<div class="bolItemTitle titleWrap" title='${removeMarks(item.title)}'>${
				item.title
			}</div>
							<div class="bolItemDropdownBtn"></div>
						</div>
						<div class="bolItemDescription">
							<div class="bolItemDescImg"><img src="${imgLink}"></div>
							<div class="bolItemDescText">${item.description}</div>
							<div class="bolItemMatch">Match: ${item.match}%</div>
						</div>
					</div>
				</div>
			`);

			bolElement.querySelector("#bolElBody").appendChild(bolItem);
		};

		// Function that calls the createItem function for every item in an array.
		const displayItems = (array) => {
			bolElement.querySelector("#bolElBody").innerHTML = "";
			array.map(createItem);
		};

		displayItems(elementArray);

		// Appends the overlay element as a child element after the <head> element.
		const htmlHead = document.querySelector("head");
		htmlHead.parentNode.insertBefore(bolElement, htmlHead.nextSibling);

		// Removes the overlay element from the html, when clicked outside the bolElement or clicking the bolElCloseBtn
		bolElement.addEventListener("click", (e) => {
			if (
				e.target.matches("#bolElCloseBtn") ||
				e.target.matches("#bolOverlay")
			) {
				htmlHead.parentNode.removeChild(
					document.getElementById("bolOverlay")
				);
			}
		});

		// Adds the onClick event on the title and the images to go to the product page on bol.com
		bolElement.addEventListener("click", (e) => {
			if (e.target.matches(".bolItemImg")) {
				window.open(e.target.parentNode.dataset.link, "_blank");
			} else if (e.target.matches(".bolItemTitle")) {
				window.open(
					e.target.parentNode.parentNode.parentNode.dataset.link,
					"_blank"
				);
			} else if (e.target.matches(".bolItemDescImg img")) {
				window.open(
					e.target.parentNode.parentNode.parentNode.parentNode.dataset
						.link,
					"_blank"
				);
			}
		});

		// Removes the overlay element from the html, when right clicked outside the bolElement
		bolElement.addEventListener("contextmenu", (e) => {
			if (e.target.matches("#bolOverlay")) {
				e.preventDefault();

				htmlHead.parentNode.removeChild(
					document.getElementById("bolOverlay")
				);
			}
		});

		// Adds a "click" event listener to toggle the active class on the bolItem element to open it up or close it.
		const addBtnClick = () => {
			document.querySelectorAll(".bolItemDropdownBtn").forEach((btn) => {
				btn.addEventListener("click", () => {
					btn.parentNode.parentNode.parentNode.classList.toggle(
						"active"
					);
				});
			});
		};

		addBtnClick();

		const bolInput = document.querySelector("#bolSearchInput");

		// "input" event listener for filtering, sorting and marking the products based on the input given.
		bolInput.addEventListener("input", (e) => {
			// .replace(/\s\s+/g, ' ');
			// ^ replaces multiple spaces with a single space.
			if (e.target.value.toLowerCase() === "") {
				elementArray.forEach((item) => {
					item.title = removeMarks(item.title);
					item.description = removeMarks(item.description);
				});

				displayItems(elementArray);
				addBtnClick();
			} else {
				const filterItems = (item) => {
					return (
						removeMarks(item.title.toLowerCase()).includes(
							e.target.value.toLowerCase()
						) ||
						removeMarks(item.description.toLowerCase()).includes(
							e.target.value.toLowerCase()
						)
					);
				};

				const filteredElementArray = elementArray.filter(filterItems);

				filteredElementArray.forEach((item) => {
					item.title = markSubstring(item.title, e.target.value);
					item.description = markSubstring(
						item.description,
						e.target.value
					);
				});

				const matchRegex = new RegExp(e.target.value, "gim");
				filteredElementArray.sort((a, b) => {
					const totalA =
						(a.title.match(matchRegex) || []).length +
						(a.description.match(matchRegex) || []).length;

					const totalB =
						(b.title.match(matchRegex) || []).length +
						(b.description.match(matchRegex) || []).length;

					return (
						totalB - totalA ||
						(b.title.match(matchRegex) || []).length -
							(a.title.match(matchRegex) || []).length ||
						(b.description.match(matchRegex) || []).length -
							(a.description.match(matchRegex) || []).length
					);
				});

				displayItems(filteredElementArray);
				addBtnClick();
			}
		});
	};
	createOverlay();
} else {
	// Removes the overlay element when the extension icon is clicked, if the overlay is open.
	const htmlHead = document.querySelector("head");
	htmlHead.parentNode.removeChild(document.querySelector("#bolOverlay"));
}
