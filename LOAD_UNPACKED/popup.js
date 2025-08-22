const CONFIG = {
    serverUrl: 'https://wellcoded.eu',
    apiKey: 'WellCodedJUTSUFREE'
};

document.addEventListener('DOMContentLoaded', function() {
    const activateBtn = document.getElementById('activateBtn');
    const status = document.getElementById('status');

    activateBtn.addEventListener('click', async function() {
        activateBtn.disabled = true;
        activateBtn.textContent = 'Загрузка...';
        status.className = 'loading';
        status.textContent = 'Получение видео';

        try {
            const [tab] = await chrome.tabs.query({active: true, currentWindow: true});

            if (!tab.url.includes('jut.su')) {
                throw new Error('Только для jut.su');
            }

            const response = await fetch(`${CONFIG.serverUrl}/api/extract`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    url: tab.url,
                    api_key: CONFIG.apiKey
                })
            });

            const data = await response.json();

            if (data.success && data.video_url) {
                status.textContent = 'Встраивание';

                await chrome.scripting.executeScript({
                    target: { tabId: tab.id },
                    func: injectVideoFunction,
                    args: [data.video_url, tab.url]
                });

                status.className = 'success';
                status.textContent = 'Готово';

                setTimeout(() => window.close(), 1000);

            } else {
                throw new Error(data.error || 'Ошибка');
            }

        } catch (error) {
            status.className = 'error';
            status.textContent = error.message;
        }

        activateBtn.disabled = false;
        activateBtn.textContent = 'Активировать';
    });
});

function injectVideoFunction(mp4Url, pageUrl) {

    document.querySelectorAll('.tab_need_plus, .plus_shareplay_ad, .question_use_old_player, #wap_player_use_old').forEach(el => el.remove());

    const video = document.querySelector('#my-player_html5_api');
    if (video) {
        video.src = mp4Url;
        document.querySelectorAll('#my-player source').forEach(source => {
            const res = source.getAttribute('res') || '720';
            source.src = mp4Url.replace('1080', res);
        });
        video.load();
    }

    const postMedia = document.querySelector('.post_media');
    if (postMedia) postMedia.classList.add('plus_player');
}