#encoding:utf-8

import urllib

#定义函数，用户输入股票代码可从新浪财经接口取数据
code=input('Please input a code:').upper()

def FullCode(code):
    #根据用户输入的代码得到请求代码
    mapcode={'60':'sh'+code,'00':'sz'+code,'50':'f_'+code,'15':'fu_'+code,'RM':'h_'+code}
    if (code[0] in list('abcdefghijgklmnopqrstuvwxyz'.upper())) and (code[2:3]=='1' or code[2:3]=='0' or code[1:2]=='1' or code[1:2]=='0') :
        return code
    else:
        fullcode=mapcode[code[:2]]
        return fullcode
    
def GetData(code):
    #请求代码
    url='http://hq.sinajs.cn/list='+code

    #将返回数据解析为列表
    datastr=urllib.request.urlopen(url).read().decode('gb2312').split('"')[1].split(',')
    data_list=list(datastr)
    
    #datalenth=len(data_list)
    #股票返回值含义
    stock_item='代码,开盘价,昨收,最新价,最高价,最低价,买入价,卖出价,成交量,成交额,买一,买一,买二,买二,买三 ,买三,买四,买四,买五,买五,卖一,卖一,卖二,卖二,卖三,卖三,卖四,卖四,卖五,卖五,日期,时间,停牌状态'
    stock=list(stock_item.split(','))
    #基金或ETF返回值含义
    fund_f_item='基金简称,最新净值,累计净值,昨日净值,净值日期,基金规模(亿份)'
    fund_f=list(fund_f_item.split(','))
    #开放式基金返回值含义
    fund_fu_item='名称,时间,最新估值,单位净值,累计单位净值,五分钟涨速(乘100后的),涨跌幅(乘100后的),日期'
    fund_fu=list(fund_fu_item.split(','))
    #中行汇率返回值定义
    fx_item='货币名称,现汇买入价,现钞买入价,现汇卖出价,现钞卖出价,中行折算价,发布日期,发布时间'
    fx=list(fx_item.split(','))
    
    future_item='期货合约,交易所代码,开盘价,最高价,最低价,昨收,买价,卖价,最新价,结算价,昨结算,买量,卖量,持仓量,成交量,交易所简称,品种名简称,日期'
    future=list(future_item.split(','))
    
    name_list={'sh':stock,'sz':stock,'f_':fund_f,'fu':fund_fu,'h_':fx}
    
    if (code[0] in list('abcdefghijgklmnopqrstuvwxyz'.upper())) and (code[2:3]=='1' or code[2:3]=='0' or code[1:2]=='1' or code[1:2]=='0') :
        for i in range(len(future)):
            print( future[i],': -->',data_list[i])
    else:
        datalenth=len(data_list)
        for i in range(datalenth):
            try:
                print(name_list[code[:2]][i],': -->',float(data_list[i]))
            except ValueError:
                print(data_list[i])

#调用函数
code=FullCode(code)
GetData(code)