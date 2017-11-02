#encoding:utf-8

import data_crawling as dc
import future_data_builder as fdb

def main():
    print(get_future_data('CU0', 5))

def get_future_data(contract_code, period_type):
    contract_id = dc.do_data(contract_code, period_type)
    
    if contract_id > 0:
        return fdb.get_contract_quote(contract_id, period_type)
    else:
        return None, None
    

if __name__ == '__main__':
    main()
    