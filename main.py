import pandas as pd
import numpy as np

# Загружаем датасет outlets
print("💾 Загружаем датасет outlets...")
OUTLETS = pd.read_csv('outlets.csv', delimiter=';')

# Загружаем датасет sellout
print("💾 Загружаем датасет sellout...")
SELLOUT = pd.read_csv('sellout.csv', delimiter=';')

# Загружаем датасет Products
print("💾 Загружаем датасет Products...")
PRODUCTS = pd.read_excel('Products.xlsx')

# Преобразуем xlsx в csv
print("💾 Преобразую Excel в CSV...")
PRODUCTS.to_csv("PRODUCTS.csv")

# Проверяем работу данных
print('♦ Открываю OUTLETS...')
print(OUTLETS.head())
print('♦ Открываю SELLOUT...')
print(SELLOUT.head())
print('♦ Открываю PRODUCTS...')
print(PRODUCTS.head())