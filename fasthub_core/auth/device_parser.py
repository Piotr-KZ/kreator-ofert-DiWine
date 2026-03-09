"""
Parsowanie User-Agent na czytelne informacje o urządzeniu.
"""


def parse_device(user_agent_string: str) -> dict:
    """
    Parsuj User-Agent na czytelne dane.

    Returns:
        {"device_type", "device_name", "browser", "os"}
    """
    try:
        from user_agents import parse

        ua = parse(user_agent_string or "")

        if ua.is_mobile:
            device_type = "mobile"
        elif ua.is_tablet:
            device_type = "tablet"
        else:
            device_type = "desktop"

        browser = f"{ua.browser.family}"
        if ua.browser.version_string:
            browser += f" {ua.browser.version_string.split('.')[0]}"

        os_name = f"{ua.os.family}"
        if ua.os.version_string:
            os_name += f" {ua.os.version_string}"

        device_name = f"{browser} na {os_name}"

        return {
            "device_type": device_type,
            "device_name": device_name,
            "browser": browser,
            "os": os_name,
        }
    except Exception:
        return {
            "device_type": "desktop",
            "device_name": "Unknown",
            "browser": "Unknown",
            "os": "Unknown",
        }
