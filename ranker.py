import json
import argparse
import sqlite3
import math
from evaluation import count_component1, count_component2, count_others

table_list = json.load(open('spider/tables.json'))
count_dict = {}
for entry in table_list:
    db_id = entry['db_id']
    num_tables = len(entry['table_names'])
    num_columns = len(entry['column_names'])-1
    count_dict[db_id] = (num_tables, num_columns)


class Ranker:
    def __init__(self,pred_file):
        self.data = json.load(open('spider/dev.json'))
        with open(pred_file) as f:
            self.pred = f.readlines()
        
    def __getitem__(self, key):
        sql = self.data[key]['sql']
        def get_difficulty(sql):
            count_comp1_ = count_component1(sql)
            count_comp2_ = count_component2(sql)
            count_others_ = count_others(sql)

            if count_comp1_ <= 1 and count_others_ == 0 and count_comp2_ == 0:
                return "easy"
            elif (count_others_ <= 2 and count_comp1_ <= 1 and count_comp2_ == 0) or \
                    (count_comp1_ <= 2 and count_others_ < 2 and count_comp2_ == 0):
                return "medium"
            elif (count_others_ > 2 and count_comp1_ <= 2 and count_comp2_ == 0) or \
                    (2 < count_comp1_ <= 3 and count_others_ <= 2 and count_comp2_ == 0) or \
                    (count_comp1_ <= 1 and count_others_ == 0 and count_comp2_ <= 1):
                return "hard"
            else:
                return "extra"
        db_id = self.data[key]['db_id']
        ntables, ncolumn = count_dict[db_id]
        
        gold_query = self.data[key]['query']
        pred_query = self.pred[key].strip().replace('<>', '!=')

        conn = sqlite3.connect(f"spider/database/{db_id}/{db_id}.sqlite")
        cursor = conn.cursor()
        try:
            cursor.execute(gold_query)
            result_gold = cursor.fetchall()
            gold_len = (len(result_gold))
        except:
            gold_len = 0
        try:
            cursor.execute(pred_query)
            result_pred= cursor.fetchall()
            pred_len = (len(result_pred))
        except:
            pred_len = 0
        # result_pred = cursor.execute(pred_query).fetchall()
        # print(result_pred)

        return gold_query, get_difficulty(sql), ntables, ncolumn, pred_query
    
    def eval(self):
        def get_difficulty(sql):
            count_comp1_ = count_component1(sql)
            count_comp2_ = count_component2(sql)
            count_others_ = count_others(sql)

            if count_comp1_ <= 1 and count_others_ == 0 and count_comp2_ == 0:
                return "easy"
            elif (count_others_ <= 2 and count_comp1_ <= 1 and count_comp2_ == 0) or \
                    (count_comp1_ <= 2 and count_others_ < 2 and count_comp2_ == 0):
                return "medium"
            elif (count_others_ > 2 and count_comp1_ <= 2 and count_comp2_ == 0) or \
                    (2 < count_comp1_ <= 3 and count_others_ <= 2 and count_comp2_ == 0) or \
                    (count_comp1_ <= 1 and count_others_ == 0 and count_comp2_ <= 1):
                return "hard"
            else:
                return "extra"
            
        dif_res = {'easy': {'correct': 0, 'total': 0},
                   'medium': {'correct': 0, 'total': 0},
                    'hard': {'correct': 0, 'total': 0},
                    'extra': {'correct': 0, 'total': 0}}
        tab_res = {}
        col_res = {}
        total = 0
        correct = 0

        for key in range(len(self.data)):
            sql = self.data[key]['sql']

            difficulty = get_difficulty(sql)
            db_id = self.data[key]['db_id']
            ntables, ncolumn = count_dict[db_id]
            
            gold_query = self.data[key]['query']
            pred_query = self.pred[key].strip().replace('<>', '!=')

            conn = sqlite3.connect(f"spider/database/{db_id}/{db_id}.sqlite")
            cursor = conn.cursor()
            try:
                cursor.execute(gold_query)
                result_gold = cursor.fetchall()
                gold_len = (len(result_gold))
            except:
                gold_len = 0
            try:
                cursor.execute(pred_query)
                result_pred= cursor.fetchall()
                pred_len = (len(result_pred))
            except:
                pred_len = 0

            dif_res[difficulty]['total'] += 1
            if math.floor(ntables/6) in tab_res:
                tab_res[math.floor(ntables/6)]['total'] += 1
            else:
                tab_res[math.floor(ntables/6)] = {'correct': 0, 'total': 0}
            if math.floor(ncolumn/10) in col_res:
                col_res[math.floor(ncolumn/10)]['total'] += 1
            else:
                col_res[math.floor(ncolumn/10)] = {'correct': 0, 'total': 0}
            total += 1


            if gold_len == pred_len:
                dif_res[difficulty]['correct'] += 1
                tab_res[math.floor(ntables/6)]['correct'] += 1
                col_res[math.floor(ncolumn/10)]['correct'] += 1
                correct += 1
        return correct/total,dif_res, tab_res, col_res


if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--pred', dest='pred', type=str)
    # args = parser.parse_args()

    # pred = args.pred
    # ranker = Ranker(pred)
    ranker = Ranker('prompting/chatgpt_type_final_output.txt')
    acc,dif_res, tab_res, col_res = ranker.eval()
    
    print(acc)
    print(dif_res)
    print(tab_res)
    #print(col_res)
