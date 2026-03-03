import { DI } from 'aurelia'

export const IConfigService = DI.createInterface<ConfigService>('IConfigService')

/** Wraps window.config (contextBridge API) for the renderer. */
export class ConfigService {
    private _isMock = false
    readonly ready: Promise<void>

    constructor() {
        this.ready = window.config.getMock().then((value) => {
            this._isMock = value
        })
    }

    get isMock(): boolean {
        return this._isMock
    }
}
