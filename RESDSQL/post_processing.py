from difflib import SequenceMatcher

def find_most_similar_sequence(source_sequence, target_sequences):
    max_match_length = -1
    most_similar_sequence = ""
    for target_sequence in target_sequences:
        match_length = SequenceMatcher(None, source_sequence, target_sequence).find_longest_match(0, len(source_sequence), 0, len(target_sequence)).size
        if max_match_length < match_length:
            max_match_length = match_length
            most_similar_sequence = target_sequence
    
    return most_similar_sequence

def fix_fatal_errors_in_sql(sql: str, tc_original):
    '''
        Try to fix fatal schema item errors in the predicted sql.
    '''
    tc_names = tc_original
    table_names = [tc_name.split(".")[0].strip() for tc_name in tc_names]
    column_names = [tc_name.split(".")[1].strip() for tc_name in tc_names]

    sql_tokens = sql.split()
    new_tokens = []
    for idx, token in enumerate(sql_tokens):
        # case A: current token is a wrong ``table.column'' name
        if "." in token and token != "@.@" and not token.startswith("'"):
            if token not in tc_names:
                current_table_name = token.split(".")[0]
                current_column_name = token.split(".")[1]

                # case 1: both table name and column name are existing, but the column doesn't belong to the table
                if current_table_name in table_names and current_column_name in column_names:
                    candidate_table_names = [table_name for table_name, column_name in zip(table_names, column_names) \
                        if current_column_name == column_name]
                    new_table_name = find_most_similar_sequence(current_table_name, candidate_table_names)
                    new_tokens.append(new_table_name+"."+current_column_name)
                # case 2: table name is not existing but column name is correct
                elif current_table_name not in table_names and current_column_name in column_names:
                    candidate_table_names = [table_name for table_name, column_name in zip(table_names, column_names) \
                        if current_column_name == column_name]
                    new_table_name = find_most_similar_sequence(current_table_name, candidate_table_names)
                    new_tokens.append(new_table_name+"."+current_column_name)
                # case 3: table name is correct but column name is not existing
                elif current_table_name in table_names and current_column_name not in column_names:
                    candidate_column_names = [column_name for table_name, column_name in zip(table_names, column_names) \
                        if current_table_name == table_name]
                    new_column_name = find_most_similar_sequence(current_column_name, candidate_column_names)
                    new_tokens.append(current_table_name+"."+new_column_name)
                # case 4: both table name and column name are not existing
                elif current_table_name not in table_names and current_column_name not in column_names:
                    new_column_name = find_most_similar_sequence(current_column_name, column_names)
                    candidate_table_names = [table_name for table_name, column_name in zip(table_names, column_names) \
                        if new_column_name == column_name]
                    new_table_name = find_most_similar_sequence(current_table_name, candidate_table_names)
                    new_tokens.append(new_table_name+"."+new_column_name)
            else:
                new_tokens.append(token)
        # case B: current token is a wrong "table'' name
        elif sql_tokens[idx-1] == "from" and token not in table_names:
            new_table_name = find_most_similar_sequence(token, list(set(table_names)))
            new_tokens.append(new_table_name)
            
        # case C: current token is a wrong "column" name
        elif sql_tokens[idx-1] in ("where", "and")\
            and not token.isnumeric()\
            and token not in column_names:
                
            new_column_name = find_most_similar_sequence(token, list(set(column_names)))
            new_tokens.append(new_column_name)
        # case D: current token is right
        else:
            new_tokens.append(token)

    return " ".join(new_tokens)
    