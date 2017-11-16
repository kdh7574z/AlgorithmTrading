import pandas as pd
import sqlite3

con_down = sqlite3.connect("./DataBase_backup.db")
con_upload = sqlite3. connect('./DataBase.db')

class PyMon:
    def __init__(self, type):
        self.make_list(type)
        self.run()

    def make_list(self, type):
        self.List = []
        aaa = "./Data_list/Market_list{}.txt".format(type)
        f = open(aaa, 'rt')
        while True:
            line = f.readline()
            line = line[:(len(line)-1)]
            if not line: break
            self.List.append(line)
        f.close

    def run(self):
        print("Data Reform is Start")
        for i in range(len(self.List)):
            code = self.List[i]
            # print(code)
            names = "KRX : " + code
            names_input = "SELECT * FROM '"+"{}'".format(names)
            data = pd.read_sql(names_input, con_down, index_col=None)

            # print(data.shape[1])
            if data.shape[1] == 7:
                data = self.make_ma(data)
                names_output = "KRX : " + code + ""
                data = data.iloc[:, 1:]
                data.to_sql(names_output, con_upload, if_exists='replace')

                if i % 10 == 9:
                    print("{} is Ma_Reform".format(code), "({})".format(i + 1))

        print("Data Reform is Complete")


    def make_ma(self, data):
        ma5 = data['close'].rolling(window=5).mean()
        ma20 = data['close'].rolling(window=20).mean()
        ma60 = data['close'].rolling(window=60).mean()
        ma120 = data['close'].rolling(window=120).mean()

        data.insert(len(data.columns), "ma5", ma5)
        data.insert(len(data.columns), "ma20", ma20)
        data.insert(len(data.columns), "ma60", ma60)
        data.insert(len(data.columns), "ma120", ma120)

        return data


if __name__=='__main__':
    type = 0
    pymon = PyMon(type)
