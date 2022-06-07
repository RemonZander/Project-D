if (!document.querySelector("#bolOverlay")) {
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

	let elementArray = [
		{
			image: "2.jpg",
			title: "Fruit of the Loom Joggingbroek (met rechte Pijp) Zwart Maat M",
			subCategory: "Broeken",
			match: "96",
			description: `Deze wereldberoemde Joggingbroek van Fruit of the Loom met rechte pijp mogen niet ontbreken in de kledingkast van een man.
			De broek is zowel casual als trendy en heeft elastieken boorden, waardoor u hem naar de sportschool of gewoon thuis op de bank kunt dragen. De Joggingbroek hebben twee handige zakken aan de zijkant.
			Fruit of the Loom gebruikt hun kwalitatief hoogwaardige Belcoro garen om deze Joggingbroek te produceren, waardoor ze zacht en comfortabel aanvoelen.
			
			Kleur: Zwart
			Maat: M
			Open boorden
			Lichtgewicht ongekamde fleece
			Zijzakken
			Elastische boord met koord
			Katoen/lycra geribbelde broekband en boorden
			2 zakken aan de zijkant
			240 g/m²
			Belcoro garen voor comfortabele zachtheid en het verkrijgen van perfecte drukresultaten
			Kijk in de tabel voor meer informatie over de maat
			Belangrijk! De genoemde maten zijn de maten van de producten
			Speling in maat +/- 2 cm
			Materiaal: Katoen: 80%, Polyester: 20%
			Merk: Fruit of the Loom
			`,
		},
		{
			image: "1.jpg",
			title: "Object OBJLISA SLIM PANT NOOS Dames Broek Marina - Maat 38",
			subCategory: "Broeken",
			match: "98",
			description: `•	Object Dames Slim fit pantalon
				•	Paspel zakken aan de achterkant
				•	Elastische tailleband
				•	50% polyester, 32% Viscose, 13% polyester, 5% Elastaan
				Dit product is gemaakt met gerecycled polyester. Gerecycled polyester beschermt de natuurlijke bronnen en vermindert de hoeveelheid afval.
				
				40°C fijne was/wolwas, Niet bleken, Hangend drogen, Niet in wasdroger drogen, Strijken op gematigde temperatuur.
				`,
		},
		{
			image: "3.jpg",
			title: "Bruine Broek/Pantalon van Je m'appelle - Dames - Maat 2XL - 6 maten beschikbaar",
			subCategory: "Broeken",
			match: "94",
			description: `• Fijne chino in zacht katoen met wafeltjesstructuur en elastan• Ritssluiting met knoop • Steekzakken aan de voorkant en fake-paspelzakjes aan de achterkant • Elastische tailleband met riemlusjes`,
		},
		{
			image: "4.jpg",
			title: "ONLY ONLLIVE LOVE LIFE NEW LEGGINGS NOOS Dames Legging - Maat L",
			subCategory: "Broeken",
			match: "92",
			description: `- Basic legging
				- Normal waist
				- Elastiek in de taille
				- Stretchy stof
				- Binnenbeenlengte: 68 cm in maat M
				`,
		},
		{
			image: "6.jpg",
			title: "GARCIA Celia Dames Skinny Fit Broek Wit - Maat W29 X L30",
			subCategory: "Broeken",
			match: "88",
			description: `De Celia 244 accentueert de vrouwelijke vormen door de superslim fit, een hoge taille en pijpen die strak aansluiten van bovenbeen tot enkel. De tailleband valt gemiddeld tot net iets onder de navel.
			
			Better Cotton is een initiatief dat zich wereldwijd inzet voor betere omstandigheden in de katoenindustrie. Bij het creëren van dit GARCIA kledingstuk gebruik gemaakt van een duurzame wastechniek.
			`,
		},
		{
			image: "7.jpg",
			title: "WE Fashion Dames soepelvallende pantalon met strikceintuur",
			subCategory: "Broeken",
			match: "86",
			description: `Een broek van soepele, geweven kwaliteit met een hoge taille en rechte, wijde pijpen. De broek heeft bekleed elastiek en een drawstring in de taille en twee steekzakken.`,
		},
		{
			image: "8.jpg",
			title: "Vila VIKOOLA PANTS Dames Broek Cement - Maat 38",
			subCategory: "Broeken",
			match: "84",
			description: `•	Vila Dames Broek
			•	Steekzakken
			•	100% Katoen
			•	Hydrofiel
			
			
			Set: samen met de VIKOOLA 3/4 Cropped Dames Blouse
			
			30°C bonte was, Niet bleken, Hangend drogen, Niet in wasdroger drogen, Strijken op lage temperatuur, Niet droogreinigen
			`,
		},
		{
			image: "9.jpg",
			title: "Fruit of the Loom Joggingbroek (met rechte Pijp) Grijs Maat S",
			subCategory: "Broeken",
			match: "82",
			description: `Deze wereldberoemde Joggingbroek van Fruit of the Loom met rechte pijp mogen niet ontbreken in de kledingkast van een man.
			De broek is zowel casual als trendy en heeft elastieken boorden, waardoor u hem naar de sportschool of gewoon thuis op de bank kunt dragen. De Joggingbroek hebben twee handige zakken aan de zijkant.
			Fruit of the Loom gebruikt hun kwalitatief hoogwaardige Belcoro garen om deze Joggingbroek te produceren, waardoor ze zacht en comfortabel aanvoelen.
			
			Kleur: Grijs
			Maat: S
			Open boorden
			Lichtgewicht ongekamde fleece
			Zijzakken
			Elastische boord met koord
			Katoen/lycra geribbelde broekband en boorden
			2 zakken aan de zijkant
			240 g/m²
			Belcoro garen voor comfortabele zachtheid en het verkrijgen van perfecte drukresultaten
			Kijk in de tabel voor meer informatie over de maat
			Belangrijk! De genoemde maten zijn de maten van de producten
			Speling in maat +/- 2 cm
			Materiaal: Katoen: 80%, Polyester: 20%
			Merk: Fruit of the Loom
			`,
		},
		{
			image: "5.jpg",
			title: "ONLY ONLPOPTRASH LIFE EASY COL PANT PNT NOOS Dames Broek - Maat M X L32",
			subCategory: "Broeken",
			match: "90",
			description: `- Loose fit broek
				- Smalle broekspijpen
				- Snoerkoord in de taille
				- Elastische rib aan de achterkant van de taille
				- Riemlussen
				- Geplooid aan de voorkant
				- 2 paspelzakken aan de achterkant
				- Stretchy stof
				- Binnenbeenlengte: 73 cm in maat 38 X L32
				`,
		},
		{
			image: "10.jpg",
			title: "Le Jogg Denim Spring - Broek van Je m'appelle",
			subCategory: "Broeken",
			match: "80",
			description: `• Fijne broek die je het liefst iedere dag wil dragen• Gemaakt van heerlijk katoen met elastan• Super stretch• Leuke contrast rib in de taille en sierlijk verstelbaar koord`,
		},
		{
			image: "11.jpg",
			title: "ONLY ONLROYAL HW SK ROCK COATED PIM NOOS Dames Broek - Maat M X L32",
			subCategory: "Broeken",
			match: "78",
			description: `- Gecoate skinny fit broek
				- High waist
				- Knoop- en rits sluiting aan de voorkant
				- 5-pocket model
				- Met riemlussen
				- Stretchy stof
				- Binnenbeenlengte: 84 cm in maat M X L34
				`,
		},
		{
			image: "12.jpg",
			title: "VERO MODA VMOCTAVIA HW SWEAT PANT GA Dames Broek - Maat M",
			subCategory: "Broeken",
			match: "76",
			description: `- Jogging broek
				- De broek is gemaakt van biologisch katoen.
				- De broek heeft een aantrekkoord in de middel om de broek te sluiten.
				-hoge taille.
				- De broek heeft een elastieke band om de enkel.
				`,
		},
		{
			image: "13.jpg",
			title: "Ambika Flared Legging - Maat M - Zwart - Rib",
			subCategory: "Broeken",
			match: "74",
			description: `LET OP: De broek valt wat groot. Twijfel je tussen twee maten, neem dan de kleinere maat!
				Deze flared broek zit zo lekker als een joggingbroek, maar ziet er super fashionable uit! Deze broeken met uitlopende pijpen zijn helemaal hot dit seizoen! Combineer de broek met een leuk wit it-shirt en sneakers of met een chique top en pumps!
				
				– Kleur: zwart
				– Materiaal: 95 polyester, 5% elastaan
				– De broek heeft een heerlijke ribstof
				– Uitlopende pijpen
				– De legging heeft een elastieken band in de taille en is highwaisted
				– Het model op de foto is 1.75m lang en draagt maat XS
				
				M: totale lengte 114 cm, binnenbeenlengte 88 cm en taille breedte 32 cm
				`,
		},
		{
			image: "14.jpg",
			title: "Bruine Broek/Pantalon van Je m'appelle - Dames - Maat M - 6 maten beschikbaar",
			subCategory: "Broeken",
			match: "72",
			description: `• Fijne chino in zacht katoen met wafeltjesstructuur en elastan• Ritssluiting met knoop • Steekzakken aan de voorkant en fake-paspelzakjes aan de achterkant • Elastische tailleband met riemlusjes`,
		},
		{
			image: "15.jpg",
			title: "Vila VIKOOLA PANTS Dames Broek Green Bay - Maat 38",
			subCategory: "Broeken",
			match: "70",
			description: `•	Vila Dames Broek
				•	Steekzakken
				•	100% Katoen
				•	Hydrofiel
				
				
				Set: samen met de VIKOOLA 3/4 Cropped Dames Blouse
				
				30°C bonte was, Niet bleken, Hangend drogen, Niet in wasdroger drogen, Strijken op lage temperatuur, Niet droogreinigen
				`,
		},
		{
			image: "16.jpg",
			title: "Comfortabele Dames Sport Broek / JoggingsBroek / Home Pants | Blauw - Maat M",
			subCategory: "Broeken",
			match: "68",
			description: `Deze mooie en trendy Joggingbroek heeft geen tekort aan mooie details zoals bijpassende strepen langs de hele zijnaad, een bijpassend trekkoord met brede metalen uiteinden en paspelzakken. In puur viscose interlockmateriaal is het een super zachte Joggingbroek. De broek is zowel casual als trendy en heeft elastieken boorden, waardoor u hem naar de sportschool of gewoon thuis op de bank kunt dragen. De Joggingbroek hebben twee handige zakken aan de zijkant. Voorzien van een elastische tailleband met aantrekkoordjes en twee steekzakken.`,
		},
		{
			image: "17.jpg",
			title: "Ambika Flared Legging - Maat M - Bruin - Panter",
			subCategory: "Broeken",
			match: "66",
			description: `Deze flared broek zit zo lekker als een joggingbroek, maar ziet er super fashionable uit! Deze broeken met luipaardprint zijn helemaal hot dit seizoen! Combineer de broek met een leuk wit it-shirt en sneakers of met een chique top en pumps!

				– Kleur: bruin
				– Materiaal: 95 polyester, 5% elastaan
				– De broek heeft een heerlijk zachte stof
				– Uitlopende pijpen
				– Een elastieken band in de taille
				– Model op foto is 1.75m en draagt maat S
				M: totale lengte 114 cm, binnenbeenlengte 88 cm en taille breedte 32 cm
				
				`,
		},
		{
			image: "18.jpg",
			title: "ONLY ONLFEVER STRETCH FLAIRED PANTS JRS NOOS Dames Broek - Maat W30xL30",
			subCategory: "Broeken",
			match: "64",
			description: `Broek van ONLY. Stretchy stof. Binnenbeenlengte: 83 cm in maat M`,
		},
		{
			image: "19.jpg",
			title: "Premium Dames Legging Katoen | Basic Legging | Wit - L",
			subCategory: "Broeken",
			match: "62",
			description: `Het is de ideale legging voor in in je vrije tijd en dagelijkse activiteiten. Deze legging voelt aan als een tweede huid en zal geen belemmering zijn!

				Een zwarte basic legging is onmisbaar in je garderobe. Van sexy jurkje, rokjes, of broekjes elke look wordt helemaal compleet met een mooie legging. De zwarte kleur maakt het eenvoudig om te combineren terwijl het extra zachte materiaal comfortabel is om te dragen.
				
				•	Beschikbaar in verschillende maten
				•	Materiaal: 95% Katoen, 5% Elastaan
				•	Wasvoorschrift: 30°C
				`,
		},
		{
			image: "20.jpg",
			title: "ONLY ONLLIVE LOVE LIFE NEW LEGGINGS NOOS Dames Legging - Maat M",
			subCategory: "Broeken",
			match: "60",
			description: `- Basic legging
				- Normal waist
				- Elastiek in de taille
				- Stretchy stof
				- Binnenbeenlengte: 68 cm in maat M
				`,
		},
	];

	// Sort items based on match, higher to lower.
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
		return string.replace(markRegex, '<mark class="markedText">$&</mark>');
	};

	// Function that creates a bolItem element and adds it as a child element to the extension.
	const createItem = (item) => {
		// Gets the correct image url to display the image in the extension
		const imgLink = chrome.runtime.getURL(`images/${item.image}`);

		const bolItem = elementFromHtml(`
			<div class="bolItem">
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
					</div>
					<div class="bolItemDetails">
						<div class="bolItemSubCategory noWrap" title="${item.subCategory}">${
			item.subCategory
		}</div>
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

	// Adds a "click" event listener to toggle the active class on the bolItem element to open it up or close it.
	const addBtnClick = () => {
		document.querySelectorAll(".bolItemDropdownBtn").forEach((btn) => {
			btn.addEventListener("click", () => {
				btn.parentNode.parentNode.parentNode.classList.toggle("active");
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
} else {
	// Removes the overlay element when the extension icon is clicked, if the overlay is open.
	const htmlHead = document.querySelector("head");
	htmlHead.parentNode.removeChild(document.querySelector("#bolOverlay"));
}
