console.log('🚀 Jut.su Premium Injector content script загружен');

window.jutsuPremiumReady = true;

const style = document.createElement('style');
style.textContent = `
    .plus_player .video-js {
        background-color: #000;
        border-radius: 8px;
    }
    .video-js video {
        border-radius: 8px;
    }
`;
document.head.appendChild(style);