#encoding:utf-8

import pymysql as db
import numpy as np
import csv

def main():
    try:
        conn = db.Connect(host='139.196.132.213', 
                          user='luzhaohui', passwd='zhongba@01', db='zhongba', port=3306, charset='utf8')
        
        #按股票代码+交易时间升序排序，每四行滑动依次迭代构建训练数据集。
        cur = conn.cursor()
        rowcount = cur.execute('SELECT InnerCode, DATE(TradingDay) TradeDate, TurnoverValue, OpenPrice, ClosePrice from qt_dailyquote WHERE InnerCode = 1 and TradingDay >= STR_TO_DATE(\'1990-01-01 00:00:00\', \'%Y-%m-%d %H:%i:%s\') ORDER BY InnerCode, TradingDay ASC')
        print("共查询到{:d}条行情数据。\n".format(rowcount))

        q, data = [], []

        results=cur.fetchall()        
        for row in results:
            data_row = np.zeros([3], dtype=float)
            data_row[0] = row[2]
            data_row[1] = row[3]
            data_row[2] = row[4]
            
            q.append(data_row)
            if len(q) >= 4:
                d = organize_data(q)
                data.append(d)
                del q[0]
                
        #写入csv文件
        write_to_csv(data)
        
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

    return [q[0][0], q[1][0], q[2][0], label]

def write_to_csv(data):
    csv_filepath = 'd:/tmp/stock_data.csv'
    csvfile = open(csv_filepath, 'w', newline='')
    writer = csv.writer(csvfile)
    writer.writerow([0, 0, 0, 0])
    for d in data:
        writer.writerow(d)   
    csvfile.close()

if __name__ == '__main__':
    main()
