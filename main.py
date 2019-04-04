import json
import threading

import requests


class ElectricityThread(threading.Thread):

    def __init__(self, data):

        threading.Thread.__init__(self)
        self.data = data
        self.electricity = {}

    def run(self):

        for room_name in self.data:
            button = True
            while button:
                button = self.post(room_name, self.data[room_name])

    def post(self, room_name, room_id):

        url = 'http://axf.nfu.edu.cn/electric/getData/getReserveAM'
        data = {'roomId': room_id}

        try:
            session = requests.session()
            response = session.post(url, data=data, timeout=1)

        except OSError:
            return True

        else:

            try:
                electric_quantity = json.loads(response.text)
                electric_quantity = electric_quantity['data']['remainPower']

            except TypeError:
                self.electricity.update({room_name: 'NULL'})
                return False

            else:

                if float(electric_quantity) < 0:
                    electric_quantity = 0

                else:

                    electric_quantity = round(float(electric_quantity), 2)
                    electric_quantity = int(float(electric_quantity) * 100)

                self.electricity.update({room_name: electric_quantity})
                return False

    def get_electricity(self):
        return self.electricity


class Electricity:
    def __init__(self):
        with open('RoomKey.json', 'r') as file:
            self.roomKey = json.load(file)
        self.electricityData = {}

    def get_electricity(self):
        for build in self.roomKey:
            data = {}
            count = 0
            thread = list(range(len(self.roomKey[build])))

            for layer in self.roomKey[build]:
                thread[count] = ElectricityThread(self.roomKey[build][layer])
                count += 1

            for i in range(len(thread)):
                thread[i].start()

            for i in range(len(thread)):
                thread[i].join()

            for i in range(len(thread)):
                data.update(thread[i].get_electricity())

            self.electricityData.update({build: data})


if __name__ == '__main__':
    electricity = Electricity()
    electricity.get_electricity()
    print(electricity.electricityData)


