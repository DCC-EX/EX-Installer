import { app } from 'electron'
import { join, basename } from 'path'
import { existsSync, mkdirSync, createWriteStream, chmodSync, unlinkSync } from 'fs'
import { readdir, rm, mkdtemp, cp } from 'fs/promises'
import { tmpdir } from 'os'
import { execFile, spawn } from 'child_process'
import { get as httpsGet } from 'https'
import { extract as tarExtract } from 'tar'

const ARDUINO_CLI_VERSION = '0.35.3'

function getPlatformDownloadUrl(): string {
    const platform = process.platform
    const arch = process.arch === 'x64' ? '64bit' : 'ARM64'

    if (platform === 'win32') {
        return `https://github.com/arduino/arduino-cli/releases/download/v${ARDUINO_CLI_VERSION}/arduino-cli_${ARDUINO_CLI_VERSION}_Windows_64bit.zip`
    } else if (platform === 'darwin') {
        const macArch = process.arch === 'arm64' ? 'ARM64' : '64bit'
        return `https://github.com/arduino/arduino-cli/releases/download/v${ARDUINO_CLI_VERSION}/arduino-cli_${ARDUINO_CLI_VERSION}_macOS_${macArch}.tar.gz`
    } else {
        return `https://github.com/arduino/arduino-cli/releases/download/v${ARDUINO_CLI_VERSION}/arduino-cli_${ARDUINO_CLI_VERSION}_Linux_${arch}.tar.gz`
    }
}

export class ArduinoCliService {
    private progressCallback?: (phase: string, message: string) => void
    private customBinaryPath: string | null = null

    get installDir(): string {
        const base = join(app.getPath('home'), 'ex-installer', 'arduino-cli')
        if (!existsSync(base)) mkdirSync(base, { recursive: true })
        return base
    }

    get cliBinaryPath(): string {
        if (this.customBinaryPath) return this.customBinaryPath
        const name = process.platform === 'win32' ? 'arduino-cli.exe' : 'arduino-cli'
        return join(this.installDir, name)
    }

    setCustomBinaryPath(path: string): void {
        this.customBinaryPath = path
    }

    setProgressCallback(cb: (phase: string, message: string) => void): void {
        this.progressCallback = cb
    }

    private emitProgress(phase: string, message: string): void {
        this.progressCallback?.(phase, message)
    }

    isInstalled(): boolean {
        return existsSync(this.cliBinaryPath)
    }

    getBundledVersion(): string {
        return ARDUINO_CLI_VERSION
    }

    async validateBinary(binaryPath: string): Promise<{ success: boolean; version?: string; error?: string }> {
        return new Promise((resolve) => {
            execFile(binaryPath, ['version', '--format', 'json'], { timeout: 10000 }, (err, stdout) => {
                if (err) return resolve({ success: false, error: 'Not a valid Arduino CLI binary' })
                try {
                    const data = JSON.parse(stdout)
                    const version = (data.VersionString ?? data.version ?? stdout.trim()) as string
                    resolve({ success: true, version })
                } catch {
                    resolve({ success: false, error: 'Could not parse version output' })
                }
            })
        })
    }

    async installFromArchive(archivePath: string): Promise<{ success: boolean; error?: string }> {
        try {
            this.emitProgress('extract', 'Extracting Arduino CLI...')
            if (archivePath.endsWith('.zip')) {
                await this.extractZipTo(archivePath, this.installDir)
            } else {
                await this.extractTarGzTo(archivePath, this.installDir)
            }
            if (process.platform !== 'win32') chmodSync(this.cliBinaryPath, 0o755)
            this.emitProgress('extract', 'Arduino CLI extracted successfully')
            return { success: true }
        } catch (err) {
            return { success: false, error: (err as Error).message }
        }
    }

    async checkPlatformInstalled(platformId: string): Promise<{ installed: boolean; version: string | null }> {
        const platforms = await this.getPlatforms()
        const found = platforms.find((p) => p.id === platformId || p.id.startsWith(platformId))
        if (found?.installed) return { installed: true, version: found.installed }
        return { installed: false, version: null }
    }

    getArduinoDataDir(): string {
        const home = app.getPath('home')
        if (process.platform === 'win32') {
            return join(process.env['LOCALAPPDATA'] ?? home, 'Arduino15')
        } else if (process.platform === 'darwin') {
            return join(home, 'Library', 'Arduino15')
        } else {
            return join(home, '.arduino15')
        }
    }

