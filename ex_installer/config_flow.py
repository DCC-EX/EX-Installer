"""Pure configuration-flow helpers used by the EX-Installer screens.

Keeping validation and generated lines here makes the configuration paths
testable without constructing the CustomTkinter UI or attaching hardware.
"""

import ipaddress


def validate_static_ip(parts):
    """Return a normalized IPv4 address or raise ``ValueError``."""
    if len(parts) != 4:
        raise ValueError("Static IP address must contain four octets")
    try:
        address = ipaddress.IPv4Address(".".join(str(part).strip() for part in parts))
    except (ValueError, ipaddress.AddressValueError) as exc:
        raise ValueError("Invalid static IP address") from exc
    if address.is_unspecified or address.is_multicast or address.is_reserved or address.is_loopback:
        raise ValueError("Static IP address is reserved")
    return str(address)


def ap_config_lines(ssid, password):
    """Generate AP-mode config lines, using firmware defaults when blank."""
    lines = []
    if ssid:
        if not password:
            raise ValueError("WiFi password not set for custom access point")
        lines.extend((f'#define WIFI_SSID "{ssid}"\n', "#define FORCE_AP true\n"))
    else:
        lines.append('#define WIFI_SSID "Your network name"\n')
    password_value = password or "Your network passwd"
    lines.append(f'#define WIFI_PASSWORD "{password_value}"\n')
    return lines


def csb1_track_defaults(motor_driver):
    """Return automatic TrackManager defaults for an EX-CSB1 C/D driver."""
    if not motor_driver.startswith("EXCSB1_"):
        return None
    return {"enabled": True, "C": "MAIN", "D": "MAIN"}


def should_upload(compile_only):
    """Return whether the post-compile upload phase should run."""
    return not bool(compile_only)


def post_flash_verification(output):
    """Classify serial/output evidence after flashing."""
    text = (output or "").lower()
    if any(marker in text for marker in ("error", "failed", "not found")):
        return False
    return any(marker in text for marker in ("dcc-ex", "commandstation", "ready", "welcome"))
