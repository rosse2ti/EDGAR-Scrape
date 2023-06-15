# import our libraries
import json
import requests
import pandas as pd


class GetFundamentals:
    def __init__(self, ticker="AAPL", steps=2) -> None:
        self.ticker = ticker
        self.steps = steps
        self.headers = {"User-Agent": f"your website your email"}
        pass

    def get_cik(self):
        symbol_to_cik = requests.get(
            "https://www.sec.gov/files/company_tickers.json", headers=self.headers
        ).json()

        cik_lookup = dict(
            [(val["ticker"], val["cik_str"]) for key, val in symbol_to_cik.items()]
        )
        cik = cik_lookup[self.ticker]
        return cik

    def get_submissions(self, cik):
        submissions = requests.get(
            f"https://data.sec.gov/submissions/CIK{cik:0>10}.json", headers=self.headers
        ).json()

        return submissions

    def get_company_facts(self, submissions, cik):
        recents = pd.DataFrame(submissions["filings"]["recent"])
        recents.head()
        recents["reportDate"] = pd.to_datetime(recents["reportDate"])
        recents["filingDate"] = pd.to_datetime(recents["filingDate"])
        insider_q1 = recents[(recents["form"] == "10-Q") | (recents["form"] == "10-K")]

        date = list(insider_q1["reportDate"])[self.steps]
        date = date.strftime("%Y-%m-%d")

        edgar_filings = requests.get(
            f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:0>10}.json",
            headers=self.headers,
        ).json()
        edgar_filings = edgar_filings["facts"]["us-gaap"]
        return [edgar_filings, date]

    def parse_instance(self, edgar_filings, date):
        with open("fundamentals/table_schema/statement_schema.json", "r") as f:
            schema = json.load(f)

        section = {}
        section["info"] = {}
        section["info"]["ticker"] = self.ticker
        section["info"]["date"] = date

        for statement in schema:
            section[statement["section"]] = {}

            for object in statement["data"]:
                for item in object["items"]:
                    if item["role"] == "category":
                        section[statement["section"]][item["id"]] = {}
                        for item_o in item["data"]:
                            if item_o["id"] in edgar_filings:
                                id_o = edgar_filings[item_o["id"]]["label"]
                                unit_o = edgar_filings[item_o["id"]]["units"].keys()

                                find_o = [
                                    i
                                    for i in edgar_filings[item_o["id"]]["units"][
                                        list(unit_o)[0]
                                    ]
                                    if i["end"] == date
                                ]
                                if find_o:
                                    section[statement["section"]][item["id"]][
                                        id_o
                                    ] = find_o[-1]["val"]

                    elif item["role"] == "fact":
                        if item["id"] in edgar_filings:
                            id = edgar_filings[item["id"]]["label"]
                            unit = edgar_filings[item["id"]]["units"].keys()
                            find = [
                                i
                                for i in edgar_filings[item["id"]]["units"][
                                    list(unit)[0]
                                ]
                                if i["end"] == date
                            ]
                            if find:
                                section[statement["section"]][id] = find[-1]["val"]

                if "total" in object:
                    if object["total"]["id"] in edgar_filings:
                        id_t = edgar_filings[object["total"]["id"]]["label"]
                        unit_t = edgar_filings[object["total"]["id"]]["units"].keys()
                        find_t = [
                            i
                            for i in edgar_filings[object["total"]["id"]]["units"][
                                list(unit_t)[0]
                            ]
                        ]
                        if find_t:
                            section[statement["section"]]["Total " + id_t] = find_t[-1][
                                "val"
                            ]

        with open(
            ("fundamentals/json_cache/{}_{}.json").format(self.ticker, date),
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(section, f)
            f.close()
        return section
