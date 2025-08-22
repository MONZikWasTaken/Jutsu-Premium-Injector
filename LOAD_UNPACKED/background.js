chrome.runtime.onInstalled.addListener(() => {
    console.log('Jut.su Premium Injector установлен');
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {

    return true;
});