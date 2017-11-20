#encoding:utf-8
#! /usr/bin/env python

import os
import pymysql as db

sql_0 = 'select id, contract_code from future_contract where status=0 ORDER BY id ASC'
sql_1 = 'select 1 from future_predictor where contract_id=%(contract_id)s and predict_period=%(predict_period)s and predict_time=DATE_FORMAT(%(predict_time)s,\'%%Y-%%m-%%d %%H:%%i:%%s\')'
sql_2 = 'INSERT INTO future_predictor(contract_id, predict_period, predict_time, predict_result, acc_rate, actual_result) VALUES(%(contract_id)s, %(predict_period)s, %(predict_time)s, %(predict_result)s, %(acc_rate)s, %(actual_result)s)'
sql_3 = 'UPDATE future_predictor SET predict_result=%(predict_result)s, acc_rate=%(acc_rate)s where contract_id=%(contract_id)s and predict_period=%(predict_period)s and predict_time=DATE_FORMAT(%(predict_time)s,\'%%Y-%%m-%%d %%H:%%i:%%s\')'
sql_4 = 'select 1 from future_predictor where contract_id=%(contract_id)s and predict_period=%(predict_period)s and predict_time=DATE_FORMAT(%(predict_time)s,\'%%Y-%%m-%%d %%H:%%i:%%s\')'

def main():
    try:
        conn = db.Connect(host='101.37.60.132', 
                          user='root', passwd='funci@868', db='collected_data', port=3306, charset='utf8')
        cur = conn.cursor()
        
        #获取所有股票内码列表
        rowcount = cur.execute(sql_0)
        print("共查询到{:d}个期货合约。\n".format(rowcount))

        results = cur.fetchall()
        for row in results:
            contract_id = row[0]
            contract_code = row[1]
            ret = os.popen('python future_service.py --contractCode ' + str(contract_code))
            data = ret.readlines()[-1].strip().split(',')
            if not data[0].isdigit():
                continue
            if int(data[0]) == -1:
                continue

            value = {'contract_id':contract_id, 'predict_period':30, 'predict_time':data[2], 'predict_result':data[0], 'acc_rate':data[1], 'actual_result':-1}

            rowcount = cur.execute(sql_1, value)
            if rowcount <= 0:
                cur.execute(sql_2, value)
            else:
                cur.execute(sql_3, value)

            conn.commit()
    except db.Error as e:
        print("Mysql Error {:d}:{:s}\n".format(e.args[0], e.args[1]))
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    main()