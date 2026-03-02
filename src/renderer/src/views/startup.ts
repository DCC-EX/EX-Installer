import { resolve } from 'aurelia'
import { Router } from '@aurelia/router'
import { InstallerState } from '../models/installer-state'
import { ArduinoCliService } from '../services/arduino-cli.service'
import { extraPlatforms } from '../models/product-details'

type SetupPhase =
    | 'splash'
    | 'checking'
    | 'cli-prompt'
    | 'installing'
    | 'upgrade-prompt'
    | 'esp32-prompt'
    | 'esp32-installing'
    | 'ready'
    | 'error'

export class Startup {
    private readonly router = resolve(Router)
    private readonly state = resolve(InstallerState)
    private readonly cli = resolve(ArduinoCliService)

    phase: SetupPhase = 'splash'
    statusMessage = 'Checking Arduino CLI...'
    progress = 0
    installedVersion: string | null = null
    bundledVersion = ''
    /** General error shown in the error card. */
    error: string | null = null
    /** Inline error shown inside prompt cards. */
    browseError: string | null = null
    /** True while a browse+validate flow is in progress. */
    browseBusy = false

    /** ESP32 platform state */
    esp32InstalledVersion: string | null = null
    esp32UpdateAvailable = false // true = update prompt, false = fresh install prompt
    readonly esp32PlatformId = 'esp32:esp32'
    get esp32PlatformVersion(): string {
        return extraPlatforms['esp32:esp32'] ?? '2.0.17'
    }

    async attached(): Promise<void> {
        await this.checkAndSetup()
    }

    private async checkAndSetup(): Promise<void> {
        this.phase = 'checking'
        this.error = null
        this.browseError = null
        this.progress = 0

        try {
            this.bundledVersion = await this.cli.getBundledVersion()
            this.statusMessage = 'Checking Arduino CLI...'

            const isInstalled = await this.cli.isInstalled()
            if (!isInstalled) {
                this.phase = 'cli-prompt'
                return
            }

            this.installedVersion = await this.cli.getVersion()
            const installed = this.parseVersion(this.installedVersion ?? '')
            const bundled = this.parseVersion(this.bundledVersion)

            if (!installed) {
                // Binary exists but couldn't report a version — treat as broken/missing.
                this.phase = 'cli-prompt'
                return
            }

            if (installed !== bundled) {
                this.phase = 'upgrade-prompt'
            } else {
                await this.checkEsp32Platform()
            }
        } catch (err) {
            this.error = (err as Error).message
            this.phase = 'error'
        }
    }

    // ── ESP32 platform check ─────────────────────────────────────────────────

    private async checkEsp32Platform(): Promise<void> {
        this.phase = 'checking'
        this.statusMessage = 'Checking ESP32 platform...'
        try {
            const result = await this.cli.checkPlatform(this.esp32PlatformId)
            if (!result.installed) {
                this.esp32UpdateAvailable = false
                this.esp32InstalledVersion = null
                this.phase = 'esp32-prompt'
            } else {
                this.esp32InstalledVersion = result.version
                const required = this.esp32PlatformVersion
                if (result.version && result.version !== required) {
                    this.esp32UpdateAvailable = true
                    this.phase = 'esp32-prompt'
                } else {
                    this.markReady()
                }
            }
        } catch {
            // Non-fatal — platform check failure doesn't block launch
            this.markReady()
        }
    }

    // ── ESP32 prompt actions ─────────────────────────────────────────────────

    async downloadEsp32(): Promise<void> {
        this.phase = 'esp32-installing'
        this.browseError = null
        this.progress = 5
        try {
            this.statusMessage = 'Installing ESP32 platform...'
            const result = await this.cli.installPlatform(this.esp32PlatformId, this.esp32PlatformVersion)
            if (!result.success) throw new Error(result.error ?? 'Platform install failed')
            this.progress = 100
            this.markReady()
        } catch (err) {
            this.error = (err as Error).message
            this.phase = 'error'
        }
    }

    async browseEsp32Archive(): Promise<void> {
        this.browseError = null
        this.browseBusy = true
        try {
            const filePath = await this.cli.browsePlatformArchive()
            if (!filePath) return // cancelled

            this.phase = 'esp32-installing'
            this.progress = 5
            this.statusMessage = 'Extracting ESP32 platform...'

            const result = await this.cli.installPlatformFromArchive(
                filePath,
                this.esp32PlatformId,
                this.esp32PlatformVersion,
            )
            if (!result.success) throw new Error(result.error ?? 'Archive extraction failed')
            this.progress = 100
            this.markReady()
        } catch (err) {
            // Return to the prompt so the user can try again
            this.browseError = (err as Error).message
            this.phase = 'esp32-prompt'
        } finally {
            this.browseBusy = false
        }
    }

