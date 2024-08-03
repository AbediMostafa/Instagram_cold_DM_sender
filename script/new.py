import random

arr = [
    1,2,3,4,5,6,7,8,9
]


def run_shuffle_events(events):
    random.shuffle(events)

    for event in events:
        print(event)

run_shuffle_events(arr)
print('==========================')
run_shuffle_events(arr)
