import { resolve } from 'aurelia'
import { IDialogController } from '@aurelia/dialog'
import { StepModel, Stepper } from '@syncfusion/ej2-navigations'
import { InstallerState } from '../models/installer-state'
import { ArduinoCliService } from '../services/arduino-cli.service'
import { UsbService } from '../services/usb.service'
import { GitService } from '../services/git.service'
import { FileService } from '../services/file.service'
import { PreferencesService } from '../services/preferences.service'
import { productDetails, extractVersionDetails } from '../models/product-details'
import type { ArduinoCliBoardInfo } from '../../../types/ipc'
import type { SavedConfiguration } from '../models/saved-configuration'
import { STARTER_TEMPLATES } from '../../../types/starter-templates'

/**
 * Known USB Vendor/Product IDs → human-readable board name.
 * Used as a fallback when Arduino CLI doesn't recognise a detected serial port.
 */
const KNOWN_BOARDS: Record<string, string> = {
    '2341:0042': 'Arduino Mega 2560',
    '2341:0010': 'Arduino Mega 2560',
    '2341:0242': 'Arduino Mega 2560 (DFU)',
    '2341:0043': 'Arduino Uno',
    '2341:0001': 'Arduino Uno',
    '2341:0243': 'Arduino Uno (DFU)',
    '2341:0058': 'Arduino Nano',
    '2341:0037': 'Arduino Nano Every',
    '1a86:7523': 'CH340 Serial (Nano/Mega clone)',
    '10c4:ea60': 'CP2102 Serial (ESP32)',
    '0403:6001': 'FTDI Serial Adapter',
    '0403:6015': 'FTDI Serial Adapter',
    '0483:374b': 'STM32 Nucleo (ST-Link)',
    '0483:3748': 'STM32 ST-Link V2',
    '303a:1001': 'EX-CSB1 (DCC-EX CommandStation Board 1)',
}

export class DeviceWizard {
    /** Injected automatically by @aurelia/dialog */
    private readonly $dialog = resolve(IDialogController)

    private readonly state = resolve(InstallerState)
    private readonly cli = resolve(ArduinoCliService)
    private readonly usb = resolve(UsbService)
    private readonly git = resolve(GitService)
    private readonly files = resolve(FileService)
    private readonly preferences = resolve(PreferencesService)

    // ── Wizard step (0–4) ────────────────────────────────────────────────────
    step = 0
    readonly STEP_LABELS: StepModel[] = [
        { label: 'Arduino CLI', iconCss: 'sf-icon-cart' },
        { label: 'Select Device', iconCss: 'sf-icon-cart' },
        { label: 'Select Product', iconCss: 'sf-icon-cart' },
        { label: 'Select Version', iconCss: 'sf-icon-cart' },
        { label: 'Confirm', iconCss: 'sf-icon-cart' },
    ];

    // ── Step 0: CLI ──────────────────────────────────────────────────────────
    cliInstalled = false
    cliVersion = ''
    cliInstalling = false
    cliProgress = 0
    cliStatus = ''
    cliError: string | null = null

    // ── Step 1: Device ───────────────────────────────────────────────────────
    boards: ArduinoCliBoardInfo[] = []
    selectedBoard: ArduinoCliBoardInfo | null = null
    scanning = false
    scanError: string | null = null

    // ── Step 2: Product ──────────────────────────────────────────────────────
    selectedProduct: string | null = null
    readonly products = Object.entries(productDetails).map(([key, val]) => ({
        key,
        name: val.productName,
        description: this.productDescription(key),
    }))

    // ── Step 3: Version ──────────────────────────────────────────────────────
    versions: string[] = []
    selectedVersion: string | null = null
    versionBusy = false
    versionStatus = ''
    versionError: string | null = null

    // ── Step 4: Confirm ──────────────────────────────────────────────────────
    deviceNickname = ''

    // ── Finishing ────────────────────────────────────────────────────────────
    finishing = false
    finishError: string | null = null

    /** True when running under `pnpm dev`. */
    readonly isMock = import.meta.env.DEV

    // ── Syncfusion Stepper ───────────────────────────────────────────────────
    stepperContainer!: HTMLElement
    private sfStepper?: Stepper

    private syncStepper(): void {
        if (this.sfStepper) this.sfStepper.activeStep = this.step
    }

    // ── Lifecycle ────────────────────────────────────────────────────────
    async binding(): Promise<void> {
        await this.checkCli()
        this.scanDevices() // background pre-scan
    }

