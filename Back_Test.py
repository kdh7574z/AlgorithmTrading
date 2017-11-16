import pandas as pd
import numpy as np
import sqlite3
import math
import matplotlib.pyplot as plt

code = {
    0: '000020',
    1: '000030',
    2: '000040',
    3: '000050',
    4: '000060'
}
day = "20060101 AND 20161231"


if __name__ == "__main__":
    con = sqlite3.connect("./DataBase.db")

    Query = "SELECT date, ma5, ma20 FROM 'KRX : {}' ".format(code[0]) + "WHERE date BETWEEN {}".format(day)
    Data = pd.read_sql(Query, con, index_col=None)
    Data.columns = ['date', 'ma5_1', 'ma20_1']

    for i in range(len(code)-1):
        Query = "SELECT date, ma5, ma20 FROM 'KRX : {}' ".format(code[i+1]) + "WHERE date BETWEEN {}".format(day)
        Data = pd.read_sql(Query, con, index_col=None)

    Data = pd.merge(pd.read_sql("SELECT ma5, ma20 FROM '000030' WHERE date BETWEEN 20060101 AND 20161231", con, index_col=None), Data, how='inner', on='date')
    Data = pd.merge(pd.read_sql("SELECT ma5, ma20 FROM '000040' WHERE date BETWEEN 20060101 AND 20161231", con, index_col=None), Data, how='inner', on='date')
    Data = pd.merge(pd.read_sql("SELECT ma5, ma20 FROM '000050' WHERE date BETWEEN 20060101 AND 20161231", con, index_col=None), Data, how='inner', on='date')
    Data = pd.merge(pd.read_sql("SELECT ma5, ma20 FROM '000060' WHERE date BETWEEN 20060101 AND 20161231", con, index_col=None), Data, how='inner', on='date')
    Data.columns = ['date', '삼성전자', '한국전력', '현대자동차', '아모레퍼시픽', '현대모비스']
    Data = Data.sort_values('date')
    Data.index = range(Data.shape[0])
    # print(Data.tail())
    Data = pd.DataFrame(Data,  dtype='float')

    ma5 = pd.DataFrame([Data.iloc[0:0 + 4, 1:].mean()])
    ma5['date'] = Data.iloc[0 + 4, 0]
    for i in range(Data.shape[0] - 5):
        Summ = pd.DataFrame([Data.iloc[i+1:i+5, 1:].mean()])
        Summ['date'] = Data.iloc[i+5, 0]
        ma5 = ma5.append(Summ)
    ma5.columns = ['삼성전자5', '한국전력5', '현대자동차5', '아모레퍼시픽5', '현대모비스5', 'date']

    ma20 = pd.DataFrame([Data.iloc[0:0 + 20, 1:].mean()])
    ma20['date'] = Data.iloc[0 + 19, 0]
    for i in range(Data.shape[0]-20):
        Summ = pd.DataFrame([Data.iloc[i+1:i+20, 1:].mean()])
        Summ['date'] = Data.iloc[i+20, 0]
        ma20 = ma20.append(Summ)
    ma20.columns = ['삼성전자20', '한국전력20', '현대자동차20', '아모레퍼시픽20', '현대모비스20', 'date']

    Result = pd.merge(ma5, ma20, how='inner', on='date')
    # print(Result.head())

    Weight = np.ones([Data.shape[0], (Data.shape[1]-1)], dtype=np.float32) * 0.2
    Weight = pd.DataFrame(Weight)
    Weight['date'] = Data.iloc[:, 0]
    Weight.columns = ['삼성전자', '한국전력', '현대자동차', '아모레퍼시픽', '현대모비스', 'date']

    Set = pd.merge(Weight, Result, how='left', on='date')
    Set = np.array(Set)


    for i in range(len(Set)-2):
        if not math.isnan(Set[i, 10]):
            if (Set[i, 6] < Set[i, 11]) and (Set[i+2, 6] > Set[i+2, 11]):
                k = 0
                if Set[i + 1, 7] > 0.01:
                    k = k + 0.01
                    Set[i + 2, 1] = Set[i + 1, 1] - 0.01

                if Set[i + 1, 8] > 0.01:
                    k = k + 0.01
                    Set[i + 2, 2] = Set[i + 1, 2] - 0.01

                if Set[i + 1, 9] > 0.01:
                    k = k + 0.01
                    Set[i + 2, 3] = Set[i + 1, 3] - 0.01

                if Set[i + 1, 10] > 0.01:
                    k = k + 0.01
                    Set[i + 2, 4] = Set[i + 1, 4] - 0.01

                Set[i + 2, 0] = Set[i + 1, 0] + k

            elif (Set[i, 6] > Set[i, 11]) and (Set[i+2, 6] < Set[i+2, 11]):
                k = 0
                if Set[i + 1, 7] > 0.04:
                    k = k + 0.01
                    Set[i + 2, 1] = Set[i + 1, 1] + 0.01

                if Set[i + 1, 8] > 0.04:
                    k = k + 0.01
                    Set[i + 2, 2] = Set[i + 1, 2] + 0.01

                if Set[i + 1, 9] > 0.04:
                    k = k + 0.01
                    Set[i + 2, 3] = Set[i + 1, 3] + 0.01

                if Set[i + 1, 10] > 0.04:
                    k = k + 0.01
                    Set[i + 2, 4] = Set[i + 1, 4] + 0.01
                Set[i + 2, 0] = Set[i + 1, 0] - k

            elif (Set[i, 7] < Set[i, 12]) and (Set[i+2, 7] > Set[i+2, 12]):
                k = 0
                if Set[i + 1, 0] > 0.01:
                    k = k + 0.01
                    Set[i + 2, 0] = Set[i + 1, 0] - 0.01

                if Set[i + 1, 2] > 0.01:
                    k = k + 0.01
                    Set[i + 2, 2] = Set[i + 1, 2] - 0.01

                if Set[i + 1, 3] > 0.01:
                    k = k + 0.01
                    Set[i + 2, 3] = Set[i + 1, 3] - 0.01

                if Set[i + 1, 4] > 0.01:
                    k = k + 0.01
                    Set[i + 2, 4] = Set[i + 1, 4] - 0.01
                Set[i + 2, 1] = Set[i + 1, 1] + k

            elif (Set[i, 7] > Set[i, 12]) and (Set[i+2, 7] < Set[i+2, 12]):
                k = 0
                if Set[i + 1, 0] > 0.04:
                    k = k + 0.01
                    Set[i + 2, 0] = Set[i + 1, 0] + 0.01

                if Set[i + 1, 2] > 0.04:
                    k = k + 0.01
                    Set[i + 2, 2] = Set[i + 1, 2] + 0.01

                if Set[i + 1, 3] > 0.04:
                    k = k + 0.01
                    Set[i + 2, 3] = Set[i + 1, 3] + 0.01

                if Set[i + 1, 4] > 0.04:
                    k = k + 0.01
                    Set[i + 2, 4] = Set[i + 1, 4] + 0.01
                Set[i + 2, 1] = Set[i + 1, 1] - k

            elif (Set[i, 8] < Set[i, 13]) and (Set[i+2, 8] > Set[i+2, 13]):
                k = 0
                if Set[i + 1, 1] > 0.01:
                    k = k + 0.01
                    Set[i + 2, 1] = Set[i + 1, 1] - 0.01

                if Set[i + 1, 0] > 0.01:
                    k = k + 0.01
                    Set[i + 2, 0] = Set[i + 1, 0] - 0.01

                if Set[i + 1, 3] > 0.01:
                    k = k + 0.01
                    Set[i + 2, 3] = Set[i + 1, 3] - 0.01

                if Set[i + 1, 4] > 0.01:
                    k = k + 0.01
                    Set[i + 2, 4] = Set[i + 1, 4] - 0.01

                Set[i + 2, 2] = Set[i + 1, 2] + k

            elif (Set[i, 8] > Set[i, 13]) and (Set[i+2, 8] < Set[i+2, 13]):
                k = 0
                if Set[i + 1, 1] > 0.04:
                    k = k + 0.01
                    Set[i + 2, 1] = Set[i + 1, 1] + 0.01

                if Set[i + 1, 0] > 0.04:
                    k = k + 0.01
                    Set[i + 2, 0] = Set[i + 1, 0] + 0.01

                if Set[i + 1, 3] > 0.04:
                    k = k + 0.01
                    Set[i + 2, 3] = Set[i + 1, 3] + 0.01

                if Set[i + 1, 4] > 0.04:
                    k = k + 0.01
                    Set[i + 2, 4] = Set[i + 1, 4] + 0.01
                Set[i + 2, 2] = Set[i + 1, 2] - k

            elif (Set[i, 9] < Set[i, 14]) and (Set[i+2, 9] > Set[i+2, 14]):
                k = 0
                if Set[i + 1, 1] > 0.01:
                    k = k + 0.01
                    Set[i + 2, 1] = Set[i + 1, 1] - 0.01

                if Set[i + 1, 2] > 0.01:
                    k = k + 0.01
                    Set[i + 2, 2] = Set[i + 1, 2] - 0.01

                if Set[i + 1, 0] > 0.01:
                    k = k + 0.01
                    Set[i + 2, 0] = Set[i + 1, 0] - 0.01

                if Set[i + 1, 4] > 0.01:
                    k = k + 0.01
                    Set[i + 2, 4] = Set[i + 1, 4] - 0.01
                Set[i + 2, 3] = Set[i + 1, 3] + k

            elif (Set[i, 9] > Set[i, 14]) and (Set[i+2, 9] < Set[i+2, 14]):
                k = 0
                if Set[i + 1, 1] > 0.04:
                    k = k + 0.01
                    Set[i + 2, 1] = Set[i + 1, 1] + 0.01

                if Set[i + 1, 2] > 0.04:
                    k = k + 0.01
                    Set[i + 2, 2] = Set[i + 1, 2] + 0.01

                if Set[i + 1, 0] > 0.04:
                    k = k + 0.01
                    Set[i + 2, 0] = Set[i + 1, 0] + 0.01

                if Set[i + 1, 4] > 0.04:
                    k = k + 0.01
                    Set[i + 2, 4] = Set[i + 1, 4] + 0.01
                Set[i + 2, 3] = Set[i + 1, 3] - k

            elif (Set[i, 10] < Set[i, 15]) and (Set[i+2, 10] > Set[i+2, 15]):
                k = 0
                if Set[i + 1, 1] > 0.01:
                    k = k + 0.01
                    Set[i + 2, 1] = Set[i + 1, 1] - 0.01

                if Set[i + 1, 2] > 0.01:
                    k = k + 0.01
                    Set[i + 2, 2] = Set[i + 1, 2] - 0.01

                if Set[i + 1, 3] > 0.01:
                    k = k + 0.01
                    Set[i + 2, 3] = Set[i + 1, 3] - 0.01

                if Set[i + 1, 0] > 0.01:
                    k = k + 0.01
                    Set[i + 2, 0] = Set[i + 1, 0] - 0.01

                Set[i + 2, 4] = Set[i + 1, 4] + k

            elif (Set[i, 10] > Set[i, 15]) and (Set[i+2, 10] < Set[i+2, 15]):
                k = 0
                if Set[i + 1, 1] > 0.04:
                    k = k + 0.01
                    Set[i + 2, 1] = Set[i + 1, 1] + 0.01

                if Set[i + 1, 2] > 0.04:
                    k = k + 0.01
                    Set[i + 2, 2] = Set[i + 1, 2] + 0.01

                if Set[i + 1, 3] > 0.04:
                    k = k + 0.01
                    Set[i + 2, 3] = Set[i + 1, 3] + 0.01

                if Set[i + 1, 0] > 0.04:
                    k = k + 0.01
                    Set[i + 2, 0] = Set[i + 1, 0] + 0.01
                Set[i + 2, 4] = Set[i + 1, 4] - k

            else:
                Set[i + 2, 0] = Set[i + 1, 0]
                Set[i + 2, 1] = Set[i + 1, 1]
                Set[i + 2, 2] = Set[i + 1, 2]
                Set[i + 2, 3] = Set[i + 1, 3]
                Set[i + 2, 4] = Set[i + 1, 4]

    Set = pd.DataFrame(Set)
    Weight = Set[[0, 1, 2, 3, 4]]
    Weight.columns =['삼성전자','한국전력','현대자동차','아모레퍼시픽','현대모비스']
    # print(Weight)
    Price = Data[['삼성전자','한국전력','현대자동차','아모레퍼시픽','현대모비스']]
    Weight_0 = np.ones([Data.shape[0], (Data.shape[1] - 1)], dtype=np.float32) * 0.2
    All = (Weight * Price).mean(1)
    BenchMark = (Weight_0 * Price).mean(1)

    plt.plot(All, label='Target')
    plt.plot(BenchMark, label='1/n')
    plt.legend()
    plt.show()









