// Create a context-menu
chrome.contextMenus.create({
	id: "bolImageSearch",
	title: "Search on bol.com",
	contexts: ["image"],
});

// Register a listener for the `onClicked` event
chrome.contextMenus.onClicked.addListener((clickedData, tab) => {
	if (
		tab &&
		clickedData.mediaType === "image" &&
		clickedData.menuItemId === "bolImageSearch"
	) {
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
				.catch((error) =>
					console.log("Authorization failed : " + error.message)
				);
		});
	}
});

chrome.action.onClicked.addListener((tab) => {
	chrome.scripting.executeScript({
		target: { tabId: tab.id },
		files: ["createOverlay.js"],
	});
});
