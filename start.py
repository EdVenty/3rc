import subprocess
import platform

system = platform.system()

if system == 'Linux':
    subprocess.Popen(['python3', '/home/pi/3rc/serve.py'])
    subprocess.run(['python3', '/home/pi/3rc/browser.py'])

elif system == 'Windows':
    subprocess.Popen(['python3', './serve.py'])
    subprocess.run(['python3', './reporter.py'])

else:
    raise SystemError("Unexpected system.")