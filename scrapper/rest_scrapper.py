from scrapper_class import Scrap
import pandas as pd


class RestScrapper(Scrap):
    def __init__(self, df, func, to_cont, nums=25, render=False) -> None:
        super().__init__(df, func, to_cont, nums, render)

        self.desc = [None] * self.total_data
        self.address = [None] * self.total_data
        self.address_link = [None] * self.total_data

        self.data_df["desc"] = self.desc
        self.data_df["address"] = self.address
        self.data_df["address_link"] = self.address_link

    def get_addr(self, item):
        addr = item.find(".bottomcomment a", first=True)
        return addr.text if addr else None

    def get_addr_link(self, item):
        addr = item.find(".bottomcomment a", first=True)
        return list(addr.absolute_links)[0] if addr else None

    def get_desc(self, item):
        desc = item.find(".rdetailbox dd", first=True)
        return desc.text[:-2] if desc else None

    def get_img(self, item):
        img = item.find("img", first=True)
        return str(img.html).split('"')[1] if img else None

    def get_standard_items(self, item):
        super().get_standard_items(item)

        addr = self.get_addr(item)
        desc = self.get_desc(item)
        addr_link = self.get_addr_link(item)

        self.address[self.count] = addr
        self.address_link[self.count] = addr_link
        self.desc[self.count] = desc


if __name__ == "__main__":
    df = pd.read_csv("/home/jun/travelWeb/csv/res_amended.csv")
    rs = RestScrapper(df, "fooditem", 0, 2)
    rs.scrap_info()
