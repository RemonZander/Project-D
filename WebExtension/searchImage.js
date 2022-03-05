/* Create a context-menu */
chrome.contextMenus.create({
    id: "bolImageSearch",   // <-- mandatory with event-pages
    title: "Search on bol.com",
    contexts: ["image"]
});


/* Register a listener for the `onClicked` event */
chrome.contextMenus.onClicked.addListener((clickedData, tab) => {
    if (tab && clickedData.mediaType === "image" && clickedData.menuItemId === "bolImageSearch") {

        const data = new FormData();
        data.append("image", clickedData.srcUrl);

        chrome.runtime.sendMessage(
            {
                query: "POST",
                data: data,
                url: "http://127.0.0.1:5000/image"
            }, 
            (res) => {
                if (res !== undefined && res !== "") {
                    console.log(res);
                }
                else {
                    console.log(`empty res: ${res}`);
                }
            }
        );
    }
});



chrome.runtime.onMessage.addListener((request, sender, sendResponse) => { 
    if (request.query == "POST") {
        fetch(request.url, {
            method: 'POST',
            body: request.data
        })
        .then(res => res.json())
        .then(res => sendResponse(res))
        .catch(err => console.error(`Error: ${err}`));

        return true
    }
});