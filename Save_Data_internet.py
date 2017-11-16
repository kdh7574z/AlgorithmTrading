import requests
import pandas as pd
import sqlite3
import time

con = sqlite3.connect("./DataBaseV.db")
con1 = sqlite3.connect("./DataBaseV_backup.db")
TIME_INTERVAL = 2

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
            line = line[:(len(line) - 1)]
            if not line: break
            self.List.append(line)
        f.close
        self.List = self.List[900:]

    def run(self):
        print("Data Download is Start")
        for i in range(len(self.List)):
            code = self.List[i]
            df = self.get_financial_statements(code)
            names = "KRX_I : " + code + ""
            df.to_sql(names, con, if_exists='replace')
            df.to_sql(names, con1, if_exists='replace')
            time.sleep(1)
            if i % 10 == 9:
                print("{} is download".format(code), "({})".format(i + 1))
            time.sleep(TIME_INTERVAL)
        print("Data Download is Complete")

    def get_financial_statements(self, code):
        url = "http://companyinfo.stock.naver.com/v1/company/ajax/cF1001.aspx?cmp_cd={}&fin_typ=0&freq_typ=Y".format(code)
        html = requests.get(url).text

        html = html.replace('<th class="bg r01c02 endLine line-bottom"colspan="8">연간</th>', "")
        html = html.replace("<span class='span-sub'>(IFRS연결)</span>", "")
        html = html.replace("<span class='span-sub'>(IFRS별도)</span>", "")
        html = html.replace("<span class='span-sub'>(GAAP개별)</span>", "")
        html = html.replace('\t', '')
        html = html.replace('\n', '')
        html = html.replace('\r', '')

        df_list = pd.read_html(html)
        df = df_list[0]
        df = pd.DataFrame(df)
        df.columns = ['지표명', '2012', '2013', '2014', '2015', '2016', '2017', '2018/12(E)', '2019/12(E)']
        return df

if __name__=='__main__':
    type = 0
    pymon = PyMon(type)
    # while():
    #     print("0:장내, 3:ELW, 4:뮤추얼펀드, 5:신주인수권, 6:리츠, 8:ETF, 9:하이일드펀드, 10:코스닥, 30:제3시장, 1:exit)\n")
    #     type = input("please insert what you want to type number : ")
    #     pymon = PyMon(type)
    #     if type == 1:
    #         break


