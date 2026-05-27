// Initialize ACE Editors
const editorLeft = ace.edit("editor-left");
editorLeft.setTheme("ace/theme/vs-dark");
editorLeft.session.setMode("ace/mode/text");

const editorRight = ace.edit("editor-right");
editorRight.setTheme("ace/theme/vs-dark");
editorRight.session.setMode("ace/mode/python");

// Requirements: Make right pane editable manually
editorRight.setReadOnly(false);

const statusEl = document.getElementById("status");

// Handle split pane resizing functionally
const container = document.querySelector('.container');
const paneLeft = document.querySelectorAll('.pane')[0];
const paneRight = document.querySelectorAll('.pane')[1];
const divider = document.querySelector('.divider');

let isDragging = false;

divider.addEventListener('mousedown', function(e) {
    isDragging = true;
});

document.addEventListener('mousemove', function(e) {
    if (!isDragging) return;
    
    // Prevent selection while dragging
    e.preventDefault();
    
    const containerRect = container.getBoundingClientRect();
    const newLeftWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100;
    
    if (newLeftWidth > 10 && newLeftWidth < 90) {
        paneLeft.style.flex = `0 0 ${newLeftWidth}%`;
        paneRight.style.flex = `0 0 ${100 - newLeftWidth}%`;
        editorLeft.resize();
        editorRight.resize();
    }
});

document.addEventListener('mouseup', function(e) {
    isDragging = false;
});

// Setup debounce for live translation via our Local Python API
let debounceTimer;
let isInternalUpdate = false;

editorLeft.session.on('change', function() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(translateCode, 500); // 500ms debounce buffer
});

async function translateCode() {
    const clrsCode = editorLeft.getValue();
    
    if (!clrsCode.trim()) {
        isInternalUpdate = true;
        editorRight.setValue("");
        editorRight.clearSelection();
        isInternalUpdate = false;
        statusEl.innerText = "Ready";
        statusEl.className = "status";
        return;
    }
    
    statusEl.innerText = "Translating...";
    statusEl.className = "status";
    
    try {
        const response = await fetch('/api/translate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ code: clrsCode })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            isInternalUpdate = true;
            // Retain scroll position logic
            const currentPosition = editorRight.getCursorPosition();
            editorRight.setValue(data.result);
            editorRight.clearSelection();
            editorRight.moveCursorToPosition(currentPosition);
            isInternalUpdate = false;
            
            statusEl.innerText = "Success";
            statusEl.className = "status success";
        } else {
            statusEl.innerText = "Syntax Error";
            statusEl.className = "status error";
            console.error(data.error);
        }
    } catch (err) {
        statusEl.innerText = "Connection Error";
        statusEl.className = "status error";
        console.error("Translation request failed:", err);
    }
}

// Set initial pseudo code matching the sample image exactly
const initialCode = `for j = 2 to n
    key = A[j]
    i = j - 1
    while i > 0 and A[i] > key
        A[i + 1] = A[i]
        i = i - 1
    A[i + 1] = key`;

editorLeft.setValue(initialCode);
editorLeft.clearSelection();

// Trigger initial translate sequence visually
translateCode();
