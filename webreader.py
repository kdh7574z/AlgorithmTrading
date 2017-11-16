from bs4 import BeautifulSoup
import requests
import datetime
import numpy as np
import pandas as pd

def get_3year_treasury():
    url = "http://www.index.go.kr/strata/jsp/showStblGams3.jsp?stts_cd=288401&idx_cd=2884&freq=Y&period=1998:2016"
    html = requests.get(url).text
    # print(html)
    soup = BeautifulSoup(html,'lxml')
    # print(soup)
    tr_data = soup.find_all('tr', id='tr_288401_1')
    td_data = tr_data[0].find_all('td')  #여기에서 실시하면 각각의 data가 문자열 형태로 들어가 있다.

    treasury_3year = {}
    start_year = 1998

    for x in td_data:
        treasury_3year[start_year] = x.text  #이제 이것을 한개의 dict에 넣는다.
        start_year += 1

    # print(treasury_3year)
    return treasury_3year  #이렇게 해서 내용을 정리해서 저장한다.

def get_current_3year_treasury():
    url = "http://info.finance.naver.com/marketindex/interestDailyQuote.nhn?marketindexCd=IRR_GOVT03Y&page=1"
    html = requests.get(url).text

    soup = BeautifulSoup(html, 'lxml')
    tbody_data = soup.find_all('tbody')
    tr_data = tbody_data[0].find_all('tr')
    td_data = tr_data[0].find_all('td')
    return td_data[1].text


def get_estimated_dividend_yield(code):
    df = get_financial_statements(code)
    dividend_yield = df.ix[29]  #df로 전체 set중에서 현금배당수익률 29번만 추출한다.

    now = datetime.datetime.now()  #받은것중에서 현재 시간을 구하기 위해서 시간을 추출한다.
    cur_year = now.year   #추출한 시간에 맞는 data를 뽑는다.

    if str(cur_year) in dividend_yield.index and not np.isnan(dividend_yield[str(cur_year)]):
        return dividend_yield[str(cur_year)]
    elif str(cur_year-1) in dividend_yield.index and not np.isnan(dividend_yield[str(cur_year-1)]):
        return dividend_yield[str(cur_year-1)]
    else:
        return np.NaN


def get_financial_statements(code):
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

def get_previous_dividend_yield(code):
    df = get_financial_statements(code)
    dividend_yield = df.ix[29]

    now = datetime.datetime.now()
    cur_year = now.year

    previous_dividend_yield = {}

    for year in range(cur_year-5, cur_year):
        if str(year) in dividend_yield.index:
            previous_dividend_yield[year] = dividend_yield[str(year)]

    return previous_dividend_yield

if __name__ == "__main__":
    estimated_dividend_yield = get_estimated_dividend_yield('058470')
    print(estimated_dividend_yield)
    print(get_current_3year_treasury())