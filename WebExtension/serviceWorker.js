chrome.runtime.onInstalled.addListener(() => {
	// Create context-menus
	chrome.contextMenus.create({
		id: "bolParentSearch",
		title: "Bol.com Extension",
		contexts: ["image"],
	});

	chrome.contextMenus.create({
		id: "bolComplexSearch",
		parentId: "bolParentSearch",
		title: "Search picture on bol.com",
		contexts: ["image"],
	});

	chrome.contextMenus.create({
		id: "bolSimpleSearch",
		parentId: "bolParentSearch",
		title: "Search item type on bol.com",
		contexts: ["image"],
	});
});

// Register a listener for the `onClicked` event
chrome.contextMenus.onClicked.addListener((clickedData, tab) => {
	if (
		!tab ||
		clickedData.mediaType !== "image" ||
		clickedData.menuItemId === "bolParentSearch"
	)
		return;

	console.log("Before first Post");

	// Fetch request to get the image from the image src url
	fetch(clickedData.srcUrl).then(async (res) => {
		// Convert the image to a blob
		const contentType = res.headers.get("content-type");
		const blob = await res.blob();

		// Making the blob into an file object
		const imgFile = new File([blob], "image.jpg", { contentType });

		console.log("Inside first Post");

		if (tab && clickedData.menuItemId === "bolComplexSearch") {
			// Adding the imgFile to the formData with the key "image" for the post request
			const data = new FormData();
			data.append("image", imgFile);
			data.append("complex_case", true);

			console.log("Before Post");

			// Post request to the server sending the formdata as the data.
			fetch(`http://127.0.0.1:5000/image`, {
				method: "POST",
				body: data,
			})
				.then((res) => {
					console.log("Recieved response!");
					res.json()
						.then((obj) => {
							let bolItems = [];
							console.log(obj);
							obj.Message.forEach((product) => {
								bolItems.push({
									image: product[0].image,
									title: product[0].title,
									link: product[0].link,
									match: product[0].match,
									description: product[0].description,
								});
							});

/*							chrome.storage.local.set({
								"bolItems": bolItems,
							}, () => {
								console.log(`localStorage set to key: ${bolItems}, value: ${bolItems}`);
							});*/

							console.log(bolItems)
							chrome.storage.local.set({ bolItems: bolItems }, () => {
								console.log("Data set.");

								chrome.storage.local.get(["bolItems"], (res) => {
									console.log(res);
								});
							});

/*							chrome.storage.local.get("bolItems", (res) => {
								console.log(`Stored data: ${res.key}`)
							});*/

							console.log("your mom")
							chrome.scripting.executeScript({
								target: { tabId: tab.id },
								files: ["createOverlay.js"],
							});
						});
				})
				.catch((error) => {
					console.log("Authorization failed : " + error.message);
				});
			
		} else if (tab && clickedData.menuItemId === "bolSimpleSearch") {
			// Adding the imgFile to the formData with the key "image" for the post request
			const data = new FormData();
			data.append("image", imgFile);
			data.append("complex_case", false);

			// Post request to the server sending the formdata as the data.
			fetch(`http://127.0.0.1:5000/image`, {
				method: "POST",
				body: data,
			})
				.then((res) => {
					res.json()
						.then((obj) => {
							console.log(obj)
							chrome.tabs.create({
								url: `https://www.bol.com/nl/nl/s/?searchtext=${obj.Message}`,
							});
						});
				})
				.catch((error) => {
					console.log("Authorization failed : " + error.message);
				});
		}
	});
});

// Function that runs the createOverlay.js file when the extension icon is clicked
chrome.action.onClicked.addListener((tab) => {
	chrome.scripting.executeScript({
		target: { tabId: tab.id },
		files: ["createOverlay.js"],
	});
});
