import { contextBridge, ipcRenderer, IpcRendererEvent } from 'electron'
import type {
    SerialDeviceInfo,
    UsbDeviceInfo,
    PythonJobOptions,
    PythonJobResult,
    ArduinoCliPlatformInfo,
    ArduinoCliLibraryInfo,
    ArduinoCliBoardInfo,
    CompileResult,
    UploadResult,
} from '../types/ipc'

// ── USB API ──────────────────────────────────────────────────────────────────
const usbApi = {
    listSerialPorts: (): Promise<SerialDeviceInfo[]> =>
        ipcRenderer.invoke('usb:list-serial-ports'),

    listUsbDevices: (): Promise<UsbDeviceInfo[]> =>
        ipcRenderer.invoke('usb:list-usb-devices'),

    openPort: (path: string, baudRate?: number): Promise<void> =>
        ipcRenderer.invoke('usb:open-port', path, baudRate),

    writeToPort: (path: string, data: string): Promise<void> =>
        ipcRenderer.invoke('usb:write-to-port', path, data),

    closePort: (path: string): Promise<void> =>
        ipcRenderer.invoke('usb:close-port', path),

    // ── Push-event subscriptions ─────────────────────────────────────────────
    onData: (cb: (payload: { path: string; data: string }) => void) => {
        const handler = (_: IpcRendererEvent, p: { path: string; data: string }) => cb(p)
        ipcRenderer.on('usb:data', handler)
        return () => ipcRenderer.off('usb:data', handler)
    },

    onError: (cb: (payload: { path: string; message: string }) => void) => {
        const handler = (_: IpcRendererEvent, p: { path: string; message: string }) => cb(p)
        ipcRenderer.on('usb:error', handler)
        return () => ipcRenderer.off('usb:error', handler)
    },

    onClosed: (cb: (payload: { path: string }) => void) => {
        const handler = (_: IpcRendererEvent, p: { path: string }) => cb(p)
        ipcRenderer.on('usb:closed', handler)
        return () => ipcRenderer.off('usb:closed', handler)
    },

    onAttached: (cb: (payload: { vendorId: number; productId: number }) => void) => {
        const handler = (_: IpcRendererEvent, p: { vendorId: number; productId: number }) => cb(p)
        ipcRenderer.on('usb:attached', handler)
        return () => ipcRenderer.off('usb:attached', handler)
    },

    onDetached: (cb: (payload: { vendorId: number; productId: number }) => void) => {
        const handler = (_: IpcRendererEvent, p: { vendorId: number; productId: number }) => cb(p)
        ipcRenderer.on('usb:detached', handler)
        return () => ipcRenderer.off('usb:detached', handler)
    },
}

// ── Python API ───────────────────────────────────────────────────────────────
const pythonApi = {
    run: (options: PythonJobOptions): Promise<PythonJobResult> =>
        ipcRenderer.invoke('python:run', options),

    send: (jobId: string, message: string): Promise<void> =>
        ipcRenderer.invoke('python:send', jobId, message),

    kill: (jobId: string): Promise<void> =>
        ipcRenderer.invoke('python:kill', jobId),

    // ── Push-event subscriptions ─────────────────────────────────────────────
    onStdout: (cb: (payload: { jobId: string; line: string }) => void) => {
        const handler = (_: IpcRendererEvent, p: { jobId: string; line: string }) => cb(p)
        ipcRenderer.on('python:stdout', handler)
        return () => ipcRenderer.off('python:stdout', handler)
    },

    onStderr: (cb: (payload: { jobId: string; line: string }) => void) => {
        const handler = (_: IpcRendererEvent, p: { jobId: string; line: string }) => cb(p)
        ipcRenderer.on('python:stderr', handler)
        return () => ipcRenderer.off('python:stderr', handler)
    },

    onDone: (cb: (result: PythonJobResult) => void) => {
        const handler = (_: IpcRendererEvent, r: PythonJobResult) => cb(r)
        ipcRenderer.on('python:done', handler)
        return () => ipcRenderer.off('python:done', handler)
    },

    onError: (cb: (payload: { jobId: string; message: string }) => void) => {
        const handler = (_: IpcRendererEvent, p: { jobId: string; message: string }) => cb(p)
        ipcRenderer.on('python:error', handler)
        return () => ipcRenderer.off('python:error', handler)
    },
}

// ── Expose to renderer via contextBridge ─────────────────────────────────────
contextBridge.exposeInMainWorld('usb', usbApi)
contextBridge.exposeInMainWorld('python', pythonApi)

