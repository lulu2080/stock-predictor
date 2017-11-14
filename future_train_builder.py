#encoding:utf-8

import pymysql as db
import numpy as np
import csv

temp_data_path = 'd:/tmp/'
sql_0 = 'SELECT trade_date, open_price, close_price, high_price, low_price, turnover_volume from future_quote WHERE contract_id=%s and period_type=%s and open_price > 0 and close_price > 0 ORDER BY trade_date ASC'

def main():
    p, d = get_contract_quote(1, 0)
    print('lastTradeDate:' + d.strftime('%Y-%m-%d %H:%M:%S') + ', data_file_path:' + p)

def get_contract_quote(contract_id, period_type):
    try:
        conn = db.Connect(host='101.37.60.132', 
                          user='root', passwd='funci@868', db='collected_data', port=3306, charset='utf8')
        
        #按交易时间升序排序，每四行滑动依次迭代构建训练数据集。
        cur = conn.cursor()

        rowcount = cur.execute(sql_0, (contract_id, period_type))
        print("共查询到{:d}条行情数据。\n".format(rowcount))

        q, data = [], []
        lastTradeDate = None

        results=cur.fetchall()
        for row in results:
            lastTradeDate = row[0]

            data_row = np.zeros([4], dtype=float)
            data_row[0] = row[5]    #成交量
            data_row[1] = row[1]    #开盘价
            data_row[2] = row[2]    #收盘价
            
            q.append(data_row)
            if len(q) >= 4:
                d = organize_data(q)
                data.append(d)
                del q[0]
                
        #写入csv文件
        return write_to_csv(data, contract_id), lastTradeDate
        
    except db.Error as e:
        print("Mysql Error {:d}:{:s}\n".format(e.args[0], e.args[1]))
    finally:
        cur.close()
        conn.close()

def organize_data(q):
    if abs(q[3][2] - q[2][2]) / q[2][2] <= 0.005:
        label = 0
    elif q[3][2] < q[2][2]:
        label = 1
    else:
        label = 2

    return [q[0][0], q[1][0], q[2][0], label]

def write_to_csv(data, contract_id):
    csv_filepath = temp_data_path + str(contract_id) + '.csv'
    csvfile = open(csv_filepath, 'w', newline='')
    writer = csv.writer(csvfile)
    writer.writerow([0, 0, 0, 0])
    for d in data:
        writer.writerow(d)   
    csvfile.close()
    return csv_filepath

if __name__ == '__main__':
    main()
