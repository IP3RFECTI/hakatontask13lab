import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import calendar
import seaborn as sns
print('♦♦♦♦♦♦♦♦♦♦ РЕШЕНИЕ ЗАДАЧИ Динамика продаж по периодам ♦♦♦♦♦♦♦♦♦♦  \n ♦♦♦♦♦♦♦♦♦♦  (выявить самые пиковые месяцы продаж, '
      '♦♦♦♦♦♦♦♦♦♦ определить сезонность по продуктам) ♦♦♦♦♦♦♦♦♦♦')

# Загружаем датасет outlets
print("💾 Загружаем датасет outlets...")
OUTLETS = pd.read_csv('outlets.csv', delimiter=';')

# Загружаем датасет sellout
print("💾 Загружаем датасет sellout...")
SELLOUT = pd.read_csv('SELLOUT_TIME.csv', delimiter=';')

# Загружаем датасет Products
print("💾 Загружаем датасет Products...")
PRODUCTS = pd.read_csv('Products.csv')

# Приводим sell_date к формату даты
SELLOUT['sell_date'] = pd.to_datetime(SELLOUT['sell_date'], format='%Y-%m-%d')

# Добавляем колонку с месяцем
SELLOUT['month'] = SELLOUT['sell_date'].dt.month

# Агрегируем продажи по месяцам
monthly_sales = SELLOUT.groupby('month')['cnt'].sum().reset_index()

# Преобразуем номера месяцев в названия
monthly_sales['month'] = monthly_sales['month'].apply(lambda x: calendar.month_abbr[x])

# Строим график динамики
plt.figure(figsize=(12, 5))
sns.lineplot(x=monthly_sales['month'], y=monthly_sales['cnt'], marker='o')
plt.xlabel('Месяц')
plt.ylabel('Продажи')
plt.title('Динамика продаж по месяцам')
plt.xticks(rotation=45)
plt.grid()
plt.savefig("monthly_sales.png")
plt.show()

# Анализ сезонности по продуктам
product_sales = SELLOUT.groupby(['product_id', 'month'])['cnt'].sum().unstack().fillna(0)

# Продукты с самыми пиковыми продажами
top_products = product_sales.sum(axis=1).nlargest(10).index

# Разделяем графики сезонности на субплоты для топ-10 продуктов
fig, axes = plt.subplots(nrows=5, ncols=2, figsize=(12, 12))
axes = axes.flatten()
colors = sns.color_palette("husl", len(top_products))

for i, (product, color) in enumerate(zip(top_products, colors)):
    axes[i].plot(product_sales.columns, product_sales.loc[product], marker='o', linestyle='-', color=color)
    axes[i].set_title(f'Продукт {product}')
    axes[i].set_xlabel('Месяц')
    axes[i].set_ylabel('Продажи')
    axes[i].grid()
    axes[i].set_xticks(product_sales.columns)
    axes[i].set_xticklabels([calendar.month_abbr[m] for m in product_sales.columns], rotation=45)

plt.tight_layout()
plt.savefig("top_10_products_seasonality.png")
plt.show()

# Разделяем графики сезонности на группы по 10 продуктов
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
        axes[j].set_title(f'Продукт {product}')
        axes[j].set_xlabel('Месяц')
        axes[j].set_ylabel('Продажи')
        axes[j].grid()
        axes[j].set_xticks(subset.columns)
        axes[j].set_xticklabels([calendar.month_abbr[m] for m in subset.columns], rotation=45)

    plt.tight_layout()
    plt.savefig(f"products_seasonality_part_{i + 1}.png")
    plt.show()