# throttle = [0 , 0.3,0.7 ,-0.3]
# steer = [-0.5,0,0,5]
# brake =[0,0.5]


class State:

    def __init__(self, throttle, steer, brake):
        self.throttle = throttle
        self.steer = steer
        self.brake = brake

    def __str__(self):
        return f'throttle: {self.throttle}, steer: {self.steer}, brake: {self.brake}'

def generator():
    throttle = [0, 0.3, 0.7, -0.3]
    steer = [-0.5, 0, 0.5]
    brake =[0, 0.5]

    states = []
    for i in throttle:
        if i == 0:
            states.append(State(0,0,brake[1]))
            continue
        for j in steer:
            states.append(State(i,j,brake[0]))
    return states

s = generator()
for i in s:
    print(i)
    







