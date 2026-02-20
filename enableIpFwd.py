import subprocess
import winreg
import ctypes
import sys

# Popup function
def popup(title, message, icon=0x40):
    ctypes.windll.user32.MessageBoxW(0, message, title, icon)

# Admin check
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )
    sys.exit()

error_msg = ""

try:
    # Configure service (ignore errors)
    subprocess.run("sc config RemoteAccess start= auto", shell=True)

    # Start service (ignore if already running)
    subprocess.run("net start RemoteAccess", shell=True)

    # Enable IP forwarding
    key_path = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, "IPEnableRouter", 0, winreg.REG_DWORD, 1)
    winreg.CloseKey(key)

    # Verify registry
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ)
    value, _ = winreg.QueryValueEx(key, "IPEnableRouter")
    winreg.CloseKey(key)

    if value == 1:
        popup("Success", "Setup Successfully Completed.")
    else:
        popup("Error", "Setup Not Completed Successfully.", 0x10)

except Exception as e:
    popup("Error", str(e), 0x10)