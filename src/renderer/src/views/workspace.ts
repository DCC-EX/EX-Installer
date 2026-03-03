import { resolve } from 'aurelia'
import { Router } from '@aurelia/router'
import { IDialogService } from '@aurelia/dialog'
import { InstallerState } from '../models/installer-state'
import { PreferencesService } from '../services/preferences.service'
import { FileService } from '../services/file.service'
import { ArduinoCliService } from '../services/arduino-cli.service'
import { ConfigService } from '../services/config.service'
import { DeviceWizard } from '../components/device-wizard'
import { productDetails } from '../models/product-details'
import type { SavedConfiguration } from '../models/saved-configuration'

export class Workspace {
    private readonly router = resolve(Router)
    private readonly dialogService = resolve(IDialogService)
    readonly state = resolve(InstallerState)
    private readonly preferences = resolve(PreferencesService)
    private readonly files = resolve(FileService)
    private readonly cli = resolve(ArduinoCliService)
    private readonly config = resolve(ConfigService)

    // ── Active config file being edited ─────────────────────────────────────
    activeFileIndex = 0

    isMock = false

    // ── Compile / upload state ───────────────────────────────────────────────
    isCompiling = false
    compileLog = ''
    compileSuccess: boolean | null = null
    compileError: string | null = null
    progressPercent = 0

    // ── Menu ─────────────────────────────────────────────────────────────────
    showDeviceMenu = false
    savedConfigs: SavedConfiguration[] = []

    async binding(): Promise<void> {
        await this.config.ready
        this.isMock = this.config.isMock
        if (!this.state.selectedDevice) {
            await this.router.load('home')
            return
        }
        await this.loadSavedConfigs()
        await this.refreshConfigFilesFromDisk()
    }

    /**
     * Re-reads each config file from disk, replacing any empty content.
     * This heals stale saved configs and handles the first-ever load after
     * the mock repo is seeded.
     */
    private async refreshConfigFilesFromDisk(): Promise<void> {
        if (!this.state.scratchPath) return
        let changed = false
        for (const f of this.state.configFiles) {
            if (f.content.trim() !== '') continue  // already has content
            const diskPath = `${this.state.scratchPath}/${f.name}`
            const diskExists = await this.files.exists(diskPath)
            if (diskExists) {
                f.content = await this.files.readFile(diskPath)
                changed = true
            }
        }
        if (changed) await this.updateSavedConfig()
    }

    private async loadSavedConfigs(): Promise<void> {
        try {
            const saved = await this.preferences.get('savedConfigurations') as SavedConfiguration[] | undefined
            this.savedConfigs = Array.isArray(saved) ? saved : this.state.savedConfigurations
        } catch {
            this.savedConfigs = this.state.savedConfigurations
        }
    }

    // ── Config file editing ───────────────────────────────────────────────────
    get activeFile(): { name: string; content: string } | null {
        return this.state.configFiles[this.activeFileIndex] ?? null
    }

    setActiveFile(index: number): void {
        this.activeFile && this.syncContent()
        this.activeFileIndex = index
    }

    syncContent(): void {
        // content is already two-way bound via textarea; nothing extra needed
    }

    async saveFiles(): Promise<void> {
        for (const f of this.state.configFiles) {
            if (this.state.scratchPath) {
                await this.files.writeFile(`${this.state.scratchPath}/${f.name}`, f.content)
            }
        }
        await this.updateSavedConfig()
    }

    private async updateSavedConfig(): Promise<void> {
        const id = this.state.activeConfigId
        if (!id) return
        const idx = this.state.savedConfigurations.findIndex((c) => c.id === id)
        if (idx === -1) return
        this.state.savedConfigurations[idx] = {
            ...this.state.savedConfigurations[idx],
            configFiles: this.state.configFiles.map((f) => ({ ...f })),
            lastModified: new Date().toISOString(),
        }
        await this.preferences.set('savedConfigurations', this.state.savedConfigurations)
    }

    // ── Compile & Upload ──────────────────────────────────────────────────────
    clearCompileLog(): void {
        this.compileLog = ''
        this.compileSuccess = null
        this.compileError = null
    }

