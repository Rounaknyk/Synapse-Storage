// background.js acts as an API proxy.
// Content scripts are subject to the host page's CSP and CORS policies.
// By routing requests through the background service worker, we bypass those restrictions.

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'search') {
        fetch('http://localhost:8000/search/smart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: request.query,
                top_k: 3,
                min_similarity: 0.0
            })
        })
            .then(res => res.json())
            .then(data => sendResponse({ success: true, data }))
            .catch(err => sendResponse({ success: false, error: err.message }));

        return true; // Keep the message channel open for async response
    }

    if (request.action === 'upload') {
        try {
            // Convert base64 string back to binary Blob
            const byteString = atob(request.fileData);
            const ab = new ArrayBuffer(byteString.length);
            const ia = new Uint8Array(ab);
            for (let i = 0; i < byteString.length; i++) {
                ia[i] = byteString.charCodeAt(i);
            }
            const blob = new Blob([ab], { type: request.fileType });

            const formData = new FormData();
            formData.append('file', blob, request.fileName);

            fetch('http://localhost:8000/upload', {
                method: 'POST',
                body: formData
            })
                .then(res => {
                    if (!res.ok) throw new Error('Upload failed with status ' + res.status);
                    return res.json();
                })
                .then(data => sendResponse({ success: true, data }))
                .catch(err => sendResponse({ success: false, error: err.message }));
        } catch (err) {
            sendResponse({ success: false, error: err.message });
        }

        return true; // Keep channel open
    }

    if (request.action === 'getUrl') {
        const url = `http://localhost:8000/download/${request.bucket}/${request.fileName}?inline=${request.inline}`;
        fetch(url)
            .then(res => {
                if (!res.ok) throw new Error('Failed to get URL');
                return res.json();
            })
            .then(data => sendResponse({ success: true, data }))
            .catch(err => sendResponse({ success: false, error: err.message }));
        return true;
    }

    if (request.action === 'delete') {
        fetch(`http://localhost:8000/documents/${request.bucket}/${request.fileName}`, {
            method: 'DELETE'
        })
            .then(res => {
                if (!res.ok) throw new Error('Delete failed');
                return res.json();
            })
            .then(data => sendResponse({ success: true, data }))
            .catch(err => sendResponse({ success: false, error: err.message }));
        return true;
    }
});
