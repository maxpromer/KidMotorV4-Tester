from ampy.files import Files
from ampy.pyboard import Pyboard
import psutil
import shutil
from time import sleep
import serial.tools.list_ports as ports

MICROPYTHON_FILE = "./MicroPython.for.KidMotorV4.V1.9.0-dirty.uf2"
SCRIPT_FILE = "main.py"
FILE_IN_DRIVE = "/" + SCRIPT_FILE

drps = psutil.disk_partitions()
drives = [dp.device for dp in drps if dp.fstype == 'FAT']
if len(drives) <= 0:
    print("ERROR: Not found KidMotorV4 drive. Press BOOT and then reconnect USB")
    exit()
KidMotorDrive = drives[0]
print("Found KidMotor at {}".format(KidMotorDrive))
print("Install MicroPython ....")
shutil.copyfile(MICROPYTHON_FILE, KidMotorDrive + "micropython.uf2")
print("install finish")
print("wait COM port present")

comport = None
error = 0
while comport == None:
    sleep(1)
    comlist = ports.comports()
    for element in comlist:
        comport = element.device
    if not comport:
        error = error + 1
        if error > 10:
            print("ERROR: COM port not present")
            exit()

print("Found {}, upload test script".format(comport))
f = open(SCRIPT_FILE, "r")
code = f.read()
pyboard = Pyboard(comport, 115200)
board_files = Files(pyboard)
board_files.put(FILE_IN_DRIVE, code)
print("upload finish, Check file ...")
found = False
for f in board_files.ls():
    if f.find(FILE_IN_DRIVE) != -1:
        found = True
        break
if not found:
    print("ERROR: check file fail !!!!")
    exit()
print("check file OK")
pyboard.serial.write(b'\x04') # ctrl-D: soft reset
print("RUN test script.")
exit()
