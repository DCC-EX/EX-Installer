# EX-Installer — Dev Mock Mode

Mock mode lets you run the full UI wizard and workspace without a physical Arduino connected. It does everything for real — real git clones, real compilation via Arduino CLI — the **only** thing that is faked is USB device scanning.

---

## How it works

Mock behaviour lives entirely in the **IPC layer** — the UI components have no knowledge of it and behave identically in both modes.

| IPC handler | Mock mode behaviour |
|---|---|
| `arduino-cli:list-boards` | Returns `MOCK_SERIAL_PORTS` from `dev-mock.ts` mapped to board name + FQBN via VID:PID lookup |
| `usb:list` / `usb:watch` | Returns / emits `MOCK_SERIAL_PORTS` |
| Everything else | **Real** — git clone/pull/checkout, version tag listing, reading/writing files, Arduino CLI `isInstalled`, `getVersion`, `compile`, `upload`, preferences storage |

### Per-device scratch folders

Every time a device is configured through the wizard, a unique scratch folder is created under `<install-dir>/repos/_build/<timestamp-id>`. Source files (`.cpp`, `.h`, `.ino`) are copied from the cloned repo; user-editable files (`config.h`, `myAutomation.h`, etc.) are preserved across reconfigures.

Compile and upload operations always use the scratch path, never the git source repo.

---

## Default behaviour

| Command | Mock mode |
|---|---|
| `pnpm dev` | **OFF** |
| `pnpm build` (packaged) | **OFF** |

A small amber **DEV MOCK** badge is shown in the wizard header and the workspace top bar whenever mock mode is active.

---

## Controlling mock mode

Mock mode is controlled via the `--mock` command-line flag in the main process (`src/main/index.ts`):

| Launch command | Mock mode |
|---|---|
| `pnpm dev` | **OFF** |
| `pnpm dev -- --mock` | **ON** |
| `electron . --mock` | **ON** (explicit flag) |
| `./EX-Installer --mock` (packaged executable) | **ON** (explicit flag) |
| `pnpm build` (packaged) | **OFF** |

Mock mode is enabled only when `--mock` is provided.

---

## Customising the mock devices

Edit [`src/main/dev-mock.ts`](main/dev-mock.ts).

### Change which ports / boards appear

```ts
export const MOCK_SERIAL_PORTS: SerialDeviceInfo[] = [
    {
        path: 'MOCK_COM3',
        manufacturer: 'DCC-EX',
        serialNumber: 'DCCEX-MOCK-0001',
        vendorId: '2341',   // VID used for board name + FQBN lookup
        productId: '0042',  // 0042 = Mega 2560
    },
    // add more entries here
]
```

Common VID:PID values (full list in `arduino-cli-ipc.ts`):

| VID:PID | Board |
|---|---|
| `303a:1001` | EX-CSB1 (ESP32-S3) |
| `2341:0042` | Arduino Mega 2560 |
| `2341:0043` | Arduino Uno |
| `10c4:ea60` | ESP32 (CP2102) |

---

## UI differences in mock mode

- The toolbar shows a **Compile** button instead of **Compile & Upload** (upload requires a real connected device).
- The amber **DEV MOCK** badge is visible in the wizard header and workspace toolbar.

---

## File locations

```
src/
├── main/
│   ├── index.ts              ← IS_DEV_MOCK flag detection (command-line args)
│   ├── dev-mock.ts           ← MOCK_SERIAL_PORTS, mock data
│   └── ipc/
│       ├── arduino-cli-ipc.ts  ← list-boards mocked; all other CLI calls are real
│       ├── git-ipc.ts          ← all real (no mock guards)
│       └── usb-ipc.ts          ← list + watch mocked
```
