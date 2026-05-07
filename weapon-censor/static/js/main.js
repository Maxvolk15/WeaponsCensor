

let selectedFile = null;

const elements = {
    dropZone: document.getElementById('inputDropZone'),
    fileInput: document.getElementById('fileInput'),
    outputZone: document.getElementById('outputZone'),
    processBtn: document.getElementById('processBtn'),
    loadingDiv: document.getElementById('loading'),
    resultInfo: document.getElementById('resultInfo'),

    censorMethod: document.getElementById('censorMethod'),
    blurStrength: document.getElementById('blurStrength'),
    pixelSize: document.getElementById('pixelSize'),
    blurValue: document.getElementById('blurValue'),
    pixelValue: document.getElementById('pixelValue'),
    blurStrengthGroup: document.getElementById('blurStrengthGroup'),
    pixelSizeGroup: document.getElementById('pixelSizeGroup'),

    weaponsCount: document.getElementById('weaponsCount'),
    weaponsList: document.getElementById('weaponsList'),
};

function setupSliders() {
    elements.censorMethod.addEventListener('change', function () {
        const method = this.value;
        elements.blurStrengthGroup.style.display = method === 'blur' ? 'block' : 'none';
        elements.pixelSizeGroup.style.display = method === 'pixelate' ? 'block' : 'none';
    });

    elements.blurStrength.addEventListener('input', () => {
        elements.blurValue.textContent = elements.blurStrength.value;
    });

    elements.pixelSize.addEventListener('input', () => {
        elements.pixelValue.textContent = elements.pixelSize.value;
    });
}

function setupDragAndDrop() {
    elements.dropZone.addEventListener('click', () => {
        elements.fileInput.click();
    });

    elements.fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    const preventDefaults = (e) => {
        e.preventDefault();
        e.stopPropagation();
    };

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        elements.dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        elements.dropZone.addEventListener(eventName, () => {
            elements.dropZone.classList.add('drag-over');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        elements.dropZone.addEventListener(eventName, () => {
            elements.dropZone.classList.remove('drag-over');
        }, false);
    });

    elements.dropZone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });
}

function handleFile(file) {
    if (!file.type.startsWith('image/')) {
        alert('Пожалуйста, выберите изображение (JPG, PNG, GIF)');
        return;
    }

    selectedFile = file;

    const reader = new FileReader();
    reader.onload = (e) => {
        elements.dropZone.innerHTML = `<img src="${e.target.result}" alt="Загруженное фото">`;
        elements.processBtn.disabled = false;
    };
    reader.readAsDataURL(file);
}

async function processImage() {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('method', elements.censorMethod.value);
    formData.append('blur_strength', elements.blurStrength.value);
    formData.append('pixel_size', elements.pixelSize.value);

    setLoading(true);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData,
        });

        const data = await response.json();

        if (data.success) {
            showResult(data);
        } else {
            alert('Ошибка: ' + data.error);
        }
    } catch (error) {
        alert('Ошибка соединения: ' + error.message);
    } finally {
        setLoading(false);
    }
}

function showResult(data) {
    elements.outputZone.innerHTML = `<img src="${data.processed_image}" alt="Обработанное фото">`;

    elements.weaponsCount.textContent = data.weapons_found;

    elements.weaponsList.innerHTML = '';
    if (data.weapons_info && data.weapons_info.length > 0) {
        data.weapons_info.forEach(weapon => {
            elements.weaponsList.innerHTML += `
                <span class="weapon-tag">
                    🔫 ${weapon.class}
                    <span class="confidence">${Math.round(weapon.confidence * 100)}%</span>
                </span>
            `;
        });
    }

    elements.resultInfo.classList.add('show');
}

function setLoading(isLoading) {
    elements.processBtn.disabled = isLoading;
    elements.loadingDiv.style.display = isLoading ? 'block' : 'none';

    if (isLoading) {
        elements.resultInfo.classList.remove('show');
    }
}

function init() {
    setupSliders();
    setupDragAndDrop();

    elements.processBtn.addEventListener('click', processImage);
}

document.addEventListener('DOMContentLoaded', init);