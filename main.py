import json
import helpers as hp
from fundamentals import GetFundamentals

ticker = "AAPL"
steps = 40

statements = []

for step in range(steps + 1):
    instance = GetFundamentals(ticker, step)
    cik = instance.get_cik()
    submission = instance.get_submissions(cik)
    facts_list = instance.get_company_facts(submission, cik)
    statement_json = instance.parse_instance(facts_list[0], facts_list[1])
    statements.append(statement_json)


fundamental_data = hp.mergeDictionary(statements)


with open(("json/{}.json").format(ticker), "w") as f:
    json.dump(fundamental_data, f)
    f.close()
