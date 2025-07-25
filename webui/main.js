// 国际化文本配置
const i18n = {
  zh: {
    title: "文件解析服务",
    apiKeyLabel: "API Key：",
    apiKeyPlaceholder: "请输入API Key",
    saveKeyBtn: "保存API Key",
    functionLabel: "选择功能：",
    convertMode: "文档转换",
    ocrMode: "图片OCR识别",
    fileInputLabel: "选择文件：",
    uploadBtn: "上传并处理",
    processing: "处理中...",
    convertResult: "文档转换结果",
    ocrResult: "OCR识别结果",
    filename: "文件名",
    fileSize: "文件大小",
    processTime: "处理时间",
    fromCache: "是否来自缓存",
    convertContent: "转换内容",
    ocrText: "识别文本",
    error: "错误",
    saveSuccess: "API Key 已保存！",
    pleaseEnterKey: "请输入API Key",
    pleaseSelectFile: "请选择要上传的文件",
    pleaseSaveKey: "请先输入并保存API Key",
    yes: "是",
    no: "否",
    loadingSupportedTypes: "正在加载支持的文件类型...",
    failedToLoadTypes: "加载支持的文件类型失败"
  },
  en: {
    title: "File Parser Service",
    apiKeyLabel: "API Key:",
    apiKeyPlaceholder: "Please enter API Key",
    saveKeyBtn: "Save API Key",
    functionLabel: "Select Function:",
    convertMode: "Document Conversion",
    ocrMode: "Image OCR Recognition",
    fileInputLabel: "Select File:",
    uploadBtn: "Upload & Process",
    processing: "Processing...",
    convertResult: "Document Conversion Result",
    ocrResult: "OCR Recognition Result",
    filename: "Filename",
    fileSize: "File Size",
    processTime: "Process Time",
    fromCache: "From Cache",
    convertContent: "Converted Content",
    ocrText: "Recognized Text",
    error: "Error",
    saveSuccess: "API Key saved successfully!",
    pleaseEnterKey: "Please enter API Key",
    pleaseSelectFile: "Please select a file to upload",
    pleaseSaveKey: "Please enter and save API Key first",
    yes: "Yes",
    no: "No",
    loadingSupportedTypes: "Loading supported file types...",
    failedToLoadTypes: "Failed to load supported file types"
  }
};

// 当前语言
let currentLang = localStorage.getItem('language') || 'zh';

// 支持的文件类型（动态获取）
let supportedExtensions = [];
let imageExtensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif', '.webp'];

// 动态获取支持的文件类型
async function loadSupportedTypes() {
  const apiKey = localStorage.getItem('apiKey');
  if (!apiKey) {
    console.log('No API key found, using default file types');
    updateSupportedTypesDisplay(123); // 使用默认数量
    return;
  }

  try {
    const response = await fetch('/v1/supported-types', {
      headers: {
        'Authorization': `Bearer ${apiKey}`
      }
    });

    if (response.ok) {
      const data = await response.json();
      supportedExtensions = data.supported_extensions || [];
      console.log(`Loaded ${supportedExtensions.length} supported file types`);
      updateSupportedTypesDisplay(supportedExtensions.length);
    } else {
      console.warn('Failed to load supported types, using defaults');
      updateSupportedTypesDisplay(123);
    }
  } catch (error) {
    console.warn('Error loading supported types:', error);
    updateSupportedTypesDisplay(123);
  }
}

// 更新支持文件类型显示
function updateSupportedTypesDisplay(count) {
  const countElement = document.getElementById('supportedTypesCount');
  if (countElement) {
    if (currentLang === 'zh') {
      countElement.textContent = `支持 ${count} 种文件格式`;
    } else {
      countElement.textContent = `Supports ${count} file formats`;
    }
  }
}

