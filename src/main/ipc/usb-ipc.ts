import { ipcMain } from 'electron'
import type { UsbManager } from '../usb-manager'
import { IS_DEV_MOCK } from '../index'
import { MOCK_SERIAL_PORTS } from '../dev-mock'

/**
 * IPC handlers for USB / serial-port operations.
 *
 * Renderer sends requests on these channels and awaits the reply:
 *
 *  usb:list-serial-ports   → SerialDeviceInfo[]
 *  usb:list-usb-devices    → UsbDeviceInfo[]
 *  usb:open-port           → void   (throws on failure)
 *  usb:write-to-port       → void
 *  usb:close-port          → void
 *
 * Main → Renderer push events (no reply expected):
 *  usb:data      { path, data }
 *  usb:error     { path, message }
 *  usb:closed    { path }
 *  usb:attached  { vendorId, productId }
 *  usb:detached  { vendorId, productId }
 */
export function registerUsbIpcHandlers(usbManager: UsbManager): void {
    ipcMain.handle('usb:list-serial-ports', async () => {
        if (IS_DEV_MOCK) return MOCK_SERIAL_PORTS
        return usbManager.listSerialPorts()
    })

    ipcMain.handle('usb:list-usb-devices', () => {
        if (IS_DEV_MOCK) return []
        return usbManager.listUsbDevices()
    })

    ipcMain.handle(
        'usb:open-port',
        async (_event, path: string, baudRate?: number) => {
            await usbManager.openPort(path, baudRate)
        },
    )

    ipcMain.handle(
        'usb:write-to-port',
        async (_event, path: string, data: string) => {
            await usbManager.writeToPort(path, data)
        },
    )

    ipcMain.handle('usb:close-port', async (_event, path: string) => {
        await usbManager.closePort(path)
    })
}
