#encoding:utf-8
#! /usr/bin/env python

import pymysql as db

sql_0 = 'select id,contract_id,predict_period,predict_time from future_predictor where actual_result=-1 ORDER BY contract_id ASC,predict_period ASC,predict_time ASC'
sql_1 = 'SELECT trade_date, close_price from future_quote WHERE contract_id=%(contract_id)s and period_type=%(period_type)s and trade_date>=DATE_FORMAT(%(predict_time)s,\'%%Y-%%m-%%d %%H:%%i:%%s\') and open_price > 0 and close_price > 0 ORDER BY trade_date ASC'
sql_2 = 'UPDATE future_predictor SET actual_result=%(actual_result)s where id=%(id)s'

period_dict = {30 : 5}
rc_dict = {30 : 6}

def main():
    try:
        conn = db.Connect(host='101.37.60.132', 
                          user='root', passwd='funci@868', db='collected_data', port=3306, charset='utf8')
        cur = conn.cursor()
        
        #获取未验证的预测记录
        rowcount = cur.execute(sql_0)
        print("共查询到{:d}条未验证的期货走势预测记录。\n".format(rowcount))

        results = cur.fetchall()
        for row in results:
            id = row[0]
            contract_id = row[1]
            predict_period = row[2]
            predict_time = row[3]

            print('Evaluating:' + 'contract_id='+ str(contract_id) + ',predict_period=' + str(predict_period) + ',predict_time=' + predict_time.strftime('%Y-%m-%d %H:%M:%S') + ' ...', end='')
            
            value = {'contract_id':contract_id, 'period_type':period_dict[predict_period], 'predict_time':predict_time}
            rowcount = cur.execute(sql_1, value)
            if rowcount > rc_dict[predict_period]:
                qr = cur.fetchall()
                if abs(qr[6][1] - qr[0][1]) / qr[0][1] <= 0.005:
                    actual_result = 0
                elif qr[6][1] < qr[0][1]:
                    actual_result = 1
                else:
                    actual_result = 2
                
                value = {'id':id, 'actual_result':actual_result}
                cur.execute(sql_2, value)
                conn.commit()
                
                print('actual_result=' + str(actual_result) + '   ok!')
            else:
                print('result has not come out yet.')
    except db.Error as e:
        print("Mysql Error {:d}:{:s}\n".format(e.args[0], e.args[1]))
    finally:
        cur.close()
        conn.close()    

if __name__ == '__main__':
    main()