from datetime import date, datetime
from json import load
from json.decoder import JSONDecodeError
from os import getenv
from traceback import format_exc

from dotenv import load_dotenv
from mysql.connector import connect
from requests import post

load_dotenv(f"{getenv('BASE')}/.env")
with open(f"{getenv('BASE')}/room_id.json", "r") as file:
    room_ids = load(file)


class ElectricityFee:
    def __init__(self):
        self.log = open(f"{getenv('BASE')}/log", "a")
        self.log.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S 开始爬取数据"))

        self.db = connect(host="localhost", user=getenv("MYSQL_USER"), passwd=getenv("MYSQL_PASSWORD"), database="nfu")
        self.cursor = self.db.cursor()

    def __del__(self):
        self.db.close()
        self.log.write(datetime.now().strftime(" -> %H:%M:%S 结束运行\n"))
        self.log.close()

    def __get_electric(self, room_id: int, retry: int = 0) -> float:
        """
        爬取电费
        :param room_id:
        :param retry:
        :return:
        """
        url = 'http://nfu.zhihuianxin.net/electric/getData/getReserveAM'
        data = dict(roomId=room_id)
        try:
            response = post(url, data=data, timeout=1)
            electric = float(response.json()["data"]["remainPower"])
        except (OSError, TypeError, JSONDecodeError, KeyError):
            if retry > 2: return -1
            else: return self.__get_electric(room_id, retry + 1)
        else:
            if electric < 0: electric = 0
            return electric

    def __insert_mysql(self, room_id, electric):
        """
        电费插入MySQL
        :param room_id:
        :param electric:
        :return:
        """
        sql = "insert into electric (room_id, value, date) VALUES (%s, %s, %s);"
        val = (room_id, electric, date.today().strftime("%Y-%m-%d"))
        self.cursor.execute(sql, val)
        self.db.commit()

    def run(self):
        """
        运行脚本
        :return:
        """
        for room_id in room_ids:
            try:
                electric = self.__get_electric(room_id)
                if electric != -1: self.__insert_mysql(room_id, electric)
            except:
                with open(f"{getenv('BASE')}/err.log", "a") as f:
                    f.write(datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
                    f.write(f"\n{format_exc()}")
                    f.write("\n")


if __name__ == "__main__":
    ElectricityFee().run()
