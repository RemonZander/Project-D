// Create a context-menu
chrome.contextMenus.create({
	id: "bolImageSearch",
	title: "Search on bol.com",
	contexts: ["image"],
});

// Register a listener for the `onClicked` event
chrome.contextMenus.onClicked.addListener((clickedData, tab) => {
	if (
		!tab ||
		clickedData.mediaType !== "image" ||
		clickedData.menuItemId !== "bolImageSearch"
	)
		return;

	// Fetch request to get the image from the image src url
	fetch(clickedData.srcUrl).then(async (res) => {
		// Convert the image to a blob
		const contentType = res.headers.get("content-type");
		const blob = await res.blob();

		// Making the blob into an file object
		const imgFile = new File([blob], "image.jpg", { contentType });

		// Adding the imgFile to the formData with the key "image" for the post request
		const data = new FormData();
		data.append("image", imgFile);

		// Post request to the server sending the formdata as the data.
		fetch(`http://127.0.0.1:5000/image`, {
			method: "POST",
			body: data,
		})
			.then((res) => {
				res.json();
				console.log(res);
			})
			.catch((error) => {
				console.log("Authorization failed : " + error.message);

				// Put this functrion in the .then() when flask server works properly
				chrome.storage.local.set(
					{
						bolItems: [
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
						],
					},
					() => {
						console.log("Array set");
					}
				);
			});
	});
});

// Function that runs the createOverlay.js file when the extension icon is clicked
chrome.action.onClicked.addListener((tab) => {
	chrome.scripting.executeScript({
		target: { tabId: tab.id },
		files: ["createOverlay.js"],
	});
});
