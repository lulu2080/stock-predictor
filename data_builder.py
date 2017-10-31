#encoding:utf-8

import pymysql as db
import numpy as np
import csv

temp_data_path = 'd:/tmp/'

def main():
    get_stock_data(3)

def get_stock_data(inner_code):
    try:
        conn = db.Connect(host='139.196.132.213', 
                          user='luzhaohui', passwd='zhongba@01', db='jydb', port=3306, charset='utf8')
        
        #按股票代码+交易时间升序排序，每四行滑动依次迭代构建训练数据集。
        cur = conn.cursor()
#        sql = 'SELECT InnerCode, DATE(TradingDay) TradeDate, TurnoverValue, OpenPrice, ClosePrice, HighPrice, ClosePrice from qt_dailyquote WHERE InnerCode=%s and OpenPrice > 0  ORDER BY InnerCode, TradingDay ASC'
        sql = 'SELECT InnerCode, DATE(TradingDay) TradeDate, TurnoverValue, OpenPrice, ClosePrice, HighPrice, TurnoverRate from QT_Performance WHERE InnerCode=%s and OpenPrice > 0 and NOT ISNULL(TurnoverRate) ORDER BY InnerCode, TradingDay ASC'
        rowcount = cur.execute(sql, (inner_code))
        print("共查询到{:d}条行情数据。\n".format(rowcount))

        q, data = [], []

        results=cur.fetchall()        
        for row in results:
            data_row = np.zeros([4], dtype=float)
            data_row[0] = row[2]    #成交额
            data_row[1] = row[3]    #开盘价
            data_row[2] = row[4]    #收盘价
            data_row[3] = row[6]    #换手率
            
            q.append(data_row)
            if len(q) >= 4:
                d = organize_data(q)
                data.append(d)
                del q[0]
                
        #写入csv文件
        return write_to_csv(data, inner_code)
        
    except db.Error as e:
        print("Mysql Error {:d}:{:s}\n".format(e.args[0], e.args[1]))
    finally:
        cur.close()
        conn.close()

def organize_data(q):
    if abs(q[3][2] - q[3][1]) / q[3][1] <= 0.005:
        label = 0
    elif q[3][2] < q[3][1]:
        label = 1
    else:
        label = 2

    return [q[0][0], q[1][0], q[2][0], q[0][3], q[1][3], q[2][3], label]

#def organize_data(q):
#    if abs(q[1][2] - q[1][1]) / q[1][1] <= 0.005:
#        label = 0
#    elif q[1][2] < q[1][1]:
#        label = 1
#    else:
#        label = 2
#
#    return [q[0][0], q[0][1], q[0][2], q[0][3], q[0][4], label]

def write_to_csv(data, inner_code):
    csv_filepath = temp_data_path + str(inner_code) + '.csv'
    csvfile = open(csv_filepath, 'w', newline='')
    writer = csv.writer(csvfile)
    writer.writerow([0, 0, 0, 0, 0, 0, 0])
    for d in data:
        writer.writerow(d)   
    csvfile.close()
    return csv_filepath

if __name__ == '__main__':
    main()