    attached(): void {
        this.sfStepper = new Stepper({
            steps: this.STEP_LABELS,
            activeStep: this.step,
            readOnly: true
        });

        this.sfStepper.appendTo(this.stepperContainer);
        let _this = this as any;

        // TODO fix this settimeout hack
        setTimeout(function () { _this.sfStepper.refresh(); }, 250);
    }

    detaching(): void {
        this.sfStepper?.destroy()
        this.sfStepper = undefined
    }

    // ── Step 0: CLI ──────────────────────────────────────────────────────────
    async checkCli(): Promise<void> {
        try {
            this.cliInstalled = await this.cli.isInstalled()
            if (this.cliInstalled) {
                this.cliVersion = (await this.cli.getVersion()) ?? 'installed'
                this.state.cliReady = true
            }
        } catch {
            this.cliInstalled = false
        }
    }

    async installCli(): Promise<void> {
        this.cliInstalling = true
        this.cliError = null
        this.cliProgress = 5
        try {
            this.cliStatus = 'Downloading Arduino CLI...'
            const dl = await this.cli.downloadCli()
            if (!dl.success) throw new Error(dl.error ?? 'Download failed')
            this.cliProgress = 35

            this.cliStatus = 'Initializing configuration...'
            const init = await this.cli.initConfig()
            if (!init.success) throw new Error(init.error ?? 'Init failed')
            this.cliProgress = 50

            this.cliStatus = 'Updating board index...'
            const upd = await this.cli.updateIndex()
            if (!upd.success) throw new Error(upd.error ?? 'Update failed')
            this.cliProgress = 70

            this.cliStatus = 'Installing Arduino AVR core...'
            await this.cli.installPlatform('arduino:avr', '1.8.6')
            this.cliProgress = 95

            this.cliInstalled = true
            this.state.cliReady = true
            this.cliVersion = (await this.cli.getVersion()) ?? 'installed'
            this.cliStatus = 'Ready!'
            this.cliProgress = 100
        } catch (err) {
            this.cliError = (err as Error).message
        } finally {
            this.cliInstalling = false
        }
    }

    // ── Step 1: Device ───────────────────────────────────────────────────────
    async scanDevices(): Promise<void> {
        this.scanning = true
        this.scanError = null
        try {
            await this.usb.initialize()
            await this.usb.refresh()
            const serial = this.usb.serialPorts

            const cliMap = new Map<string, ArduinoCliBoardInfo>()
            if (this.cliInstalled) {
                try {
                    const cliBoards = await this.cli.listBoards()
                    for (const b of cliBoards) cliMap.set(b.port, b)
                } catch { /* fall back silently */ }
            }

            this.boards = serial.map((sp) => {
                const cliMatch = cliMap.get(sp.path)
                if (cliMatch) return { ...cliMatch, serialNumber: cliMatch.serialNumber ?? sp.serialNumber }
                const vid = sp.vendorId?.toLowerCase() ?? ''
                const pid = sp.productId?.toLowerCase() ?? ''
                const vidPid = vid && pid ? `${vid}:${pid}` : ''
                return {
                    name: KNOWN_BOARDS[vidPid] ?? sp.manufacturer ?? 'Unknown device',
                    fqbn: '',
                    port: sp.path,
                    protocol: 'serial',
                    serialNumber: sp.serialNumber,
                } satisfies ArduinoCliBoardInfo
            })
        } catch (err) {
            this.scanError = (err as Error).message
        } finally {
            this.scanning = false
        }
    }

    // ── Step 2: Product ──────────────────────────────────────────────────────
    private productDescription(key: string): string {
        const desc: Record<string, string> = {
            ex_commandstation: 'Full DCC command station for model railroads',
            ex_ioexpander: 'Expands I/O pins via I\u00b2C',
            ex_turntable: 'Controls a turntable or traverser',
        }
        return desc[key] ?? ''
    }

    isDeviceSupported(productKey: string): boolean {
        const product = productDetails[productKey]
        const board = this.selectedBoard
        if (!product || !board) return false
        if (!board.fqbn) return true // unidentified board — allow any
        return product.supportedDevices.some(
            (d) => board.fqbn.startsWith(d) || d.startsWith(board.fqbn)
        )
    }

