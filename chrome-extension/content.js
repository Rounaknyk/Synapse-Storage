// Inject the floating widget into a Shadow DOM to isolate CSS
const host = document.createElement('div');
host.id = 'synapse-extension-root';
host.style.position = 'fixed';
host.style.bottom = '24px';
host.style.right = '24px';
host.style.zIndex = '2147483647';
document.body.appendChild(host);

const shadow = host.attachShadow({ mode: 'open' });

// Inject styles
const style = document.createElement('style');
style.textContent = `
    * { box-sizing: border-box; font-family: system-ui, sans-serif; }
    
    #widget {
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #7c3aed, #3b82f6);
        border-radius: 30px;
        box-shadow: 0 8px 32px rgba(124, 58, 237, 0.3);
        color: white;
        transition: all 0.3s cubic-bezier(0.25, 1, 0.5, 1);
        display: flex;
        flex-direction: column;
        overflow: hidden;
        cursor: pointer;
        position: absolute;
        bottom: 0;
        right: 0;
    }
    
    #widget.expanded {
        width: 360px;
        height: 520px;
        border-radius: 16px;
        background: #0a0a1a;
        border: 1px solid rgba(124, 58, 237, 0.4);
        cursor: default;
    }
    
    .fab-icon {
        position: absolute;
        top: 18px;
        left: 18px;
        width: 24px;
        height: 24px;
        transition: opacity 0.2s;
        fill: white;
    }
    
    #widget.expanded .fab-icon {
        opacity: 0;
        pointer-events: none;
    }
    
    .content {
        opacity: 0;
        transition: opacity 0.2s;
        pointer-events: none;
        padding: 20px;
        display: flex;
        flex-direction: column;
        height: 100%;
        color: #e2e8f0;
    }
    
    #widget.expanded .content {
        opacity: 1;
        pointer-events: all;
    }
    
    .header {
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .header svg { stroke: #a78bfa; }
    
    .search-input {
        width: 100%;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(124, 58, 237, 0.4);
        padding: 12px 14px;
        border-radius: 12px;
        color: white;
        outline: none;
        margin-bottom: 16px;
    }
    
    .search-input:focus {
        border-color: #a78bfa;
        background: rgba(124, 58, 237, 0.1);
    }
    
    #dynamic-area {
        flex: 1;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }
    
    .dropzone {
        flex: 1;
        border: 2px dashed rgba(124, 58, 237, 0.4);
        border-radius: 12px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        color: #94a3b8;
        background: rgba(0,0,0,0.2);
        transition: all 0.2s;
        margin-bottom: 16px;
    }
    
    .dropzone.dragover {
        border-color: #a78bfa;
        background: rgba(124, 58, 237, 0.15);
        color: white;
    }
    
    .rag-answer {
        background: linear-gradient(135deg, rgba(124,58,237,0.15), rgba(59,130,246,0.1));
        padding: 16px;
        border-radius: 12px;
        border: 1px solid rgba(124, 58, 237, 0.3);
        font-size: 0.9rem;
        line-height: 1.5;
        overflow-y: auto;
        flex: 1;
        margin-bottom: 16px;
    }
    
    .sources {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 8px;
        border-top: 1px solid rgba(255,255,255,0.1);
        padding-top: 8px;
    }
    
    .status {
        font-size: 0.85rem;
        color: #10b981;
        text-align: center;
        padding: 8px;
    }
    .status.error { color: #ef4444; }
    .status.loading { color: #a78bfa; }
    
    .close-btn {
        position: absolute;
        top: 16px;
        right: 16px;
        background: transparent;
        border: none;
        color: #94a3b8;
        cursor: pointer;
    }
    .close-btn:hover { color: white; }
`;

// Build UI
const widget = document.createElement('div');
widget.id = 'widget';

// SVG Icon for FAB
widget.innerHTML = `
    <svg class="fab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
        <polyline points="17 8 12 3 7 8"></polyline>
        <line x1="12" y1="3" x2="12" y2="15"></line>
    </svg>
    <div class="content">
        <button class="close-btn">✖</button>
        <div class="header">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
            Synapse Storage
        </div>
        
        <input type="text" class="search-input" placeholder="Ask AI about your docs..." />
        
        <div id="dynamic-area">
            <div class="dropzone" id="dropzone">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-bottom: 10px; stroke: #a78bfa;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
                Drop files here to upload<br>
                <small style="opacity: 0.7; margin-top: 4px;">PDF, MD, TXT, DOCX</small>
            </div>
        </div>
        
        <div id="status" class="status" style="display:none;"></div>
    </div>
`;

