import { ipcMain } from 'electron'
import { IS_DEV_MOCK } from '../index'

export function registerConfigIpcHandlers(): void {
    ipcMain.handle('config:get-mock', () => {
        return IS_DEV_MOCK
    })
}
