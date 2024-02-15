import pandas as pd
from requests_html import HTMLSession, user_agent
import random
import time


class SightDetailedScrapper:
    def __init__(self, df, to_cont=0, render=False) -> None:
        self.df = df
        self.render = render
        self.to_cont = to_cont
        self.nums = 10
        self.names = [None] * self.nums
        self.addresses = [None] * self.nums
        self.times = [None] * self.nums
        self.teles = [None] * self.nums
        self.places = [None] * self.nums
        self.descs = [None] * self.nums
        self.titles = [None] * self.nums
        self.imgs = [None] * self.nums
        self.count = 0

        self.text_data = {
            "names": self.names,
            "places": self.places,
            "addresses": self.addresses,
            "times": self.times,
            "teles": self.teles,
            "titles": self.titles,
            "descs": self.descs,
        }
        self.img_data = {
            "names": self.names,
            "places": self.places,
            "imgs": self.imgs,
        }

    def scrap(self):
        remaining = False
        for i in range(self.to_cont, len(self.df)):
            session = HTMLSession()
            remaining = True
            ua = self.assign_ua()

            name, place, link = self.df.names[i], self.df.places[i], self.df.links[i]
            print()
            print("------------------City break---------------------")
            print(name, place, i)
            self.slp(1, 15)
            r = session.get(link, headers=ua)

            if self.render:
                r.html.render()

            r = self.verify_check(r, i)

            self.names[self.count] = name
            self.places[self.count] = place

            self.add_info(r, i)
            self.add_imgs(r, i)
            self.count += 1

            if self.count == self.nums:
                self.data_to_csv(i)
                remaining = False
                self.count = 0

        if remaining:
            self.data_to_csv(i)

    def data_to_csv(self, i):
        self.add_csv("sight_detailed_info", self.text_data, i)
        self.add_csv("sight_imgs_info", self.img_data, i)

    def assign_ua(self):
        ua = user_agent("chrome")
        return {"User-Agent": ua}

    def add_csv(self, name, data, i):
        pd.DataFrame(data).to_csv(f"../csv/temp/{name}_{i}.csv", index=False)
        print("Added new csv")

    def add_info(self, r, i):
        print("First round of verification check for basic info")
        r = self.verify_check(r, i)
        print("getting text info...")
        basic_info = r.html.find(".baseInfoModule .baseInfoText")
        if basic_info:
            print("collecting basic info...")
            print(basic_info[0].text)

            address = self.get_address(basic_info)
            time = self.get_time(basic_info)
            tele = self.get_tele(basic_info)

            self.addresses[self.count] = address
            self.times[self.count] = time
            self.teles[self.count] = tele
        else:
            input("Check what is going on:")

        print("Second round of verification check for detailed info")
        detailed_info = r.html.find(".normalModule", first=True)
        if detailed_info:
            print("collection detailed info...")
            desc, title = self.get_desc(detailed_info)

            self.descs[self.count] = desc
            self.titles[self.count] = title
        print()

    def add_imgs(self, r, i):
        print("Third round of verification check for img info")
        r = self.verify_check(r, i)
        img_info = r.html.find(".totalCont a", first=True)
        img_link = list(img_info.absolute_links)[0] if img_info else None
        print(f"img link:{img_link}") if img_link else None

        if img_link:
            self.slp(1, 5)
            print("getting imgs...")
            session = HTMLSession()
            ua = self.assign_ua()

            r = session.get(img_link, headers=ua)
            print("Last round of verification check for img info")
            r = self.verify_check(r, same=img_link)
            img_list = r.html.find(".photolist .itempic img")

            img_temp = []
            for x in range(10):
                try:
                    img = str(img_list[x].html).split('"')[1]
                    img_temp.append(img)
                except:
                    pass

            print(f"Total imgs:{len(img_temp)}")
            self.imgs[self.count] = "->".join(img_temp)
        else:
            self.imgs[self.count] = None

    def get_desc(self, detailed_info):
        desc_temp, titles_temp = [], []
        if detailed_info:
            desc = detailed_info.find(".moduleContent")
            titles = detailed_info.find(".moduleTitle")

            for i in range(len(titles)):
                titles_temp.append(titles[i].text)
            for i in range(len(desc)):
                desc_temp.append(desc[i].text)

            print(f"title length:{len(titles_temp)} desc length:{len(desc_temp)}")
            return "->".join(desc_temp), "->".join(titles_temp)

        return None, None

    def get_address(self, basic_info):
        if len(basic_info) < 1:
            return None
        addr = basic_info[0]
        return addr.text if addr else None

    def get_time(self, basic_info):
        if len(basic_info) < 2:
            return None
        time = basic_info[1]
        try:
            time = str(time.text).split("；")[1] if time else None
        except:
            time = None
        return time

    def get_tele(self, basic_info):
        if len(basic_info) < 3:
            return None
        try:
            tele = basic_info[2]
        except:
            tele = None
        return tele.text if tele else None

    def slp(self, low=1, high=15):
        slp = random.randint(low, high)
        print(f"waiting for {slp} secs")
        time.sleep(0)

    def verify_check(self, r, i=False, same=False):
        print(f"Verify pre-check: {r.html}")
        if "verify" in str(r.html):
            print(r.html)
            input("NEED TO VERIFY TO CONTINUE")
            session = HTMLSession()
            ua = self.assign_ua()
            if same:
                r = session.get(same, headers=ua)
            else:
                r = session.get(self.df.links[i], headers=ua)
            print("verified!")

        return r


if __name__ == "__main__":
    df = pd.read_csv("../csv/sight_all_amended.csv")
    sds = SightDetailedScrapper(df, 7540)
    sds.scrap()
