#encoding:utf-8
#! /usr/bin/env python

import os
import pymysql as db

#sql_0 = 'select InnerCode from secumain where InnerCode=18575 ORDER BY InnerCode ASC LIMIT 0,1000'
sql_0 = 'select InnerCode from secumain where InnerCode=1 or (SecuCategory=1 and ListedSector in (1,2,6) and ListedState=1) ORDER BY InnerCode ASC'
sql_1 = 'select 1 from zb_predictor where InnerCode=%(InnerCode)s and period=%(period)s'
sql_2 = 'INSERT INTO zb_predictor(InnerCode, result, accRate, lastTradingDay, period, created_at, updated_at) VALUES(%(InnerCode)s, %(result)s, %(accRate)s, %(lastTradingDay)s, %(period)s, now(), now())'
sql_3 = 'UPDATE zb_predictor SET result=%(result)s, accRate=%(accRate)s, lastTradingDay=%(lastTradingDay)s, updated_at=now() where InnerCode=%(InnerCode)s and period=%(period)s'

def main():
    try:
        conn = db.Connect(host='139.196.132.213', 
                          user='luzhaohui', passwd='zhongba@01', db='jydb', port=3306, charset='utf8')
        cur = conn.cursor()
        
        #获取所有股票内码列表
        rowcount = cur.execute(sql_0)
        print("共查询到{:d}个股票/指数。\n".format(rowcount))

        results = cur.fetchall()
        for row in results:
            inner_code = row[0]
            ret = os.popen('python stock_service.py --innerCode ' + str(inner_code))
            data = ret.readlines()[-1].strip().split(',')
            if not data[0].isdigit():
                continue
            if int(data[0]) == -1:
                continue

            value = {'InnerCode':inner_code, 'result':data[0], 'accRate':data[1], 'lastTradingDay':data[2], 'period':1}
            
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