// ── Arduino CLI API ──────────────────────────────────────────────────────────
const arduinoCliApi = {
    isInstalled: (): Promise<boolean> =>
        ipcRenderer.invoke('arduino-cli:is-installed'),

    getVersion: (): Promise<string | null> =>
        ipcRenderer.invoke('arduino-cli:get-version'),

    downloadCli: (): Promise<{ success: boolean; error?: string }> =>
        ipcRenderer.invoke('arduino-cli:download'),

    installPlatform: (platform: string, version?: string): Promise<{ success: boolean; error?: string }> =>
        ipcRenderer.invoke('arduino-cli:install-platform', platform, version),

    installLibrary: (library: string, version?: string): Promise<{ success: boolean; error?: string }> =>
        ipcRenderer.invoke('arduino-cli:install-library', library, version),

    getPlatforms: (): Promise<ArduinoCliPlatformInfo[]> =>
        ipcRenderer.invoke('arduino-cli:get-platforms'),

    getLibraries: (): Promise<ArduinoCliLibraryInfo[]> =>
        ipcRenderer.invoke('arduino-cli:get-libraries'),

    listBoards: (): Promise<ArduinoCliBoardInfo[]> =>
        ipcRenderer.invoke('arduino-cli:list-boards'),

    compile: (sketchPath: string, fqbn: string): Promise<CompileResult> =>
        ipcRenderer.invoke('arduino-cli:compile', sketchPath, fqbn),

    upload: (sketchPath: string, fqbn: string, port: string): Promise<UploadResult> =>
        ipcRenderer.invoke('arduino-cli:upload', sketchPath, fqbn, port),

    initConfig: (): Promise<{ success: boolean; error?: string }> =>
        ipcRenderer.invoke('arduino-cli:init-config'),

    updateIndex: (): Promise<{ success: boolean; error?: string }> =>
        ipcRenderer.invoke('arduino-cli:update-index'),

    getBundledVersion: (): Promise<string> =>
        ipcRenderer.invoke('arduino-cli:get-bundled-version'),

    browseBinary: (): Promise<string | null> =>
        ipcRenderer.invoke('arduino-cli:browse-binary'),

    browsePlatformArchive: (): Promise<string | null> =>
        ipcRenderer.invoke('arduino-cli:browse-platform-archive'),

    validateBinary: (binaryPath: string): Promise<{ success: boolean; version?: string; error?: string }> =>
        ipcRenderer.invoke('arduino-cli:validate-binary', binaryPath),

    setCustomPath: (binaryPath: string): Promise<{ success: boolean }> =>
        ipcRenderer.invoke('arduino-cli:set-custom-path', binaryPath),

    installFromArchive: (archivePath: string): Promise<{ success: boolean; error?: string }> =>
        ipcRenderer.invoke('arduino-cli:install-from-archive', archivePath),

    checkPlatform: (platformId: string): Promise<{ installed: boolean; version: string | null }> =>
        ipcRenderer.invoke('arduino-cli:check-platform', platformId),

    installPlatformFromArchive: (archivePath: string, platformId: string, version: string): Promise<{ success: boolean; error?: string }> =>
        ipcRenderer.invoke('arduino-cli:install-platform-from-archive', archivePath, platformId, version),

    onProgress: (cb: (payload: { phase: string; message: string }) => void) => {
        const handler = (_: IpcRendererEvent, p: { phase: string; message: string }) => cb(p)
        ipcRenderer.on('arduino-cli:progress', handler)
        return () => ipcRenderer.off('arduino-cli:progress', handler)
    },
}

// ── Git API ──────────────────────────────────────────────────────────────────
const gitApi = {
    clone: (url: string, dest: string, branch?: string): Promise<{ success: boolean; error?: string }> =>
        ipcRenderer.invoke('git:clone', url, dest, branch),

    pull: (repoPath: string): Promise<{ success: boolean; error?: string }> =>
        ipcRenderer.invoke('git:pull', repoPath),

    listTags: (repoPath: string): Promise<string[]> =>
        ipcRenderer.invoke('git:list-tags', repoPath),

    checkout: (repoPath: string, ref: string): Promise<{ success: boolean; error?: string }> =>
        ipcRenderer.invoke('git:checkout', repoPath, ref),

    checkLocalChanges: (repoPath: string): Promise<{ hasChanges: boolean; files: string[] }> =>
        ipcRenderer.invoke('git:check-local-changes', repoPath),

    hardReset: (repoPath: string): Promise<{ success: boolean; error?: string }> =>
        ipcRenderer.invoke('git:hard-reset', repoPath),
}

// ── File System API ──────────────────────────────────────────────────────────
const filesApi = {
    readFile: (filePath: string): Promise<string> =>
        ipcRenderer.invoke('files:read', filePath),

    writeFile: (filePath: string, content: string): Promise<void> =>
        ipcRenderer.invoke('files:write', filePath, content),

    listDir: (dirPath: string): Promise<string[]> =>
        ipcRenderer.invoke('files:list-dir', dirPath),

    exists: (filePath: string): Promise<boolean> =>
        ipcRenderer.invoke('files:exists', filePath),

    mkdir: (dirPath: string): Promise<void> =>
        ipcRenderer.invoke('files:mkdir', dirPath),

    copyFiles: (src: string, dest: string): Promise<void> =>
        ipcRenderer.invoke('files:copy', src, dest),

    deleteFiles: (filePath: string): Promise<void> =>
        ipcRenderer.invoke('files:delete', filePath),

    getInstallDir: (subdir?: string): Promise<string> =>
        ipcRenderer.invoke('files:get-install-dir', subdir),

    selectDirectory: (): Promise<string | null> =>
        ipcRenderer.invoke('files:select-directory'),
}

// ── Preferences API ──────────────────────────────────────────────────────────
const preferencesApi = {
    get: (key: string): Promise<unknown> =>
        ipcRenderer.invoke('preferences:get', key),

    set: (key: string, value: unknown): Promise<void> =>
        ipcRenderer.invoke('preferences:set', key, value),

    getAll: (): Promise<Record<string, unknown>> =>
        ipcRenderer.invoke('preferences:get-all'),
}

contextBridge.exposeInMainWorld('arduinoCli', arduinoCliApi)
contextBridge.exposeInMainWorld('git', gitApi)
contextBridge.exposeInMainWorld('files', filesApi)
contextBridge.exposeInMainWorld('preferences', preferencesApi)
// ── Config API ───────────────────────────────────────────────────────────────
const configApi = {
    getMock: (): Promise<boolean> =>
        ipcRenderer.invoke('config:get-mock'),
}

contextBridge.exposeInMainWorld('config', configApi)
