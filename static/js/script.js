const leftZone = document.getElementById('leftDropZone');
const rightZone = document.getElementById('rightZone');
const fileInput = document.getElementById('fileInput');
const refreshBtn = document.getElementById('refreshBtn');

let currentUploadedFile = null;
let currentResultUrl = null;

async function uploadFile(file) {
    if (!file.type.match('image/png')) {
        alert('Ошибка: можно загружать только PNG файлы!');
        return false;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/upload', { method: 'POST', body: formData });
        const data = await response.json();

        if (!response.ok) {
            alert(data.error || 'Ошибка загрузки');
            return false;
        }

        const previewUrl = data.preview_url;
        currentUploadedFile = previewUrl;
        displayImageInLeft(previewUrl);
        currentResultUrl = data.result_url;
        clearRightZone();

        return true;
    } catch (err) {
        console.error(err);
        alert('Сетевая ошибка: ' + err.message);
        return false;
    }
}

function displayImageInLeft(imageUrl) {
    leftZone.innerHTML = '';
    const img = document.createElement('img');
    img.src = imageUrl;
    img.alt = 'Загруженное фото';
    img.style.maxWidth = '100%';
    img.style.maxHeight = '350px';
    img.style.borderRadius = '0.75rem';
    leftZone.appendChild(img);
    leftZone.style.cursor = 'pointer';
}

function clearRightZone() {
    rightZone.innerHTML = '';
    const placeholderDiv = document.createElement('div');
    placeholderDiv.style.textAlign = 'center';
    placeholderDiv.innerHTML = `
        <div class="placeholder-icon">✨🔞</div>
        <div class="placeholder-text">Нажмите «Обновить» для обработки</div>
        <div class="download-hint">👇 Результат появится после нажатия</div>
    `;
    rightZone.appendChild(placeholderDiv);
    rightZone.style.cursor = 'default';
    rightZone.onclick = null;
}

function displayResultInRight(imageUrl) {
    rightZone.innerHTML = '';
    const img = document.createElement('img');
    img.src = imageUrl + '?t=' + new Date().getTime();
    img.alt = 'PseudoCensorship';
    img.style.maxWidth = '100%';
    img.style.maxHeight = '350px';
    img.style.borderRadius = '0.75rem';
    img.classList.add('right-image');
    rightZone.appendChild(img);
    rightZone.style.cursor = 'pointer';

    rightZone.onclick = () => {
        if (currentResultUrl) {
            const link = document.createElement('a');
            link.href = currentResultUrl;
            link.download = 'PseudoCensorship.png';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } else {
            alert('Нет доступного результата');
        }
    };
}

async function handleRefresh() {
    if (!currentUploadedFile) {
        alert('Сначала загрузите фото слева (перетащите или нажмите на левый экран)');
        return;
    }

    try {
        const response = await fetch('/process', { method: 'POST' });
        const data = await response.json();

        if (response.ok) {
            currentResultUrl = data.result_url;
            displayResultInRight(currentResultUrl);
        } else {
            alert('Ошибка обработки: ' + (data.error || 'неизвестная ошибка'));
        }
    } catch (e) {
        alert('Ошибка связи: ' + e.message);
    }
}

// Drag & Drop
leftZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    leftZone.classList.add('drag-over');
});

leftZone.addEventListener('dragleave', () => {
    leftZone.classList.remove('drag-over');
});

leftZone.addEventListener('drop', async (e) => {
    e.preventDefault();
    leftZone.classList.remove('drag-over');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        await uploadFile(files[0]);
    }
});

leftZone.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', async (e) => {
    if (e.target.files.length > 0) {
        await uploadFile(e.target.files[0]);
        fileInput.value = '';
    }
});

refreshBtn.addEventListener('click', handleRefresh);
clearRightZone();