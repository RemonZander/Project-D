/* Create a context-menu */
chrome.contextMenus.create({
    id: "bolImageSearch",   // <-- mandatory with event-pages
    title: "Search on bol.com",
    contexts: ["image"]
});

/* Register a listener for the `onClicked` event */
chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (tab && info.mediaType === "image") {
        /* Create the code to be injected */
        var code = [
            'window.location.href = "https://www.bol.com";',
        ].join("\n");

        /* Inject the code into the current tab */
        chrome.tabs.executeScript(tab.id, { code: code });
    }
});