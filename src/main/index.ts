import { app, BrowserWindow, shell } from 'electron'
import { join } from 'path'
import { config } from './config'
import { registerAllIpcHandlers } from './ipc'
import { UsbManager } from './usb-manager'
import { PythonRunner } from './python-runner'
import { ArduinoCliService } from './arduino-cli'
import { GitService } from './git-client'
import { FileService } from './file-manager'
import { PreferencesService } from './preferences'

// ── Mock mode flag ──────────────────────────────────────────────────────────
/**
 * Runtime mock mode flag.
 *
 * Works for both `electron-vite dev -- --mock` and packaged executables
 * launched with `./EX-Installer --mock`.
 */
export const IS_DEV_MOCK =
    app.commandLine.hasSwitch('mock') || process.argv.includes('--mock')

if (config.disableHardwareAcceleration) app.disableHardwareAcceleration()

if (config.disableDBus && process.platform === 'linux') {
    process.env['DBUS_SESSION_BUS_ADDRESS'] ??= 'disabled:'
}
if (config.disableMediaSession) {
    app.commandLine.appendSwitch('disable-features', 'MediaSessionService')
}

// Enable Chromium remote DevTools protocol so VS Code's Chrome debugger
// can attach to the renderer process on port 9222 during development.
if (process.env['ELECTRON_RENDERER_URL']) {
    app.commandLine.appendSwitch('remote-debugging-port', '9222')
}

// ── Singletons shared between IPC handlers ──────────────────────────────────
export const usbManager = new UsbManager()
export const pythonRunner = new PythonRunner()
export const arduinoCliService = new ArduinoCliService()
export const gitService = new GitService()
export const fileService = new FileService()
export const preferencesService = new PreferencesService()

// ── Window factory ───────────────────────────────────────────────────────────
function createWindow(): BrowserWindow {
    const win = new BrowserWindow({
        width: config.window.width,
        height: config.window.height,
        minWidth: config.window.minWidth,
        minHeight: config.window.minHeight,
        resizable: config.window.resizable,
        maximizable: config.window.maximizable,
        show: false,
        autoHideMenuBar: true,
        webPreferences: {
            preload: join(__dirname, '../preload/index.js'),
            sandbox: false,
            contextIsolation: true,
            nodeIntegration: false,
        },
    })

    win.on('ready-to-show', () => {
        win.show()
        if (process.env['ELECTRON_RENDERER_URL']) {
            //win.webContents.openDevTools()
        }
    })

    // F5 or Ctrl+R / Cmd+R → reload the renderer
    // F12 or Ctrl+Shift+I / Cmd+Option+I → toggle DevTools
    win.webContents.on('before-input-event', (_event, input) => {
        if (input.type !== 'keyDown') return
        const reload =
            input.key === 'F5' ||
            ((input.control || input.meta) && input.key === 'r')
        if (reload) { win.webContents.reload(); return }

        const devtools =
            input.key === 'F12' ||
            ((input.control || input.meta) && input.shift && input.key === 'I')
        if (devtools) win.webContents.toggleDevTools()
    })

    // Open external links in the OS browser, not in Electron
    win.webContents.setWindowOpenHandler(({ url }) => {
        shell.openExternal(url)
        return { action: 'deny' }
    })

    if (process.env['ELECTRON_RENDERER_URL']) {
        // Dev: Vite dev-server URL injected by electron-vite
        win.loadURL(process.env['ELECTRON_RENDERER_URL'])
    } else {
        // Prod: load compiled HTML
        win.loadFile(join(__dirname, '../renderer/index.html'))
    }

    return win
}

// ── App lifecycle ────────────────────────────────────────────────────────────
app.whenReady().then(() => {
    registerAllIpcHandlers({
        usbManager,
        pythonRunner,
        arduinoCliService,
        gitService,
        fileService,
        preferencesService,
    })
    createWindow()

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) createWindow()
    })
})

app.on('window-all-closed', () => {
    usbManager.dispose()
    pythonRunner.killAll()
    if (process.platform !== 'darwin') app.quit()
})
