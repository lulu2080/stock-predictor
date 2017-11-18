#encoding:utf-8

import pymysql as db
import numpy as np
import decimal
import csv

temp_data_path = '/tmp/ai-temp-files/'
sql_0 = 'SELECT trade_date, open_price, close_price, high_price, low_price, turnover_volume from future_quote WHERE contract_id=%s and period_type=%s and open_price > 0 and close_price > 0 ORDER BY trade_date DESC'

def main():
    p, d = get_contract_quote(1, 5)
    print('lastTradeDate:' + d.strftime('%Y-%m-%d %H:%M:%S') + ', data_file_path:' + p)

def get_contract_quote(contract_id, period_type):
    try:
        conn = db.Connect(host='101.37.60.132', 
                          user='root', passwd='funci@868', db='collected_data', port=3306, charset='utf8')
        
        #按交易时间降序排序，每六行滑动依次迭代构建训练数据集。
        cur = conn.cursor()

        rowcount = cur.execute(sql_0, (contract_id, period_type))
        print("共查询到{:d}条行情数据。\n".format(rowcount))

        q, data = [], []
        lastTradeDate = None
        data_row = None
        index = 0

        results=cur.fetchall()
        for row in results:
            if index == 0:
                lastTradeDate = row[0]
            if index % 6 == 0:
                if not data_row is None:
                    q.append(data_row)
                    if len(q) >= 3:
                        d = organize_data(q)
                        data.append(d)
                        del q[0]
                data_row = np.zeros([3], dtype=decimal.Decimal)
                data_row[2] = row[2]    #收盘价
            data_row[0] += row[5]    #成交量
            data_row[1] = row[1]    #开盘价
            index += 1

        data = data[::-1]
        #写入csv文件
        return write_to_csv(data, contract_id), lastTradeDate
        
    except db.Error as e:
        print("Mysql Error {:d}:{:s}\n".format(e.args[0], e.args[1]))
    finally:
        cur.close()
        conn.close()

def organize_data(q):
    return [q[0][0], q[1][0], q[2][0]]

def write_to_csv(data, contract_id):
    csv_filepath = temp_data_path + str(contract_id) + '.csv'
    csvfile = open(csv_filepath, 'w', newline='')
    writer = csv.writer(csvfile)
    writer.writerow([0, 0, 0])
    for d in data:
        writer.writerow(d)   
    csvfile.close()
    return csv_filepath

if __name__ == '__main__':
    main()