// 应用语言
function applyLanguage(lang) {
  currentLang = lang;
  localStorage.setItem('language', lang);
  
  // 更新所有带有 data-i18n 属性的元素
  document.querySelectorAll('[data-i18n]').forEach(element => {
    const key = element.getAttribute('data-i18n');
    if (i18n[lang][key]) {
      element.textContent = i18n[lang][key];
    }
  });
  
  // 更新所有带有 data-i18n-placeholder 属性的元素
  document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
    const key = element.getAttribute('data-i18n-placeholder');
    if (i18n[lang][key]) {
      element.placeholder = i18n[lang][key];
    }
  });
  
  // 更新语言按钮状态
  document.querySelectorAll('.language-btn').forEach(btn => {
    btn.classList.remove('active');
  });
  document.querySelector(`[data-lang="${lang}"]`).classList.add('active');
  
  // 更新文件类型显示
  updateSupportedTypesDisplay(supportedExtensions.length || 123);
}

// 读取localStorage中的API Key
window.onload = async function() {
  const apiKey = localStorage.getItem('apiKey');
  if (apiKey) {
    document.getElementById('apiKey').value = apiKey;
  }
  
  // 应用保存的语言设置
  applyLanguage(currentLang);
  
  // 加载支持的文件类型
  await loadSupportedTypes();
  
  // 添加语言切换事件监听
  document.querySelectorAll('.language-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      const lang = this.getAttribute('data-lang');
      applyLanguage(lang);
    });
  });
  
  // 添加模式切换事件监听
  document.getElementById('convertMode').addEventListener('change', updateFileInput);
  document.getElementById('ocrMode').addEventListener('change', updateFileInput);
  
  // 初始化文件输入提示
  updateFileInput();
};

// 根据选择的模式更新文件输入提示
function updateFileInput() {
  const convertMode = document.getElementById('convertMode');
  const fileInput = document.getElementById('fileInput');
  
  if (convertMode.checked) {
    // 使用动态获取的支持文件类型，如果没有则使用默认值
    const acceptTypes = supportedExtensions.length > 0 
      ? supportedExtensions.join(',') 
      : '.pdf,.docx,.doc,.rtf,.odt,.txt,.xlsx,.xls,.csv,.pptx,.md,.pages,.numbers,.keynote,.svg,.py,.js,.java,.cpp,.c,.html,.css,.json,.xml,.yaml,.yml';
    
    fileInput.accept = acceptTypes;
    fileInput.title = currentLang === 'zh' 
      ? `支持 ${supportedExtensions.length || 123} 种文件格式，包括文档、表格、演示文稿、图片、代码等` 
      : `Supports ${supportedExtensions.length || 123} file formats including documents, spreadsheets, presentations, images, code and more`;
  } else {
    fileInput.accept = imageExtensions.join(',');
    fileInput.title = currentLang === 'zh' 
      ? '仅支持图片格式：JPG, PNG, BMP, TIFF, GIF, WebP' 
      : 'Only supports image formats: JPG, PNG, BMP, TIFF, GIF, WebP';
  }
}

document.getElementById('saveKeyBtn').onclick = async function() {
  const key = document.getElementById('apiKey').value.trim();
  if (key) {
    localStorage.setItem('apiKey', key);
    alert(i18n[currentLang].saveSuccess);
    
    // 保存API Key后重新加载支持的文件类型
    await loadSupportedTypes();
    updateFileInput();
  } else {
    alert(i18n[currentLang].pleaseEnterKey);
  }
};

