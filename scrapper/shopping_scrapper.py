import pandas as pd
from scrapper_class import Scrap


class ShoppingScrapper(Scrap):
    def __init__(self, df, func, to_cont=0, nums=25, render=False) -> None:
        super().__init__(df, func, to_cont, nums, render)
        self.ranks = [None] * self.total_data
        self.scores = [None] * self.total_data
        self.address = [None] * self.total_data

        self.data_df["scores"] = self.scores
        self.data_df["address"] = self.address
        self.data_df["ranks"] = self.ranks
        self.rank_count = 1

    def page_loop(self, session, next_page, r, p, i):
        super().page_loop(session, next_page, r, p, i)
        # reset the rank count to 1 for after every city/province is visited
        self.rank_count = 1

    def get_img(self, item):
        img = item.find("a img", first=True)
        return str(img.html).split('"')[1] if img else None

    def get_score(self, item):
        score = item.find(".score", first=True)
        score = score.find("strong", first=True)
        return score.text if score else None

    def get_addr(self, item):
        addr = item.find("dl .ellipsis", first=True)
        return addr.text if addr else None

    def get_standard_items(self, item):
        super().get_standard_items(item)

        score = self.get_score(item)
        addr = self.get_addr(item)

        self.scores[self.count] = score
        self.address[self.count] = addr
        self.ranks[self.count] = self.rank_count
        self.rank_count += 1


if __name__ == "__main__":
    df = pd.read_csv("/home/jun/travelWeb/csv/shop_amended.csv")
    ss = ShoppingScrapper(df, "shoppinglist", 56, 3, True)
    ss.scrap_info()
