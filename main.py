import json
import threading
import time

import pymysql
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
                    electric_quantity = '0'
                else:
                    electric_quantity = round(float(electric_quantity), 2)
                    electric_quantity = str(int(float(electric_quantity) * 100))
                self.electricity.update({room_name: electric_quantity})
                return False

    def get_electricity(self):
        return self.electricity


class Electricity:
    def __init__(self):
        with open('RoomKey.json', 'r') as file:
            self.roomKey = json.load(file)
        with open('DataSQL.json', 'r') as file:
            self.config = json.load(file)
        self.electricityData = {}
        self.log = open('log', 'a')
        self.server_time = time.strftime('%y%m%d', time.localtime(time.time()))
        self.log.write(time.strftime('%c 开始爬取数据', time.localtime(time.time())))
        # noinspection PyBroadException
        try:
            self.conn = pymysql.connect(**self.config)
            self.cursor = self.conn.cursor()
        except:
            self.log.write(time.strftime(' -> %X 数据库连接失败', time.localtime(time.time())))

    def __del__(self):
        # noinspection PyBroadException
        try:
            self.conn.close()
        except:
            self.log.write(time.strftime(' -> %X 数据库异常', time.localtime(time.time())))
        finally:
            self.log.write(time.strftime(' -> %X 结束运行\n', time.localtime(time.time())))
            self.log.close()

    def input_file(self):
        self.log.write(time.strftime(' -> %X 开始写入文件缓存', time.localtime(time.time())))
        for build in self.electricityData:
            data = {
                'version': self.server_time,
                'building': build,
                'data': self.electricityData[build]
            }
            with open('data/' + build, 'w') as file:
                json.dump(data, file)

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

    def create_data_tables(self):
        for build in self.roomKey:
            sql = 'CREATE TABLE IF NOT EXISTS ' + build + ' ( `date` INT NULL '
            for layer in self.roomKey[build]:
                for room in self.roomKey[build][layer]:
                    sql += (', `' + room + '` INT NULL ')
            sql += ') ENGINE = InnoDB DEFAULT CHARSET = utf8;'
            self.cursor.execute(sql)

    def insert_data_tables(self):
        self.log.write(time.strftime(' -> %X 开始写入数据库', time.localtime(time.time())))
        for build in self.electricityData:
            sql = 'INSERT INTO ' + build + ' ( date'
            for room in self.electricityData[build]:
                sql += ', ' + room
            sql += ') VALUES (' + self.server_time
            for room in self.electricityData[build]:
                if self.electricityData[build][room] != 'NULL':
                    sql += ', ' + self.electricityData[build][room]
                else:
                    sql += ', ' + self.electricityData[build][room]
            sql += ');'
            # noinspection PyBroadException
            try:
                self.cursor.execute(sql)
                self.conn.commit()
            except:
                self.conn.rollback()
                self.log.write(time.strftime(' -> %X "' + build + '"数据表插入错误', time.localtime(time.time())))


if __name__ == '__main__':
    electricity = Electricity()
    electricity.get_electricity()
    electricity.insert_data_tables()
    electricity.input_file()
