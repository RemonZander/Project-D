var elementFromHtml = (html) => {
	const template = document.createElement("template");

	template.innerHTML = html.trim();

	return template.content.firstElementChild;
};

var bolElement = elementFromHtml(`
	<div id="bolOverlay">
		<div id="bolElement">
			<div id="bolElHeader">
				<div id="bolLogo">
					<p id="bolLogoMainText">Bol.com</p>
					<p id="bolLogoExtText">Extension</p>
				</div>
				<div id="bolSearchBar">
					<input id="bolSearchInput" class="noWrap" placeholder="Main category"/>
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
				<div class="bolItem">
					<img class="bolItemImg" src="https://placeholder.pics/svg/75x100">
					<div class="bolItemBody">
						<div class="bolItemHeader">
							<div class="bolItemTitle titleWrap" title="title">Laptop - Apple MacBook Air (November, 2020) MGN63N/A - 13.3 inch - Apple M1 - 256 GB - Space Grey</div>
							<div class="bolItemDropdownBtn"></div>
						</div>
						<div class="bolItemDescription">Bol.com's keuze voor een MacBook Air met de nieuwe M1 chip en 18 uur batterijduur. Ideaal voor al je dagelijkse werkzaamheden en lichte grafische taken.</div>
						<div class="bolItemDetails">
							<div class="bolItemSubCategory noWrap" title="category">category</div>
							<div class="bolItemMatch">Match: 99%</div>
						</div>
					</div>
				</div>
				<div class="bolItem">
					<img class="bolItemImg" src="https://placeholder.pics/svg/75x100">
					<div class="bolItemBody">
						<div class="bolItemHeader">
							<div class="bolItemTitle titleWrap" title="title">Laptop - Apple MacBook Air (November, 2020) MGN63N/A - 13.3 inch - Apple M1 - 256 GB - Space Grey</div>
							<div class="bolItemDropdownBtn"></div>
						</div>
						<div class="bolItemDescription">Bol.com's keuze voor een MacBook Air met de nieuwe M1 chip en 18 uur batterijduur. Ideaal voor al je dagelijkse werkzaamheden en lichte grafische taken.</div>
						<div class="bolItemDetails">
							<div class="bolItemSubCategory noWrap" title="category">category</div>
							<div class="bolItemMatch">Match: 99%</div>
						</div>
					</div>
				</div>
				<div class="bolItem">
					<img class="bolItemImg" src="https://placeholder.pics/svg/75x100">
					<div class="bolItemBody">
						<div class="bolItemHeader">
							<div class="bolItemTitle titleWrap" title="title">Laptop - Apple MacBook Air (November, 2020) MGN63N/A - 13.3 inch - Apple M1 - 256 GB - Space Grey</div>
							<div class="bolItemDropdownBtn"></div>
						</div>
						<div class="bolItemDescription">Bol.com's keuze voor een MacBook Air met de nieuwe M1 chip en 18 uur batterijduur. Ideaal voor al je dagelijkse werkzaamheden en lichte grafische taken.</div>
						<div class="bolItemDetails">
							<div class="bolItemSubCategory noWrap" title="category">category</div>
							<div class="bolItemMatch">Match: 99%</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
`);

var elementArray = [
	{
		image: "./images/rivierkreeften.jpg",
		title: "Daar waar de rivierkreeften zingen.",
		mainCategory: "Boeken",
		subCategory: "Literatuur & Romans",
		match: "99.9%",
	},
	{
		image: "./images/rivierkreeften.jpg",
		title: "Daar waar de rivierkreeften zingen.",
		mainCategory: "Boeken",
		subCategory: "Literatuur & Romans",
		match: "99.9%",
	},
	{
		image: "./images/rivierkreeften.jpg",
		title: "Daar waar de rivierkreeften zingen.",
		mainCategory: "Boeken",
		subCategory: "Literatuur & Romans",
		match: "99.9%",
	},
	{
		image: "./images/rivierkreeften.jpg",
		title: "Daar waar de rivierkreeften zingen.",
		mainCategory: "Boeken",
		subCategory: "Literatuur & Romans",
		match: "99.9%",
	},
	{
		image: "./images/rivierkreeften.jpg",
		title: "Daar waar de rivierkreeften zingen.",
		mainCategory: "Boeken",
		subCategory: "Literatuur & Romans",
		match: "99.9%",
	},
	{
		image: "./images/rivierkreeften.jpg",
		title: "Daar waar de rivierkreeften zingen.",
		mainCategory: "Boeken",
		subCategory: "Literatuur & Romans",
		match: "99.9%",
	},
	{
		image: "./images/rivierkreeften.jpg",
		title: "Daar waar de rivierkreeften zingen.",
		mainCategory: "Boeken",
		subCategory: "Literatuur & Romans",
		match: "99.9%",
	},
	{
		image: "./images/rivierkreeften.jpg",
		title: "Daar waar de rivierkreeften zingen.",
		mainCategory: "Boeken",
		subCategory: "Literatuur & Romans",
		match: "99.9%",
	},
];

var mainCategory;

elementArray.forEach((el) => {
	const bolItem = elementFromHtml(`
        <div class="bolItem" style="display: flex;background-color: #F2F2F2;border: solid 1px #020202;">
            <img class="bolItemImg" src="https://placeholder.pics/svg/75x100" style="cursor: pointer;">
            <div class="bolItemBody" style="display: flex;flex-direction: column;width: 100%;justify-content: space-between;">
                <div class="bolItemTitle noWrapText" title="${el.title}" style="padding: 0px 10% 0px 10%;border-bottom: solid 1px #020202;height: 35px;line-height: 35px;font-size: 18px;font-weight: 700;cursor: pointer;text-overflow: ellipsis;white-space: nowrap;overflow: hidden;">${el.title}</div>
                <div class="bolItemDetails" style="display: flex;justify-content: space-between;padding: 0px 10% 0px 10%;margin-bottom: 5%;">
                    <div class="bolItemSubCategory noWrapText" title="${el.subCategory}" style="width: 100px;border: solid 1px #020202;padding: 5px;cursor: pointer;text-overflow: ellipsis;white-space: nowrap;overflow: hidden;">${el.subCategory}</div>
                    <div class="bolItemMatch" style="padding: 5px;">Match: ${el.match}</div>
                </div>
            </div>
        </div>
    `);

	bolElement.querySelector("#bolElBody").appendChild(bolItem);

	if (!mainCategory) {
		mainCategory = el.mainCategory;
	}
});

bolElement.querySelector("#bolSearchInput").value = mainCategory;

// Appends the overlay element as a child element after the <head> element
var htmlHead = document.querySelector("head");
htmlHead.parentNode.insertBefore(testEl, htmlHead.nextSibling);

bolElement.querySelector("#bolElCloseBtn").addEventListener("click", () => {
	htmlHead.parentNode.removeChild(document.querySelector("#bolOverlay"));
});