    skipEsp32(): void {
        this.markReady()
    }

    // ── cli-prompt actions ───────────────────────────────────────────────────

    async downloadAndInstall(): Promise<void> {
        await this.runInstall()
    }

    async browseForBinary(): Promise<void> {
        this.browseError = null
        this.browseBusy = true
        try {
            const filePath = await this.cli.browseBinary()
            if (!filePath) return

            const validation = await this.cli.validateBinary(filePath)
            if (!validation.success) {
                this.browseError = validation.error ?? 'The selected file is not a valid Arduino CLI binary.'
                return
            }

            await this.cli.setCustomPath(filePath)
            this.installedVersion = validation.version ?? null
            await this.checkAndSetup()
        } catch (err) {
            this.browseError = (err as Error).message
        } finally {
            this.browseBusy = false
        }
    }

    async browseForArchive(): Promise<void> {
        this.browseError = null
        this.browseBusy = true
        try {
            const filePath = await this.cli.browseBinary()
            if (!filePath) return

            this.phase = 'installing'
            this.statusMessage = 'Extracting Arduino CLI from archive...'
            this.progress = 10

            const extract = await this.cli.installFromArchive(filePath)
            if (!extract.success) throw new Error(extract.error ?? 'Extraction failed')
            this.progress = 40

            this.statusMessage = 'Initializing configuration...'
            const init = await this.cli.initConfig()
            if (!init.success) throw new Error(init.error ?? 'Config init failed')
            this.progress = 55

            this.statusMessage = 'Updating board index...'
            const upd = await this.cli.updateIndex()
            if (!upd.success) throw new Error(upd.error ?? 'Index update failed')
            this.progress = 75

            this.statusMessage = 'Installing Arduino AVR core...'
            const platform = await this.cli.installPlatform('arduino:avr', '1.8.6')
            if (!platform.success) throw new Error(platform.error ?? 'AVR platform install failed')
            this.progress = 100

            this.statusMessage = 'Arduino CLI ready!'
            await this.checkEsp32Platform()
        } catch (err) {
            this.error = (err as Error).message
            this.phase = 'error'
        } finally {
            this.browseBusy = false
        }
    }

    // ── upgrade-prompt actions ───────────────────────────────────────────────

    async upgrade(): Promise<void> {
        await this.runInstall()
    }

    async skipUpgrade(): Promise<void> {
        await this.checkEsp32Platform()
    }

    async browseForUpgradeFile(): Promise<void> {
        await this.browseForBinary()
    }

    // ── error card ───────────────────────────────────────────────────────────

    async retry(): Promise<void> {
        await this.checkAndSetup()
    }

    // ── Install / upgrade (download path) ───────────────────────────────────

    private async runInstall(): Promise<void> {
        this.phase = 'installing'
        this.error = null

        try {
            this.statusMessage = 'Downloading Arduino CLI...'
            this.progress = 5
            const dl = await this.cli.downloadCli()
            if (!dl.success) throw new Error(dl.error ?? 'Download failed')
            this.progress = 35

            this.statusMessage = 'Initializing configuration...'
            const init = await this.cli.initConfig()
            if (!init.success) throw new Error(init.error ?? 'Config init failed')
            this.progress = 50

            this.statusMessage = 'Updating board index...'
            const upd = await this.cli.updateIndex()
            if (!upd.success) throw new Error(upd.error ?? 'Index update failed')
            this.progress = 70

            this.statusMessage = 'Installing Arduino AVR core...'
            const platform = await this.cli.installPlatform('arduino:avr', '1.8.6')
            if (!platform.success) throw new Error(platform.error ?? 'AVR platform install failed')
            this.progress = 100

            this.statusMessage = 'Arduino CLI ready!'
            await this.checkEsp32Platform()
        } catch (err) {
            this.error = (err as Error).message
            this.phase = 'error'
        }
    }

    // ── Helpers ──────────────────────────────────────────────────────────────

    private markReady(): void {
        this.phase = 'ready'
        this.state.cliReady = true
        this.router.load('home')
    }

    private parseVersion(versionString: string): string {
        const match = versionString.match(/\d+\.\d+\.\d+/)
        return match ? match[0] : ''
    }
}