    async installPlatformFromArchive(
        archivePath: string,
        platformId: string,
        version: string,
    ): Promise<{ success: boolean; error?: string }> {
        let tempDir: string | null = null
        try {
            tempDir = await mkdtemp(join(tmpdir(), 'ez-platform-'))
            this.emitProgress('extract', 'Extracting platform archive...')
            if (archivePath.endsWith('.zip')) {
                await this.extractZipTo(archivePath, tempDir)
            } else {
                await this.extractTarGzTo(archivePath, tempDir)
            }
            const entries = await readdir(tempDir)
            const srcDir = entries.length === 1 ? join(tempDir, entries[0]) : tempDir
            const parts = platformId.split(':')
            const vendor = parts[0]
            const arch = parts[1] ?? parts[0]
            const destDir = join(this.getArduinoDataDir(), 'packages', vendor, 'hardware', arch, version)
            if (!existsSync(destDir)) mkdirSync(destDir, { recursive: true })
            this.emitProgress('extract', 'Copying platform files...')
            await cp(srcDir, destDir, { recursive: true })
            return { success: true }
        } catch (err) {
            return { success: false, error: (err as Error).message }
        } finally {
            if (tempDir) await rm(tempDir, { recursive: true, force: true }).catch(() => { })
        }
    }

    async getVersion(): Promise<string | null> {
        if (!this.isInstalled()) return null
        return new Promise((resolve) => {
            execFile(this.cliBinaryPath, ['version', '--format', 'json'], { timeout: 10000 }, (err, stdout) => {
                if (err) return resolve(null)
                try {
                    const data = JSON.parse(stdout)
                    resolve(data.VersionString ?? data.version ?? stdout.trim())
                } catch {
                    resolve(stdout.trim())
                }
            })
        })
    }

    async downloadCli(): Promise<{ success: boolean; error?: string }> {
        try {
            this.emitProgress('download', 'Downloading Arduino CLI...')
            const url = getPlatformDownloadUrl()
            const destFile = join(this.installDir, basename(url))

            await this.downloadFile(url, destFile)
            this.emitProgress('extract', 'Extracting Arduino CLI...')

            if (destFile.endsWith('.zip')) {
                await this.extractZipTo(destFile, this.installDir)
            } else {
                await this.extractTarGzTo(destFile, this.installDir)
            }

            // Make executable on Unix
            if (process.platform !== 'win32') {
                chmodSync(this.cliBinaryPath, 0o755)
            }

            // Clean up archive
            try { unlinkSync(destFile) } catch { /* ignore */ }

            this.emitProgress('download', 'Arduino CLI installed successfully')
            return { success: true }
        } catch (err) {
            return { success: false, error: (err as Error).message }
        }
    }

    async initConfig(): Promise<{ success: boolean; error?: string }> {
        return this.runCli(['config', 'init', '--overwrite',
            '--additional-urls',
            'https://espressif.github.io/arduino-esp32/package_esp32_index.json,https://github.com/stm32duino/BoardManagerFiles/raw/main/package_stmicroelectronics_index.json'
        ])
    }

    async updateIndex(): Promise<{ success: boolean; error?: string }> {
        this.emitProgress('update', 'Updating board index...')
        return this.runCli(['core', 'update-index'])
    }

    async installPlatform(platform: string, version?: string): Promise<{ success: boolean; error?: string }> {
        const arg = version ? `${platform}@${version}` : platform
        this.emitProgress('install', `Installing platform ${arg}...`)
        return this.runCli(['core', 'install', arg])
    }

    async installLibrary(library: string, version?: string): Promise<{ success: boolean; error?: string }> {
        const arg = version ? `${library}@${version}` : library
        this.emitProgress('install', `Installing library ${arg}...`)
        return this.runCli(['lib', 'install', arg])
    }

    async getPlatforms(): Promise<Array<{ id: string; installed: string; latest: string; name: string }>> {
        const result = await this.runCliJson(['core', 'list', '--format', 'json'])
        if (!result) return []
        const platforms = Array.isArray(result) ? result : (result.platforms ?? [])
        return platforms.map((p: Record<string, unknown>) => ({
            id: (p.id ?? p.ID ?? '') as string,
            installed: (p.installed ?? p.Installed ?? '') as string,
            latest: (p.latest ?? p.Latest ?? '') as string,
            name: (p.name ?? p.Name ?? '') as string,
        }))
    }

    async getLibraries(): Promise<Array<{ name: string; installedVersion: string; availableVersion?: string }>> {
        const result = await this.runCliJson(['lib', 'list', '--format', 'json'])
        if (!result) return []
        const libs = Array.isArray(result) ? result : (result.installed_libraries ?? [])
        return libs.map((entry: Record<string, unknown>) => {
            const lib = (entry.library ?? entry) as Record<string, unknown>
            return {
                name: (lib.name ?? lib.Name ?? '') as string,
                installedVersion: (lib.version ?? lib.installed_version ?? '') as string,
            }
        })
    }

