import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import calendar
import seaborn as sns
import os

print('♦♦♦♦♦♦♦♦♦♦ ДИНАМИКА ПРОДАЖ ПО ПЕРИОДАМ ♦♦♦♦♦♦♦♦♦♦')

# Создаем папку для сохранения графиков
output_folder = "charts"
os.makedirs(output_folder, exist_ok=True)

# Загружаем датасеты
print("💾 Загружаем датасеты...")
OUTLETS = pd.read_csv('outlets.csv', delimiter=';', dtype=str)
SELLOUT = pd.read_csv('SELLOUT_TIME.csv', delimiter=';', dtype=str)
PRODUCTS = pd.read_csv('Products.csv', delimiter=',', dtype=str, names=['index', 'product_id', 'product_name', 'subsegment', 'brand'], header=0)

# Удаляем колонку 'index'
if 'index' in PRODUCTS.columns:
    PRODUCTS.drop(columns=['index'], inplace=True)

# Приводим product_id в PRODUCTS к строке (убираем .0)
PRODUCTS['product_id'] = PRODUCTS['product_id'].str.replace(r'\.0$', '', regex=True)

# Приводим sell_date к формату даты
SELLOUT['sell_date'] = pd.to_datetime(SELLOUT['sell_date'], format='%Y-%m-%d')

# Добавляем колонку с месяцем
SELLOUT['month'] = SELLOUT['sell_date'].dt.month

# Приводим cnt к числу
SELLOUT['cnt'] = pd.to_numeric(SELLOUT['cnt'], errors='coerce').fillna(0).astype(int)

# 🔗 Объединяем SELLOUT и PRODUCTS
SELLOUT = SELLOUT.merge(PRODUCTS, on='product_id', how='left')

# Заменяем NaN
SELLOUT['product_name'].fillna('Неизвестный продукт', inplace=True)
SELLOUT['brand'].fillna('Неизвестный бренд', inplace=True)

# 📊 Агрегируем продажи по месяцам
monthly_sales = SELLOUT.groupby('month')['cnt'].sum().reset_index()
monthly_sales['month'] = monthly_sales['month'].apply(lambda x: calendar.month_abbr[x])

# 🔥 График динамики продаж по месяцам
plt.figure(figsize=(12, 5))
sns.lineplot(x=monthly_sales['month'], y=monthly_sales['cnt'], marker='o')
plt.xlabel('Месяц')
plt.ylabel('Продажи')
plt.title('Динамика продаж по месяцам')
plt.xticks(rotation=45)
plt.grid()
plt.savefig(os.path.join(output_folder, "monthly_sales.png"))
plt.show()

# 🔥 Анализ сезонности по продуктам (группируем по `product_name`)
product_sales = SELLOUT.groupby(['product_name', 'month'])['cnt'].sum().unstack().fillna(0)

# 🔥 ТОП-10 продуктов с самыми пиковыми продажами
top_products = product_sales.sum(axis=1).nlargest(10).index

# 📊 Графики сезонности для топ-10 продуктов
fig, axes = plt.subplots(nrows=5, ncols=2, figsize=(12, 12))
axes = axes.flatten()
colors = sns.color_palette("husl", len(top_products))

for i, (product, color) in enumerate(zip(top_products, colors)):
    axes[i].plot(product_sales.columns, product_sales.loc[product], marker='o', linestyle='-', color=color)
    axes[i].set_title(f'{product}')
    axes[i].set_xlabel('Месяц')
    axes[i].set_ylabel('Продажи')
    axes[i].grid()
    axes[i].set_xticks(product_sales.columns)
    axes[i].set_xticklabels([calendar.month_abbr[m] for m in product_sales.columns], rotation=45)

plt.tight_layout()
plt.savefig(os.path.join(output_folder, "top_10_products_seasonality.png"))
plt.show()

# 🔥 Разделяем графики сезонности на группы по 10 продуктов
num_products = len(product_sales)
products_per_plot = 10
num_plots = int(np.ceil(num_products / products_per_plot))
colors = sns.color_palette("husl", products_per_plot)

for i in range(num_plots):
    subset = product_sales.iloc[i * products_per_plot:(i + 1) * products_per_plot]
    num_subplots = len(subset)
    rows = (num_subplots // 2) + (num_subplots % 2)
    fig, axes = plt.subplots(nrows=rows, ncols=2, figsize=(12, rows * 3))
    axes = axes.flatten()

    for j, (product, color) in enumerate(zip(subset.index, colors[:num_subplots])):
        axes[j].plot(subset.columns, subset.loc[product], marker='o', linestyle='-', color=color)
        axes[j].set_title(f'{product}')
        axes[j].set_xlabel('Месяц')
        axes[j].set_ylabel('Продажи')
        axes[j].grid()
        axes[j].set_xticks(subset.columns)
        axes[j].set_xticklabels([calendar.month_abbr[m] for m in subset.columns], rotation=45)

    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, f"products_seasonality_part_{i + 1}.png"))
    plt.show()
