import { ipcMain, BrowserWindow, dialog } from 'electron'
import type { ArduinoCliService } from '../arduino-cli'
import { IS_DEV_MOCK } from '../index'
import { MOCK_SERIAL_PORTS } from '../dev-mock'

/** VID:PID → board name + FQBN (used for mock board identification). */
const KNOWN_BOARDS: Record<string, { name: string; fqbn: string }> = {
    '303a:1001': { name: 'EX-CSB1 (DCC-EX CommandStation Board 1)', fqbn: 'esp32:esp32:esp32' },
    '2341:0042': { name: 'Arduino Mega 2560', fqbn: 'arduino:avr:mega:cpu=atmega2560' },
    '2341:0010': { name: 'Arduino Mega 2560', fqbn: 'arduino:avr:mega' },
    '2341:0043': { name: 'Arduino Uno', fqbn: 'arduino:avr:uno' },
    '2341:0001': { name: 'Arduino Uno', fqbn: 'arduino:avr:uno' },
    '2341:0058': { name: 'Arduino Nano', fqbn: 'arduino:avr:nano' },
    '1a86:7523': { name: 'CH340 Serial (Nano/Mega clone)', fqbn: '' },
    '10c4:ea60': { name: 'CP2102 Serial (ESP32)', fqbn: 'esp32:esp32:esp32' },
    '0403:6001': { name: 'FTDI Serial Adapter', fqbn: '' },
}

export function registerArduinoCliIpcHandlers(arduinoCliService: ArduinoCliService): void {
    // Wire up progress events to renderer
    arduinoCliService.setProgressCallback((phase, message) => {
        BrowserWindow.getAllWindows().forEach((win) => {
            if (!win.isDestroyed()) win.webContents.send('arduino-cli:progress', { phase, message })
        })
    })

    ipcMain.handle('arduino-cli:is-installed', () => {
        return arduinoCliService.isInstalled()
    })

    ipcMain.handle('arduino-cli:get-version', async () => {
        return arduinoCliService.getVersion()
    })

    ipcMain.handle('arduino-cli:download', async () => {
        return arduinoCliService.downloadCli()
    })

    ipcMain.handle('arduino-cli:install-platform', async (_event, platform: string, version?: string) => {
        return arduinoCliService.installPlatform(platform, version)
    })

    ipcMain.handle('arduino-cli:install-library', async (_event, library: string, version?: string) => {
        return arduinoCliService.installLibrary(library, version)
    })

    ipcMain.handle('arduino-cli:get-platforms', async () => {
        return arduinoCliService.getPlatforms()
    })

    ipcMain.handle('arduino-cli:get-libraries', async () => {
        return arduinoCliService.getLibraries()
    })

    ipcMain.handle('arduino-cli:list-boards', async () => {
        if (IS_DEV_MOCK) {
            return MOCK_SERIAL_PORTS.map((sp) => {
                const vid = sp.vendorId?.toLowerCase() ?? ''
                const pid = sp.productId?.toLowerCase() ?? ''
                const lookup = KNOWN_BOARDS[`${vid}:${pid}`]
                return {
                    name: lookup?.name ?? sp.manufacturer ?? 'Unknown device',
                    fqbn: lookup?.fqbn ?? '',
                    port: sp.path,
                    protocol: 'serial' as const,
                    serialNumber: sp.serialNumber,
                }
            })
        }
        return arduinoCliService.listBoards()
    })

    ipcMain.handle('arduino-cli:compile', async (_event, sketchPath: string, fqbn: string) => {
        return arduinoCliService.compile(sketchPath, fqbn)
    })

    ipcMain.handle('arduino-cli:upload', async (_event, sketchPath: string, fqbn: string, port: string) => {
        return arduinoCliService.upload(sketchPath, fqbn, port)
    })

    ipcMain.handle('arduino-cli:init-config', async () => {
        return arduinoCliService.initConfig()
    })

    ipcMain.handle('arduino-cli:update-index', async () => {
        return arduinoCliService.updateIndex()
    })

    ipcMain.handle('arduino-cli:get-bundled-version', () => {
        return arduinoCliService.getBundledVersion()
    })

    // ── File-picker helpers ──────────────────────────────────────────────────

    ipcMain.handle('arduino-cli:browse-binary', async () => {
        const win = BrowserWindow.getFocusedWindow() ?? BrowserWindow.getAllWindows()[0]
        const result = await dialog.showOpenDialog(win, {
            title: 'Select Arduino CLI Binary or Archive',
            properties: ['openFile'],
            filters: [
                { name: 'Arduino CLI Binary', extensions: process.platform === 'win32' ? ['exe'] : [''] },
                { name: 'Archive', extensions: ['tar.gz', 'tgz', 'zip'] },
                { name: 'All Files', extensions: ['*'] },
            ],
        })
        return result.canceled ? null : (result.filePaths[0] ?? null)
    })

    ipcMain.handle('arduino-cli:browse-platform-archive', async () => {
        const win = BrowserWindow.getFocusedWindow() ?? BrowserWindow.getAllWindows()[0]
        const result = await dialog.showOpenDialog(win, {
            title: 'Select Platform Archive (.tar.gz / .zip)',
            properties: ['openFile'],
            filters: [
                { name: 'Archive', extensions: ['tar.gz', 'tgz', 'zip'] },
                { name: 'All Files', extensions: ['*'] },
            ],
        })
        return result.canceled ? null : (result.filePaths[0] ?? null)
    })

    ipcMain.handle('arduino-cli:validate-binary', async (_event, binaryPath: string) => {
        return arduinoCliService.validateBinary(binaryPath)
    })

    ipcMain.handle('arduino-cli:set-custom-path', (_event, binaryPath: string) => {
        arduinoCliService.setCustomBinaryPath(binaryPath)
        return { success: true }
    })

    ipcMain.handle('arduino-cli:install-from-archive', async (_event, archivePath: string) => {
        return arduinoCliService.installFromArchive(archivePath)
    })

    ipcMain.handle('arduino-cli:check-platform', async (_event, platformId: string) => {
        return arduinoCliService.checkPlatformInstalled(platformId)
    })

    ipcMain.handle('arduino-cli:install-platform-from-archive', async (
        _event,
        archivePath: string,
        platformId: string,
        version: string,
    ) => {
        return arduinoCliService.installPlatformFromArchive(archivePath, platformId, version)
    })
}