    // ── Step 3: Version ──────────────────────────────────────────────────────
    async loadVersions(): Promise<void> {
        const product = productDetails[this.selectedProduct ?? '']
        if (!product) return
        this.versionBusy = true
        this.versionError = null
        try {
            const reposDir = await this.files.getInstallDir('repos')
            const repoFolder = product.repoName.split('/')[1]
            const repoPath = `${reposDir}/${repoFolder}`
            const repoExists = await this.files.exists(`${repoPath}/.git`)

            if (repoExists) {
                this.versionStatus = 'Pulling latest changes...'
                await this.git.pull(repoPath)
            } else {
                this.versionStatus = `Cloning ${product.productName}...`
                await this.git.clone(product.repoUrl, repoPath, product.defaultBranch)
            }

            this.versionStatus = 'Loading version list...'
            const tags = await this.git.listTags(repoPath)
            this.versions = tags.sort((a, b) => {
                const va = extractVersionDetails(a)
                const vb = extractVersionDetails(b)
                if (va.major !== vb.major) return vb.major - va.major
                if (va.minor !== vb.minor) return vb.minor - va.minor
                return vb.patch - va.patch
            })
            this.selectedVersion =
                this.versions.find((t) => extractVersionDetails(t).type === 'Prod') ??
                this.versions[0] ?? null
            this.versionStatus = ''
        } catch (err) {
            this.versionError = (err as Error).message
        } finally {
            this.versionBusy = false
        }
    }

    // ── Navigation ───────────────────────────────────────────────────────────
    get canGoNext(): boolean {
        if (this.step === 0) return this.cliInstalled
        if (this.step === 1) return this.selectedBoard !== null
        if (this.step === 2) return this.selectedProduct !== null
        if (this.step === 3) return this.selectedVersion !== null && !this.versionBusy
        if (this.step === 4) return this.deviceNickname.trim().length > 0
        return false
    }

    async goNext(): Promise<void> {
        if (!this.canGoNext) return
        if (this.step === 4) {
            await this.finish()
            return
        }
        this.step++
        this.sfStepper?.nextStep();
        if (this.step === 3) await this.loadVersions()
    }

    goBack(): void {
        if (this.step > 0) {
            this.step--
            //this.syncStepper()
            this.sfStepper?.previousStep();
        }
    }

    cancel(): void {
        this.$dialog.cancel()
    }