    async compile(): Promise<void> {
        const device = this.state.selectedDevice
        if (!device || !this.state.scratchPath) return

        this.isCompiling = true
        this.compileLog = ''
        this.compileError = null
        this.compileSuccess = null
        this.progressPercent = 10

        try {
            await this.saveFiles()
            this.progressPercent = 20

            const fqbn = device.fqbn
            if (!fqbn) {
                throw new Error(`Board "${device.name}" has no FQBN — install Arduino CLI and rescan to identify it.`)
            }

            this.compileLog += `Compiling for ${fqbn}...\n`
            this.progressPercent = 40
            const result = await this.cli.compile(this.state.scratchPath!, fqbn)
            this.compileLog += result.output ?? ''
            if (!result.success) throw new Error(result.error ?? 'Compilation failed')

            this.progressPercent = 70
            this.compileSuccess = true
            this.compileLog += '\n✓ Compile successful!'
        } catch (err) {
            this.compileError = (err as Error).message
            this.compileSuccess = false
        } finally {
            this.isCompiling = false
        }
    }

    async upload(): Promise<void> {
        const device = this.state.selectedDevice
        if (!device || !this.state.scratchPath) return

        this.isCompiling = true
        this.compileError = null
        this.progressPercent = 75

        try {
            const fqbn = device.fqbn
            if (!fqbn) {
                throw new Error(`Board "${device.name}" has no FQBN — install Arduino CLI and rescan to identify it.`)
            }

            this.compileLog += `\nUploading to ${device.port}...\n`
            this.progressPercent = 80
            const result = await this.cli.upload(this.state.scratchPath!, fqbn, device.port)
            this.compileLog += result.output ?? ''
            if (!result.success) throw new Error(result.error ?? 'Upload failed')

            this.progressPercent = 100
            this.compileSuccess = true
            this.compileLog += '\n✓ Upload complete!'
        } catch (err) {
            this.compileError = (err as Error).message
            this.compileSuccess = false
        } finally {
            this.isCompiling = false
        }
    }

    async compileAndUpload(): Promise<void> {
        await this.compile()
        if (this.compileSuccess) {
            await this.upload()
        }
    }

    // ── Device switching ──────────────────────────────────────────────────────
    toggleDeviceMenu(): void {
        this.showDeviceMenu = !this.showDeviceMenu
    }

    async switchToConfig(config: SavedConfiguration): Promise<void> {
        this.showDeviceMenu = false
        this.state.selectedDevice = { name: config.deviceName, port: config.devicePort, fqbn: config.deviceFqbn, protocol: 'serial' }
        this.state.selectedProduct = config.product
        this.state.selectedVersion = config.version
        this.state.repoPath = config.repoPath
        this.state.scratchPath = config.scratchPath
        this.state.configFiles = config.configFiles.map((f) => ({ ...f }))
        this.state.activeConfigId = config.id
        this.activeFileIndex = 0
        this.compileLog = ''
        this.compileSuccess = null
        await this.refreshConfigFilesFromDisk()
    }

    async addNewDevice(): Promise<void> {
        this.showDeviceMenu = false
        this.state.reset()
        const result = await this.dialogService
            .open({ component: () => DeviceWizard })
            .whenClosed((r) => r)
        if (typeof result === 'object' && result !== null && 'status' in result && (result as any).status === 'ok') {
            await this.loadSavedConfigs()
            // The wizard stored the new config in state directly and in savedConfigurations.
            // Re-apply it via switchToConfig so configFiles / repoPath are all in sync.
            const newId = ((result as any).value as { id: string } | undefined)?.id
            const newConfig = this.state.savedConfigurations.find((c) => c.id === newId)
            if (newConfig) {
                await this.switchToConfig(newConfig)
            }
        }
    }

    async deleteConfig(config: SavedConfiguration, event: Event): Promise<void> {
        event.stopPropagation()
        this.state.savedConfigurations = this.state.savedConfigurations.filter((c) => c.id !== config.id)
        this.savedConfigs = this.savedConfigs.filter((c) => c.id !== config.id)
        await this.preferences.set('savedConfigurations', this.state.savedConfigurations)
        // If the deleted config was the one open, switch to the next or go home
        if (config.id === this.state.activeConfigId) {
            const next = this.savedConfigs[0]
            if (next) {
                await this.switchToConfig(next)
            } else {
                this.showDeviceMenu = false
                this.router.load('home')
            }
        }
    }

    goHome(): void {
        this.router.load('home')
    }

    get productName(): string {
        const key = this.state.selectedProduct
        return key ? (productDetails[key]?.productName ?? key) : ''
    }

    get activeConfigName(): string {
        const id = this.state.activeConfigId
        if (!id) return this.state.selectedDevice?.name ?? ''
        return (
            this.savedConfigs.find((c) => c.id === id)?.name ??
            this.state.savedConfigurations.find((c) => c.id === id)?.name ??
            this.state.selectedDevice?.name ?? ''
        )
    }
}
