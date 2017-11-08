#encoding:utf-8

import urllib
import json
import csv
import pymysql as db

#历史日K数据
url_day = 'http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesDailyKLine?symbol='
#历史5分钟数据
url_5f = 'http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesMiniKLine5m?symbol='
#历史30分钟数据
url_30f = 'http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesMiniKLine30m?symbol='

sql_0 = 'INSERT INTO future_quote(contract_id, period_type, trade_date, open_price, close_price, high_price, low_price, turnover_volume) VALUES(%(contract_id)s, %(period_type)s, %(trade_date)s, %(open_price)s, %(close_price)s, %(high_price)s, %(low_price)s, %(turnover_volume)s)'
sql_1 = 'SELECT id from future_contract WHERE contract_code=%s'
sql_2 = 'SELECT 1 from future_quote WHERE contract_id=%(contract_id)s and period_type=%(period_type)s and trade_date=%(trade_date)s'

def main():
    code=input('Please input a code:').upper()
    fcode = fill_code(code)
    data = grab_data(fcode, 0)
    contract_id = write_to_db(fcode, 0, data)
    if contract_id > 0:
        print('successfully! writed total row count:' + str(len(data)))
    else:
        print('Failure!')

def fill_code(code):
    #根据用户输入的代码得到请求代码
    mapcode={'60':'sh'+code,'00':'sz'+code,'50':'f_'+code,'15':'fu_'+code,'RM':'h_'+code}
    if (code[0] in list('abcdefghijgklmnopqrstuvwxyz'.upper())) and (code[2:3]=='1' or code[2:3]=='0' or code[1:2]=='1' or code[1:2]=='0') :
        return code
    else:
        fullcode=mapcode[code[:2]]
        return fullcode
    
def grab_data(fcode, period_type):
    url = ''
    if period_type == 0:
        url = url_day + fcode
    elif period_type == 5:
        url = url_5f + fcode
    elif period_type == 30:
        url = url_30f+ fcode

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

def write_to_db(fcode, period_type, data):
    try:
        conn = db.Connect(host='101.37.60.132', 
                          user='root', passwd='funci@868', db='collected_data', port=3306, charset='utf8')
        cur = conn.cursor()
        
        #获取期货合约内部ID
        contract_id = -1
        if cur.execute(sql_1, (fcode)) > 0:
            r = cur.fetchone()
            contract_id = r[0]
        else:
            return -1

        for d in data:
            value = {'contract_id':contract_id, 'period_type':period_type, 'trade_date':d[0], 'open_price':d[1], 'close_price':d[4], 'high_price':d[2], 'low_price':d[3], 'turnover_volume':d[5]}
            
            rowcount = cur.execute(sql_2, value)
            if rowcount <= 0:
                print('writing:' + ''.join(d) + '...', end='')
                cur.execute(sql_0, value)
                conn.commit()
                print('ok!')
            else:
                print('already existed, skipped!')
        
        return contract_id
    except db.Error as e:
        print("Mysql Error {:d}:{:s}\n".format(e.args[0], e.args[1]))
    finally:
        cur.close()
        conn.close()

def do_data(contract_code, period_type):
    fcode = fill_code(contract_code)
    data = grab_data(fcode, period_type)
    contract_id = write_to_db(fcode, period_type, data)
    if contract_id > 0:
        print('successfully! writed total row count:' + str(len(data)))
        return contract_id
    else:
        print('failure!')
        return -1

    
if __name__ == '__main__':
    main()