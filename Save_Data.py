import sys
from PyQt5.QtWidgets import *
import Kiwoom
import time
from pandas import DataFrame
import datetime
import sqlite3

MARKET_KOSPI = 0
MARKET_KOSDAQ = 10
TR_REQ_TIME_INTERVAL = 1

con = sqlite3.connect("C:/Users/SGD/Dropbox (CDAL)/Python-program/Project/Kiwoom/DataBase.db")
con_sub = sqlite3.connect("C:/Users/SGD/Dropbox (CDAL)/Python-program/Project/Kiwoom/DataBase_backup.db")

GetCodeList = {
    1:0,
    2:3,
    3:4,
    4:5,
    5:6,
    6:8,
    7:9,
    8:10,
    9:30
}


class PyMon:
    def __init__(self):
        self.kiwoom = Kiwoom.Kiwoom()
        self.kiwoom.comm_connect()
        self.get_code_list()

    def run(self):
        print("Data Download is Start")

        for i in range(len(self.kospi_codes)):
            code = self.kospi_codes[i]
            today = datetime.datetime.today().strftime("%Y%m%d")
            df = self.get_ohlcv(code, today)
            names = "KRX : " + code
            df.to_sql(names, con, if_exists='replace')
            df.to_sql(names, con_sub, if_exists='replace')
            # print(df, today, code)
            if i % 10 == 9:
                print("{} is download".format(code), "({})".format(i+1))
            time.sleep(TR_REQ_TIME_INTERVAL)

        print("Data Download is Complete")

    def get_code_list(self):
        self.kospi_codes = self.kiwoom.get_code_list_by_market(MARKET_KOSPI)
        self.kosdaq_codes = self.kiwoom.get_code_list_by_market(MARKET_KOSDAQ)
        self.kospi_codes = self.kospi_codes[1280:]
        # self.kospi_codes = self.kospi_codes[:950]
        # self.kospi_codes = self.kospi_codes[1200:]
        for i in range(len(GetCodeList)):
            List = self.kiwoom.get_code_list_by_market(GetCodeList[i+1])
            aaa = "./Data_list/Market_list{}.txt".format(GetCodeList[i+1])
            f = open(aaa, 'wt')
            for j in range(len(List)):
                code = List[j]
                f.writelines("{}\n".format(code))
            f.close()
        print("LIst Update is Complete")

    def get_ohlcv(self, code, start):
        self.kiwoom.ohlcv ={'date': [], 'open': [], 'high': [], 'low': [], 'close': [], 'volume': []}
        self.kiwoom.set_input_value("종목코드", code)
        self.kiwoom.set_input_value("기준일자", start)
        self.kiwoom.set_input_value("수정주가구분", 1)
        self.kiwoom.comm_rq_data("opt10081_req", "opt10081", 0, "0101")

        while self.kiwoom.remianed_data == True:
            time.sleep(TR_REQ_TIME_INTERVAL)
            self.kiwoom.set_input_value("종목코드", code)
            self.kiwoom.set_input_value("기준일자", start)
            self.kiwoom.set_input_value("수정주가구분", 1)
            self.kiwoom.comm_rq_data("opt10081_req", "opt10081", 2, "0101")

        df = DataFrame(self.kiwoom.ohlcv, columns=['open', 'high', 'low', 'close', 'volume', 'date'], index=self.kiwoom.ohlcv['date'])
        # print(df)
        df = df.sort_values('date')
        df.index = range(df.shape[0])
        return df


if __name__=='__main__':
    app = QApplication(sys.argv)
    pymon = PyMon()
    pymon.run()









