from subprocess import Popen, PIPE
import signal
import os

f = open('state.txt','r')
pid = int(f.read())
f.close()
f =open('state.txt','w')
if pid==0:
    print("Starting Carla")
    process = Popen(['~/Downloads/CARLA_0.9.5/CarlaUE4.sh', '-ResX=8','ResY=8'], stdout=PIPE, stderr=PIPE)
    f.write(str(process.pid))
else:
    print("Kill Carla")
    os.kill(pid,signal.SIGTERM)
    print("Starting Carla")
    process = Popen(['~/Downloads/CARLA_0.9.5/CarlaUE4.sh', '-ResX=8','ResY=8'], stdout=PIPE, stderr=PIPE)
    f.write(process.pid)

f.close()

# print(process)