    // ── Finish: persist state then close dialog ───────────────────────────────
    private async finish(): Promise<void> {
        this.finishing = true
        this.finishError = null
        try {
            const product = productDetails[this.selectedProduct ?? '']
            if (!product || !this.selectedBoard || !this.selectedVersion) {
                throw new Error('Incomplete selection — cannot finish.')
            }

            // ── Paths ────────────────────────────────────────────────────────
            const reposDir = await this.files.getInstallDir('repos')
            const repoFolder = product.repoName.split('/')[1]
            const repoPath = `${reposDir}/${repoFolder}`         // git source (never cleared)
            const id = String(Date.now())
            // Arduino CLI requires the sketch directory name to match the .ino filename,
            // so nest files under _build/<id>/<repoFolder> (e.g. CommandStation-EX/).
            const scratchPath = `${reposDir}/_build/${id}/${repoFolder}`  // per-device working dir

            // ── Checkout requested version in the source repo ────────────────
            const checkout = await this.git.checkout(repoPath, this.selectedVersion)
            if (!checkout.success) throw new Error(checkout.error ?? 'Checkout failed')

            // ── Collect user-tracked file names ──────────────────────────────
            // These are config.h, myAutomation, etc. — preserved across reconfigures.
            const userFileNames = new Set<string>(product.minimumConfigFiles)
            if (product.otherConfigFilePatterns) {
                // We'll match files from the scratch dir against these patterns
                for (const p of product.otherConfigFilePatterns) {
                    // We'll evaluate per-file below
                    void p
                }
            }
            const userPatterns = (product.otherConfigFilePatterns ?? []).map(p => new RegExp(p))
            const isUserFile = (name: string) =>
                userFileNames.has(name) || userPatterns.some(re => re.test(name))

            // ── Save existing user files from previous scratchPath (if any) ──
            // Look for any previously saved config for the same product/repo
            const prevConf = this.state.savedConfigurations.find(
                c => c.product === this.selectedProduct && c.scratchPath
            )
            const savedUserFiles: Map<string, string> = new Map()
            if (prevConf?.scratchPath) {
                try {
                    const prevFiles = await this.files.listDir(prevConf.scratchPath)
                    for (const name of prevFiles) {
                        if (isUserFile(name)) {
                            const content = await this.files.readFile(`${prevConf.scratchPath}/${name}`)
                            if (content.trim()) savedUserFiles.set(name, content)
                        }
                    }
                } catch { /* previous scratch dir may not exist */ }
            }

            // ── Clear scratch dir and create fresh ───────────────────────────
            try { await this.files.deleteFiles(scratchPath) } catch { /* ignore */ }
            await this.files.mkdir(scratchPath)

            // ── Selectively copy source files from repo (no examples/templates) ──
            const allowedExts = ['.ino', '.cpp', '.h']
            const allowedSubDirs = ['src', 'libraries']
            const isSourceFile = (name: string) => {
                if (name.endsWith('.example') || name.endsWith('.template')) return false
                return allowedExts.some(ext => name.endsWith(ext))
            }
            const copySourceDir = async (srcDir: string, destDir: string) => {
                const entries = await this.files.listDir(srcDir)
                for (const entry of entries) {
                    const src = `${srcDir}/${entry}`
                    const dest = `${destDir}/${entry}`
                    if (allowedSubDirs.includes(entry)) {
                        await this.files.mkdir(dest)
                        await copySourceDir(src, dest)
                    } else if (isSourceFile(entry) && !isUserFile(entry)) {
                        await this.files.copyFiles(src, dest)
                    }
                }
            }
            await copySourceDir(repoPath, scratchPath)

            // ── Resolve user config files ────────────────────────────────────
            // Priority: 1) previously-saved user edit
            //           2) bundled starter template (curated, known-good default)
            //           3) file in source repo
            //           4) example file in source repo ("config.h.example")
            //           5) example file in source repo ("config.example.h")
            const configFiles: Array<{ name: string; content: string }> = []
            for (const fileName of product.minimumConfigFiles) {
                let content = savedUserFiles.get(fileName) ?? ''
                if (!content) {
                    // 2) bundled starter template
                    content = STARTER_TEMPLATES[repoFolder]?.[fileName] ?? ''
                }
                if (!content) {
                    const filePath = `${repoPath}/${fileName}`
                    // Repos may name the example file either "config.h.example" or
                    // "config.example.h" — probe both conventions.
                    const examplePathSuffix = `${repoPath}/${fileName}.example`
                    const dotIdx = fileName.lastIndexOf('.')
                    const examplePathInfix = dotIdx !== -1
                        ? `${repoPath}/${fileName.slice(0, dotIdx)}.example${fileName.slice(dotIdx)}`
                        : null
                    if (await this.files.exists(filePath)) {
                        content = await this.files.readFile(filePath)
                    } else if (await this.files.exists(examplePathSuffix)) {
                        content = await this.files.readFile(examplePathSuffix)
                    } else if (examplePathInfix && await this.files.exists(examplePathInfix)) {
                        content = await this.files.readFile(examplePathInfix)
                    }
                }
                configFiles.push({ name: fileName, content })
                await this.files.writeFile(`${scratchPath}/${fileName}`, content)
            }
            // Restore other tracked user files (myAutomation, etc.)
            for (const [name, content] of savedUserFiles) {
                if (!product.minimumConfigFiles.includes(name)) {
                    configFiles.push({ name, content })
                    await this.files.writeFile(`${scratchPath}/${name}`, content)
                }
            }

            // ── Update state ─────────────────────────────────────────────────
            this.state.repoPath = repoPath
            this.state.scratchPath = scratchPath
            this.state.selectedDevice = this.selectedBoard
            this.state.selectedProduct = this.selectedProduct
            this.state.selectedVersion = this.selectedVersion
            this.state.configFiles = configFiles

            // ── Persist saved configuration ──────────────────────────────────
            const savedConf: SavedConfiguration = {
                id,
                name: this.deviceNickname.trim(),
                deviceName: this.selectedBoard.name,
                devicePort: this.selectedBoard.port,
                deviceFqbn: this.selectedBoard.fqbn,
                product: this.selectedProduct!,
                productName: product.productName,
                version: this.selectedVersion,
                repoPath,
                scratchPath,
                configFiles,
                lastModified: new Date().toISOString(),
            }
            this.state.activeConfigId = id
            const existing = Array.isArray(this.state.savedConfigurations)
                ? this.state.savedConfigurations : []
            this.state.savedConfigurations = [savedConf, ...existing].slice(0, 10)
            await this.preferences.set('savedConfigurations', this.state.savedConfigurations)

            await this.$dialog.ok({ id })
        } catch (err) {
            this.finishError = (err as Error).message
        } finally {
            this.finishing = false
        }
    }
}
