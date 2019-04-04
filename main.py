import json


class Electricity:

    def __init__(self):
        with open('RoomKey.json', 'r') as file:
            self.data = json.load(file)