document.getElementById('uploadBtn').onclick = async function() {
  const apiKey = localStorage.getItem('apiKey');
  const fileInput = document.getElementById('fileInput');
  const resultDiv = document.getElementById('result');
  const convertMode = document.getElementById('convertMode');
  const uploadBtn = document.getElementById('uploadBtn');
  const loadingSpinner = document.getElementById('loadingSpinner');
  const buttonText = document.getElementById('buttonText');
  
  resultDiv.style.display = 'none';
  resultDiv.innerText = '';

  if (!apiKey) {
    alert(i18n[currentLang].pleaseSaveKey);
    return;
  }
  if (!fileInput.files.length) {
    alert(i18n[currentLang].pleaseSelectFile);
    return;
  }

  // 显示加载状态
  uploadBtn.disabled = true;
  loadingSpinner.style.display = 'inline-block';
      buttonText.textContent = i18n[currentLang].processing;

  const file = fileInput.files[0];
  const formData = new FormData();
  formData.append('file', file);

  // 根据选择的模式决定调用哪个接口
  const endpoint = convertMode.checked ? '/v1/convert' : '/v1/ocr';
  const modeName = convertMode.checked ? (currentLang === 'zh' ? '文档转换' : 'Document Conversion') : (currentLang === 'zh' ? 'OCR识别' : 'OCR Recognition');

  try {
    console.log(`${currentLang === 'zh' ? '开始' : 'Starting'} ${modeName}，${currentLang === 'zh' ? '调用接口' : 'calling endpoint'}: ${endpoint}`);
    
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`
      },
      body: formData
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`${currentLang === 'zh' ? '上传失败' : 'Upload failed'} (${response.status}): ${errorText}`);
    }
    
    const data = await response.json();
    resultDiv.style.display = 'block';
    
    // 根据不同的接口返回格式显示结果
    if (convertMode.checked) {
      // 文档转换结果
      resultDiv.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: space-between;">
          <h3 style="margin:0;">${i18n[currentLang].convertResult}</h3>
          <button id="copyBtn" style="margin-left:auto;">${currentLang === 'zh' ? '复制内容' : 'Copy Content'}</button>
        </div>
        <p><strong>${i18n[currentLang].filename}:</strong> ${data.filename}</p>
        <p><strong>${i18n[currentLang].fileSize}:</strong> ${data.size} bytes</p>
        <p><strong>${i18n[currentLang].processTime}:</strong> ${data.duration_ms}ms</p>
        <p><strong>${i18n[currentLang].fromCache}:</strong> ${data.from_cache ? i18n[currentLang].yes : i18n[currentLang].no}</p>
        <hr>
        <h4>${i18n[currentLang].convertContent}:</h4>
        <pre id="resultContent" style="white-space: pre-wrap; word-wrap: break-word;">${data.content}</pre>
      `;
    } else {
      // OCR识别结果
      resultDiv.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: space-between;">
          <h3 style="margin:0;">${i18n[currentLang].ocrResult}</h3>
          <button id="copyBtn" style="margin-left:auto;">${currentLang === 'zh' ? '复制内容' : 'Copy Content'}</button>
        </div>
        <p><strong>${i18n[currentLang].filename}:</strong> ${data.filename}</p>
        <p><strong>${i18n[currentLang].fileSize}:</strong> ${data.size} bytes</p>
        <p><strong>${i18n[currentLang].processTime}:</strong> ${data.duration_ms}ms</p>
        <p><strong>${i18n[currentLang].fromCache}:</strong> ${data.from_cache ? i18n[currentLang].yes : i18n[currentLang].no}</p>
        <hr>
        <h4>${i18n[currentLang].ocrText}:</h4>
        <pre id="resultContent" style="white-space: pre-wrap; word-wrap: break-word;">${data.ocr_text}</pre>
      `;
    }
    // 复制按钮逻辑
    const copyBtn = document.getElementById('copyBtn');
    if (copyBtn) {
      copyBtn.onclick = function() {
        const content = document.getElementById('resultContent').innerText;
        navigator.clipboard.writeText(content).then(() => {
          copyBtn.textContent = currentLang === 'zh' ? '已复制!' : 'Copied!';
          copyBtn.style.background = '#1976d2';
          copyBtn.style.color = '#fff';
          setTimeout(() => {
            copyBtn.textContent = currentLang === 'zh' ? '复制内容' : 'Copy Content';
            copyBtn.style.background = '';
            copyBtn.style.color = '';
          }, 1200);
        });
      };
    }
  } catch (err) {
    resultDiv.style.display = 'block';
    resultDiv.innerHTML = `<h3>${i18n[currentLang].error}</h3><p style="color: red;">${err.message}</p>`;
  } finally {
    // 恢复按钮状态
    uploadBtn.disabled = false;
    loadingSpinner.style.display = 'none';
    buttonText.textContent = i18n[currentLang].uploadBtn;
  }
}; 