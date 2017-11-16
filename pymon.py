import sys
from PyQt5.QtWidgets import *
import Kiwoom
import time
from pandas import DataFrame
import datetime
import webreader
import numpy as np

MARKET_KOSPI = 0
MARKET_KOSDAQ = 10

class PyMon:
    def __init__(self):
        self.kiwoom = Kiwoom.Kiwoom()
        self.kiwoom.comm_connect()         #여기에서 접속을 하고
        self.get_code_list()

    def run(self):
        print(len(self.kospi_codes))
        buy_list = []
        num = len(self.kosdaq_codes)

        for i, code in enumerate(self.kosdaq_codes):
            print(i, '/', num)
            if self.check_speedy_rising_volume(code):
                print("급등주: ", code)
                buy_list.append(code)

        self.update_buy_list(buy_list)  #여기에서 메서드를 호출하므로 run을 실행하면 추가하고 바로 넣어준다.

        # df = self.get_ohlcv("039490", "20170321")
        # print(df)


    def get_code_list(self):
        self.kospi_codes = self.kiwoom.get_code_list_by_market(MARKET_KOSPI)  #여기에서 get_code_list_by_market이라는 method를 호출해서 가지고 오게 된다.
        self.kosdaq_codes = self.kiwoom.get_code_list_by_market(MARKET_KOSDAQ)

    def get_ohlcv(self, code, start):  #여기에서 data를 받아오게 된다.  code와 start가 종목코드와 기준일자를 세팅을 하게 된다.
        self.kiwoom.ohlcv ={'date': [], 'open': [], 'high': [], 'low': [], 'close': [], 'volume': []}

        self.kiwoom.set_input_value("종목코드", code)
        self.kiwoom.set_input_value("기준일자", start)
        self.kiwoom.set_input_value("수정주가구분", 1)
        self.kiwoom.comm_rq_data("opt10081_req", "opt10081", 0, "0101")  #opt10081_req에서 data set을 받게 된다. 이때의 세팅은 그러므로 Kiwoom.py에서 세팅해야된다.
        time.sleep(0.2)

        df = DataFrame(self.kiwoom.ohlcv, columns=['open', 'high', 'low', 'close', 'volume'], index=self.kiwoom.ohlcv['date'])
        # print(df)

        return df

    def check_speedy_rising_volume(self, code):  #급증주식을 포착하는 알고리즘이다.
        today = datetime.datetime.today().strftime("%Y%m%d")  #여기에서 오늘의 날짜를 20170321 과 같은 포맷으로 받아오게 된다.
        df = self.get_ohlcv(code, today)   #오늘 기준으로 특정 code값의 값을 가지고 오게 된다.
        volumes = df['volume']  #그중에서 거래량인 volume값만을 가지게 된다.

        if len(volumes) < 21:  #그 기간이 21일을 지내지 않은 신생주식에 대해서는 바로 False 처리를 합니다.
            return False

        sum_vol20 = 0
        today_vol = 0

        for i, vol in enumerate(volumes):
            if i == 0:
                today_vol = vol  #오늘치는 today_vol에 넣고 이전의 vol값은 sum_vol20에 넣는다.
            elif 1 <=i <= 20:
                sum_vol20 += vol
            else:
                break
        avg_vol20 = sum_vol20 / 20  #그것을 20으로 나눠서 평균 vol을 넣고
        if today_vol>avg_vol20 * 10: #평균값보다 10배 이상 거래량이 초과할시에 true를 계산시킨다.
            return True

    def update_buy_list(self, buy_list):  #구입하려는 but_list를 메모장에 넘기는 메서드
        f = open("buy_list.txt", 'wt')
        for code in buy_list:
            f.writelines("매수;%s;시장가;10;0;매수전\n" % (code))
        f.close()

    def calculate_estimated_dividend_to_treasury(self, code):
        estimated_dividend_yield = webreader.get_estimated_dividend_yield(code)   #여기에서 현재의 estimate한 yield값을 추출하고
        if np.isnan(estimated_dividend_yield):
            estimated_dividend_yield = webreader.get_dividend_yield(code)

        current_3year_treasury = webreader.get_current_3year_treasury()     #3year_treasure를 추출한다.
        estimated_dividend_to_treasury = float(estimated_dividend_yield) / float(current_3year_treasury)  #2개를 나눠서 return한다.
        return estimated_dividend_to_treasury

    def get_min_max_dividend_to_treasury(self, code):   #여기에서 5년치 min_max값을 구한다.
        previous_dividend_yield = webreader.get_previous_dividend_yield(code)
        three_years_treasury = webreader.get_3year_treasury()
        now = datetime.datetime.now()
        cur_year = now.year
        previous_dividend_to_treasury = {}

        for year in range(cur_year - 5, cur_year):
            if year in previous_dividend_yield.keys() and year in three_years_treasury.keys():
                ratio = float(previous_dividend_yield[year]) / float(three_years_treasury[year])
                previous_dividend_to_treasury[year] = ratio

        print(previous_dividend_to_treasury)
        min_ratio = min(previous_dividend_to_treasury.values())
        max_ratio = max(previous_dividend_to_treasury.values())

        return (min_ratio, max_ratio)

    def buy_check_by_dividend_algorithm(self, code):
        estimated_dividend_to_treasury = self.calculate_estimated_dividend_to_treasury(code)
        (min_ratio, max_ratio) = self.get_min_max_dividend_to_treasury(code)

        if estimated_dividend_to_treasury >= max_ratio:
            return (1, estimated_dividend_to_treasury)
        else:
            return (0, estimated_dividend_to_treasury)

    def calculate_estimated_dividend_to_treasury(self, code):
        estimated_dividend_yield = webreader.get_estimated_dividend_yield(code)

        if np.isnan(estimated_dividend_yield):
            estimated_dividend_yield = webreader.get_dividend_yield(code)

            if estimated_dividend_yield == "":
                estimated_dividend_yield = 0

    def run_dividend(self):
        buy_list = []

        for code in self.kospi_codes:
            print('Check: ', code)
            ret = self.buy_check_by_dividend_algorithm(code)

            if ret[0] == 1:
                print("Pass", ret)
                buy_list.append((code, ret[1]))
            else:
                print("Fail", ret)

if __name__=='__main__':
    app = QApplication(sys.argv)
    pymon = PyMon()
    # pymon.run()
    pymon.run_dividend()