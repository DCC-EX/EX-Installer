import { DI } from 'aurelia'
import type {
    ArduinoCliPlatformInfo,
    ArduinoCliLibraryInfo,
    ArduinoCliBoardInfo,
    CompileResult,
    UploadResult,
} from '../../../types/ipc'

export const IArduinoCliService = DI.createInterface<ArduinoCliService>('IArduinoCliService')

/** Wraps window.arduinoCli (contextBridge API) for the renderer. */
export class ArduinoCliService {
    progressLog: Array<{ phase: string; message: string }> = []
    private readonly unsubscribers: Array<() => void> = []

    constructor() {
        if (window.arduinoCli) {
            this.unsubscribers.push(
                window.arduinoCli.onProgress((payload) => {
                    this.progressLog.push(payload)
                })
            )
        }
    }

    async isInstalled(): Promise<boolean> {
        return window.arduinoCli.isInstalled()
    }

    async getVersion(): Promise<string | null> {
        return window.arduinoCli.getVersion()
    }

    async downloadCli(): Promise<{ success: boolean; error?: string }> {
        return window.arduinoCli.downloadCli()
    }

    async installPlatform(platform: string, version?: string): Promise<{ success: boolean; error?: string }> {
        return window.arduinoCli.installPlatform(platform, version)
    }

    async installLibrary(library: string, version?: string): Promise<{ success: boolean; error?: string }> {
        return window.arduinoCli.installLibrary(library, version)
    }

    async getPlatforms(): Promise<ArduinoCliPlatformInfo[]> {
        return window.arduinoCli.getPlatforms()
    }

    async getLibraries(): Promise<ArduinoCliLibraryInfo[]> {
        return window.arduinoCli.getLibraries()
    }

    async listBoards(): Promise<ArduinoCliBoardInfo[]> {
        return window.arduinoCli.listBoards()
    }

    async compile(sketchPath: string, fqbn: string): Promise<CompileResult> {
        return window.arduinoCli.compile(sketchPath, fqbn)
    }

    async upload(sketchPath: string, fqbn: string, port: string): Promise<UploadResult> {
        return window.arduinoCli.upload(sketchPath, fqbn, port)
    }

    async initConfig(): Promise<{ success: boolean; error?: string }> {
        return window.arduinoCli.initConfig()
    }

    async updateIndex(): Promise<{ success: boolean; error?: string }> {
        return window.arduinoCli.updateIndex()
    }

    async getBundledVersion(): Promise<string> {
        return window.arduinoCli.getBundledVersion()
    }

    async browseBinary(): Promise<string | null> {
        return window.arduinoCli.browseBinary()
    }

    async browsePlatformArchive(): Promise<string | null> {
        return window.arduinoCli.browsePlatformArchive()
    }

    async validateBinary(binaryPath: string): Promise<{ success: boolean; version?: string; error?: string }> {
        return window.arduinoCli.validateBinary(binaryPath)
    }

    async setCustomPath(binaryPath: string): Promise<{ success: boolean }> {
        return window.arduinoCli.setCustomPath(binaryPath)
    }

    async installFromArchive(archivePath: string): Promise<{ success: boolean; error?: string }> {
        return window.arduinoCli.installFromArchive(archivePath)
    }

    async checkPlatform(platformId: string): Promise<{ installed: boolean; version: string | null }> {
        return window.arduinoCli.checkPlatform(platformId)
    }

    async installPlatformFromArchive(
        archivePath: string,
        platformId: string,
        version: string,
    ): Promise<{ success: boolean; error?: string }> {
        return window.arduinoCli.installPlatformFromArchive(archivePath, platformId, version)
    }

    dispose(): void {
        this.unsubscribers.forEach((fn) => fn())
        this.unsubscribers.length = 0
    }
}
