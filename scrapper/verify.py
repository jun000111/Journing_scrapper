import pandas as pd


cnl = pd.read_csv('/home/jun/travelWeb/csv/cities_n_links.csv')
all = pd.read_csv('/home/jun/travelWeb/csv/shop_all.csv')

print(len(cnl.city.unique()))
print(len(all.places.unique()))