shadow.appendChild(style);
shadow.appendChild(widget);

// State & DOM Elements
let isExpanded = false;
const searchInput = shadow.querySelector('.search-input');
const dropzone = shadow.querySelector('#dropzone');
const dynamicArea = shadow.querySelector('#dynamic-area');
const statusEl = shadow.querySelector('#status');
const closeBtn = shadow.querySelector('.close-btn');

function showStatus(text, type = 'loading') {
    statusEl.textContent = text;
    statusEl.className = 'status ' + type;
    statusEl.style.display = 'block';
    setTimeout(() => { if (type !== 'loading') statusEl.style.display = 'none'; }, 4000);
}

// Expand/Collapse Logic
widget.addEventListener('mouseenter', () => {
    if (!isExpanded) {
        isExpanded = true;
        widget.classList.add('expanded');
        setTimeout(() => searchInput.focus(), 300);
    }
});

// Auto-expand when a file is dragged anywhere on the page
document.addEventListener('dragenter', (e) => {
    // Only expand if the dragged item might be a file
    if (e.dataTransfer && e.dataTransfer.types.includes('Files')) {
        if (!isExpanded) {
            isExpanded = true;
            widget.classList.add('expanded');
        }
    }
});

closeBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    isExpanded = false;
    widget.classList.remove('expanded');
    // Reset view
    searchInput.value = '';
    dynamicArea.innerHTML = `
        <div class="dropzone" id="dropzone">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-bottom: 10px; stroke: #a78bfa;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
            Drop files here to upload<br>
            <small style="opacity: 0.7; margin-top: 4px;">PDF, MD, TXT, DOCX</small>
        </div>
    `;
    attachDropzoneListeners(dynamicArea.querySelector('#dropzone'));
});

// Search Logic
searchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        const query = searchInput.value.trim();
        if (!query) return;

        showStatus('Thinking...', 'loading');
        dynamicArea.innerHTML = '<div style="flex:1; display:flex; align-items:center; justify-content:center; color:#a78bfa;">Querying Synapse AI...</div>';

        chrome.runtime.sendMessage({ action: 'search', query }, (response) => {
            if (response.success && response.data) {
                const { rag_answer, sources } = response.data;
                const sourceList = sources.map(s => s.file_name).join(', ');

                dynamicArea.innerHTML = `
                    <div class="rag-answer">
                        <strong style="color:var(--accent-violet-light)">✨ AI Answer:</strong><br><br>
                        ${rag_answer || "No relevant information found."}
                        ${sources.length > 0 ? `<div class="sources">Sources: ${sourceList}</div>` : ''}
                    </div>
                `;
                statusEl.style.display = 'none';
            } else {
                showStatus('Search failed', 'error');
            }
        });
    }
});

// Drag and Drop Upload Logic
function attachDropzoneListeners(dz) {
    if (!dz) return;

    dz.addEventListener('dragover', (e) => {
        e.preventDefault();
        dz.classList.add('dragover');
    });

    dz.addEventListener('dragleave', () => dz.classList.remove('dragover'));

    dz.addEventListener('drop', (e) => {
        e.preventDefault();
        dz.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length === 0) return;
        const file = files[0];

        showStatus('Uploading ' + file.name + '...', 'loading');

        const reader = new FileReader();
        reader.onload = () => {
            const base64Data = reader.result.split(',')[1];
            chrome.runtime.sendMessage({
                action: 'upload',
                fileData: base64Data,
                fileName: file.name,
                fileType: file.type || 'application/octet-stream'
            }, (response) => {
                if (response && response.success) {
                    const result = response.data;
                    showStatus(`Success! Classified as ${result.document_type}`, 'success');
                } else {
                    showStatus('Upload failed: ' + (response.error || 'Unknown error'), 'error');
                }
            });
        };
        reader.readAsDataURL(file);
    });
}

attachDropzoneListeners(dropzone);
