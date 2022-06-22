// Create context-menus
chrome.contextMenus.create({
	id: "bolParentSearch",
	title: "Bol.com Extension",
	contexts: ["image"],
});

// Create context-menus
chrome.contextMenus.create({
	id: "bolComplexSearch",
	parentId: "bolParentSearch",
	title: "Search item on bol.com (Complex Case)",
	contexts: ["image"],
});

chrome.contextMenus.create({
	id: "bolSimpleSearch",
	parentId: "bolParentSearch",
	title: "Search type on bol.com (Simple Case)",
	contexts: ["image"],
});

// Register a listener for the `onClicked` event
chrome.contextMenus.onClicked.addListener((clickedData, tab) => {
	if (
		!tab ||
		clickedData.mediaType !== "image" ||
		clickedData.menuItemId === "bolParentSearch"
	)
		return;

	if (tab && clickedData.menuItemId === "bolComplexSearch") {
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
			data.append("complex_case", true);

			// Post request to the server sending the formdata as the data.
			fetch(`http://127.0.0.1:5000/image`, {
				method: "POST",
				body: data,
			})
				.then((res) => {
					res.json()
						.then((data) => ({
							body: data,
						}))
						.then((obj) => {
							let bolItems = [];
							obj.body.Message.forEach((product) => {
								bolItems.push({
									image: product.image,
									title: product.title,
									link: product.link,
									match: product.match,
									description: product.description,
								});
							});

							chrome.storage.local.set({
								bolItems: bolItems,
							});
						});
				})
				.catch((error) => {
					console.log("Authorization failed : " + error.message);
				});
		});
	} else if (tab && clickedData.menuItemId === "bolSimpleSearch") {
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
			data.append("complex_case", false);

			// Post request to the server sending the formdata as the data.
			fetch(`url`, {
				method: "POST",
				body: data,
			})
				.then((res) => {
					res.json()
						.then((data) => ({
							body: data,
						}))
						.then((obj) => {
							console.log(obj.body.Message);
						});
				})
				.catch((error) => {
					console.log("Authorization failed : " + error.message);
				});
		});
	}
});

// Function that runs the createOverlay.js file when the extension icon is clicked
chrome.action.onClicked.addListener((tab) => {
	chrome.scripting.executeScript({
		target: { tabId: tab.id },
		files: ["createOverlay.js"],
	});
});
