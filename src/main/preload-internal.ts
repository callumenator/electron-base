const {contextBridge, ipcRenderer} = require('electron');

console.log('in preload, changed', document);

window.addEventListener('DOMContentLoaded', () => {
    const element = document.getElementById('chrome-version');
    if (element) {
        element.innerText = process.versions['chrome'];
    }
});

contextBridge.exposeInMainWorld('whoohooapi', {
    message: 'Hello',
});

// document.body.addEventListener("mousemove", (e) => {
//     ipc.send('event', { id: "${id}", x: e.offsetX, y: e.offsetY, });
// });