    async listBoards(): Promise<Array<{ name: string; fqbn: string; port: string; protocol: string; serialNumber?: string }>> {
        const result = await this.runCliJson(['board', 'list', '--format', 'json'])
        if (!result) return []
        const ports = Array.isArray(result) ? result : (result.detected_ports ?? [])
        const boards: Array<{ name: string; fqbn: string; port: string; protocol: string; serialNumber?: string }> = []

        for (const entry of ports) {
            const port = (entry.port ?? {}) as Record<string, unknown>
            const matchingBoards = (entry.matching_boards ?? []) as Array<Record<string, unknown>>
            const portPath = (port.address ?? port.label ?? '') as string
            const protocol = (port.protocol ?? '') as string
            const serialNumber = (port.serial_number ?? undefined) as string | undefined

            if (matchingBoards.length > 0) {
                for (const board of matchingBoards) {
                    boards.push({
                        name: (board.name ?? 'Unknown') as string,
                        fqbn: (board.fqbn ?? '') as string,
                        port: portPath,
                        protocol,
                        serialNumber,
                    })
                }
            } else if (portPath) {
                boards.push({ name: 'Unknown', fqbn: '', port: portPath, protocol, serialNumber })
            }
        }
        return boards
    }

    async compile(sketchPath: string, fqbn: string): Promise<{ success: boolean; output: string; error?: string }> {
        this.emitProgress('compile', `Compiling for ${fqbn}...`)
        return new Promise((resolve) => {
            const child = spawn(this.cliBinaryPath, ['compile', '--fqbn', fqbn, sketchPath, '--format', 'json'], {
                timeout: 300000,
            })
            let stdout = ''
            let stderr = ''
            child.stdout.on('data', (d: Buffer) => {
                stdout += d.toString()
                this.emitProgress('compile', d.toString().trim())
            })
            child.stderr.on('data', (d: Buffer) => { stderr += d.toString() })
            child.on('close', (code) => {
                resolve({
                    success: code === 0,
                    output: stdout,
                    error: code !== 0 ? stderr || stdout : undefined,
                })
            })
            child.on('error', (err) => {
                resolve({ success: false, output: '', error: err.message })
            })
        })
    }

    async upload(sketchPath: string, fqbn: string, port: string): Promise<{ success: boolean; output: string; error?: string }> {
        this.emitProgress('upload', `Uploading to ${port}...`)
        return new Promise((resolve) => {
            const child = spawn(this.cliBinaryPath, ['upload', '-p', port, '--fqbn', fqbn, sketchPath, '--format', 'json'], {
                timeout: 300000,
            })
            let stdout = ''
            let stderr = ''
            child.stdout.on('data', (d: Buffer) => {
                stdout += d.toString()
                this.emitProgress('upload', d.toString().trim())
            })
            child.stderr.on('data', (d: Buffer) => { stderr += d.toString() })
            child.on('close', (code) => {
                resolve({
                    success: code === 0,
                    output: stdout,
                    error: code !== 0 ? stderr || stdout : undefined,
                })
            })
            child.on('error', (err) => {
                resolve({ success: false, output: '', error: err.message })
            })
        })
    }

    // ── Private helpers ──────────────────────────────────────────────────────

    private runCli(args: string[]): Promise<{ success: boolean; error?: string }> {
        return new Promise((resolve) => {
            execFile(this.cliBinaryPath, args, { timeout: 300000 }, (err, _stdout, stderr) => {
                if (err) return resolve({ success: false, error: stderr || err.message })
                resolve({ success: true })
            })
        })
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    private runCliJson(args: string[]): Promise<any> {
        return new Promise((resolve) => {
            execFile(this.cliBinaryPath, args, { timeout: 30000, maxBuffer: 10 * 1024 * 1024 }, (err, stdout) => {
                if (err) return resolve(null)
                try {
                    resolve(JSON.parse(stdout))
                } catch {
                    resolve(null)
                }
            })
        })
    }

    private downloadFile(url: string, dest: string): Promise<void> {
        return new Promise((resolve, reject) => {
            const follow = (currentUrl: string) => {
                httpsGet(currentUrl, (res) => {
                    if (res.statusCode && res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
                        follow(res.headers.location)
                        return
                    }
                    if (res.statusCode !== 200) {
                        reject(new Error(`Download failed: HTTP ${res.statusCode}`))
                        return
                    }
                    const file = createWriteStream(dest)
                    res.pipe(file)
                    file.on('finish', () => { file.close(); resolve() })
                    file.on('error', reject)
                }).on('error', reject)
            }
            follow(url)
        })
    }

    private async extractTarGzTo(archivePath: string, cwd: string): Promise<void> {
        await tarExtract({ file: archivePath, cwd })
    }

    private extractZipTo(archivePath: string, cwd: string): Promise<void> {
        return new Promise((resolve, reject) => {
            const { execFile: exec } = require('child_process')
            if (process.platform === 'win32') {
                exec('powershell', ['-Command', `Expand-Archive -Path '${archivePath}' -DestinationPath '${cwd}' -Force`],
                    (err: Error | null) => err ? reject(err) : resolve())
            } else {
                exec('unzip', ['-o', archivePath, '-d', cwd],
                    (err: Error | null) => err ? reject(err) : resolve())
            }
        })
    }
}
