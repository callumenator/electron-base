import {app, BrowserWindow, BrowserView} from 'electron'
import * as path from 'path'

const isDevelopment = process.env.NODE_ENV !== 'production'

let mainWindow: BrowserWindow;

function makeBrowser(cls: typeof BrowserWindow): BrowserWindow;
function makeBrowser(cls: typeof BrowserView): BrowserView;
function makeBrowser(cls: typeof BrowserWindow | typeof BrowserView): BrowserWindow | BrowserView {
    const view = new cls({
        webPreferences: {
            nodeIntegration: true,
            enableRemoteModule: false,
            contextIsolation: true,
            // Note: at this point, we are in dist, so we are actually getting the compiled preload
            // Also, this has to be an absolute path
            preload: path.resolve(path.join(__dirname, 'preload-internal.js')),
        }
    });

    view.webContents.on('dom-ready', () => {
    });

    view.webContents.on('console-message', (e, level, msg, line, sourdId) => {
        console.log('Got message:', msg);
    });

    return view;
}

function createMainWindow() {
    const rendererUrl = `http://${DEVSERVER_ADDRESS}:${DEVSERVER_PORT}/index.html`;
    const window = makeBrowser(BrowserWindow);
    const otherWindow = makeBrowser(BrowserView);
    window.addBrowserView(otherWindow);
    otherWindow.setBackgroundColor('#ffeeaa');
    otherWindow.setBounds({x: 0, y: 0, width: 300, height: 300})

    window.webContents.loadURL(rendererUrl);
    otherWindow.webContents.loadURL(rendererUrl)

    if (isDevelopment) {
        window.webContents.openDevTools()
    }

    window.on('closed', () => {
        mainWindow = null
    })

    window.webContents.on('devtools-opened', () => {
        window.focus()
        setImmediate(() => {
            window.focus()
        })
    })

    return window
}

// quit application when all windows are closed
app.on('window-all-closed', () => {
    // on macOS it is common for applications to stay open until the user explicitly quits
    if (process.platform !== 'darwin') {
        app.quit()
    }
})

app.on('activate', () => {
    // on macOS it is common to re-create a window even after all windows have been closed
    if (mainWindow === null) {
        mainWindow = createMainWindow()
    }
})

// create main BrowserWindow when electron is ready
app.on('ready', () => {
    mainWindow = createMainWindow()
})
