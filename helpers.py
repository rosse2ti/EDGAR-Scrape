def mergeDictionary(statements_list: list) -> dict:
    if len(statements_list) > 1:
        dict_final = {}
        for statement in statements_list:
            for key, categ in statement.items():
                if key not in dict_final:
                    dict_final[key] = {}
                for i, items in categ.items():
                    if type(items) is not dict:
                        if i in dict_final[key]:
                            dict_final[key][i].append(items)

                        else:
                            dict_final[key][i] = [items]

                    else:
                        if i not in dict_final[key]:
                            dict_final[key][i] = {}
                        for k, single in items.items():
                            if k in dict_final[key][i]:
                                dict_final[key][i][k].append(single)
                            else:
                                dict_final[key][i][k] = [single]
        dict_final["info"]["ticker"] = dict_final["info"]["ticker"][0]
        return dict_final
    else:
        return statements_list[0]
