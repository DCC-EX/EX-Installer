import { mkdir, writeFile } from 'fs/promises'
import { join } from 'path'
import type { SerialDeviceInfo } from '../types/ipc'
import { STARTER_TEMPLATES } from '../types/starter-templates'

export const MOCK_SERIAL_PORTS: SerialDeviceInfo[] = [
    {
        // EX-CSB1 — ESP32-S3 with native USB (Espressif VID)
        path: '/dev/ttyACM0',
        manufacturer: 'DCC-EX',
        serialNumber: 'DCCEX-CSB1-0001',
        vendorId: '303a',
        productId: '1001',
    },
    {
        // Arduino Mega 2560
        path: '/dev/ttyACM1',
        manufacturer: 'Arduino (www.arduino.cc)',
        serialNumber: 'DEV-MEGA-0001',
        vendorId: '2341',
        productId: '0042',
    },
    {
        // Arduino Uno
        path: '/dev/ttyACM2',
        manufacturer: 'Arduino (www.arduino.cc)',
        serialNumber: 'DEV-UNO-0001',
        vendorId: '2341',
        productId: '0043',
    },
    {
        // Arduino Nano
        path: '/dev/ttyUSB0',
        manufacturer: 'Arduino (www.arduino.cc)',
        serialNumber: 'DEV-NANO-0001',
        vendorId: '2341',
        productId: '0058',
    },
    {
        // Arduino Nano Every
        path: '/dev/ttyACM3',
        manufacturer: 'Arduino (www.arduino.cc)',
        serialNumber: 'DEV-NANO-EVERY-0001',
        vendorId: '2341',
        productId: '0037',
    },
    {
        // ESP32 via CP2102 USB-UART bridge
        path: '/dev/ttyUSB1',
        manufacturer: 'Silicon Labs',
        serialNumber: 'DEV-ESP32-0001',
        vendorId: '10c4',
        productId: 'ea60',
    },
    {
        // Generic CH340 clone (Nano/Mega)
        path: '/dev/ttyUSB2',
        manufacturer: 'QinHeng Electronics',
        serialNumber: undefined,
        vendorId: '1a86',
        productId: '7523',
    },
    {
        // FTDI USB-Serial adapter
        path: '/dev/ttyUSB3',
        manufacturer: 'FTDI',
        serialNumber: 'DEV-FTDI-0001',
        vendorId: '0403',
        productId: '6001',
    },
]

export const MOCK_VERSIONS = [
    'v5.4.0-Prod',
    'v5.3.2-Prod',
    'v5.3.0-Prod',
    'v5.2.0-Prod',
    'v5.4.1-Devel',
    'v5.3.3-Devel',
]

export const MOCK_SKETCH_SEEDS: Record<string, { sketchFile: string; content: string }> = {
    // repoFolder → sketch
    'CommandStation-EX': {
        sketchFile: 'CommandStation-EX.ino',
        content: [
            '// CommandStation-EX.ino — minimal mock sketch for dev compilation',
            '#include "config.h"',
            '',
            'void setup() {}',
            'void loop() {}',
        ].join('\n') + '\n',
    },
    'EX-IOExpander': {
        sketchFile: 'EX-IOExpander.ino',
        content: [
            '// EX-IOExpander.ino — minimal mock sketch for dev compilation',
            '#include "myConfig.h"',
            '',
            'void setup() {}',
            'void loop() {}',
        ].join('\n') + '\n',
    },
    'EX-Turntable': {
        sketchFile: 'EX-Turntable.ino',
        content: [
            '// EX-Turntable.ino — minimal mock sketch for dev compilation',
            '#include "config.h"',
            '',
            'void setup() {}',
            'void loop() {}',
        ].join('\n') + '\n',
    },
}

/**
 * Default config file content seeded into the mock sketch directory.
 * Sourced from STARTER_TEMPLATES — the canonical definition lives in
 * src/types/starter-templates.ts and is also used by the renderer as a
 * last-resort fallback when no config file is found on disk or in the repo.
 */
export const MOCK_CONFIG_SEEDS = STARTER_TEMPLATES

/**
 * Seeds the mock repo directory on disk so arduino-cli has a real sketch tree.
 * Called by the git:clone IPC handler when IS_DEV_MOCK is true.
 */
export async function seedMockRepo(dest: string): Promise<void> {
    await mkdir(dest, { recursive: true })
    const folderName = dest.split('/').pop() ?? ''
    const sketchSeed = MOCK_SKETCH_SEEDS[folderName]
    const configSeed = MOCK_CONFIG_SEEDS[folderName]
    if (sketchSeed) {
        await writeFile(join(dest, sketchSeed.sketchFile), sketchSeed.content, 'utf-8')
    }
    if (configSeed) {
        for (const [filename, content] of Object.entries(configSeed)) {
            await writeFile(join(dest, filename), content, 'utf-8')
        }
    }
}
