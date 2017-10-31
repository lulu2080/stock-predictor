#encoding:utf-8

import urllib
import json
import csv
import pymysql as db


sql_0 = 'INSERT INTO future_quote(contract_id, period_type, trade_date, open_price, close_price, high_price, low_price, turnover_volume) VALUES(%(contract_id)s, %(period_type)s, %(trade_date)s, %(open_price)s, %(close_price)s, %(high_price)s, %(low_price)s, %(turnover_volume)s)'

#定义函数，用户输入股票代码可从新浪财经接口取数据
code=input('Please input a code:').upper()

def fill_code(code):
    #根据用户输入的代码得到请求代码
    mapcode={'60':'sh'+code,'00':'sz'+code,'50':'f_'+code,'15':'fu_'+code,'RM':'h_'+code}
    if (code[0] in list('abcdefghigklmnopqrstuvwxyz'.upper())) and (code[2:3]=='1' or code[2:3]=='0' or code[1:2]=='1' or code[1:2]=='0') :
        return code
    else:
        fullcode=mapcode[code[:2]]
        return fullcode
    
def get_data(code):
    #历史日K数据
    url = 'http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesDailyKLine?symbol=' + code
    #将返回数据解析为列表
    datastr=urllib.request.urlopen(url).read().decode('gb2312')
    jdata = json.loads(datastr)
    return jdata
    
def write_to_csv(data):
    csv_filepath = 'd:/tmp/data.csv'
    csvfile = open(csv_filepath, 'w', newline='')
    writer = csv.writer(csvfile)
    for d in data:
        writer.writerow(d)   
    csvfile.close()
    return csv_filepath

def write_to_db(data):
    try:
        conn = db.Connect(host='101.37.60.132', 
                          user='root', passwd='funci@868', db='collected_data', port=3306, charset='utf8')
        cur = conn.cursor()

        for d in data:
            print('writing:' + d, end='')
            value = {'contract_id':1, 'period_type':0, 'trade_date':d[0], 'open_price':d[1], 'close_price':d[4], 'high_price':d[2], 'low_price':d[3], 'turnover_volume':d[5]}
            cur.execute(sql_0, value)
            conn.commit()
            print('ok!')
    except db.Error as e:
        print("Mysql Error {:d}:{:s}\n".format(e.args[0], e.args[1]))
    finally:
        cur.close()
        conn.close()


#调用函数
code = fill_code(code)
data = get_data(code)
write_to_db(data)
print('successfully! writed total row count:' + len(data))
