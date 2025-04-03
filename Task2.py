import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Настройки графиков
sns.set(style="whitegrid")
plt.rcParams['font.family'] = 'DejaVu Sans'  # Поддержка эмодзи

# Создаем папку для сохранения графиков
output_folder = "charts"
os.makedirs(output_folder, exist_ok=True)

print('♦♦♦♦♦♦♦♦♦♦ - Динамика продаж по продуктам ♦♦♦♦♦♦♦♦♦♦')

# Загружаем датасеты
print("💾 Загружаем датасеты...")
OUTLETS = pd.read_csv('outlets.csv', delimiter=';', dtype=str)

SELLOUT = pd.read_csv('SELLOUT_TIME.csv', delimiter=';', dtype=str,
                      names=['product_id', 'outlet_id', 'org_name', 'quantity', 'sell_date'], header=0)

PRODUCTS = pd.read_csv('Products.csv', delimiter=',', dtype=str,
                       names=['index', 'product_id', 'product_name', 'subsegment', 'brand'], header=0)

# Удаляем колонку 'index', если она есть
if 'index' in PRODUCTS.columns:
    PRODUCTS.drop(columns=['index'], inplace=True)

# Приводим product_id в PRODUCTS к строке и убираем `.0`
PRODUCTS['product_id'] = PRODUCTS['product_id'].str.replace(r'\.0$', '', regex=True)

# Приводим quantity к числу
SELLOUT['quantity'] = pd.to_numeric(SELLOUT['quantity'], errors='coerce').fillna(0).astype(int)

# Проверяем совпадения перед merge
print("🔍 Проверка product_id:")
print("Примеры из SELLOUT:", SELLOUT['product_id'].unique()[:5])
print("Примеры из PRODUCTS:", PRODUCTS['product_id'].unique()[:5])

# Объединяем продажи с продуктами
product_sales = SELLOUT.groupby('product_id')['quantity'].sum().reset_index()
product_sales = product_sales.merge(PRODUCTS, on='product_id', how='left')

# Проверяем количество NaN после merge
print("🛠️ NaN после merge:", product_sales.isna().sum())

# Заменяем NaN
product_sales['product_name'].fillna('Неизвестный продукт', inplace=True)
product_sales['brand'].fillna('Неизвестный бренд', inplace=True)

# Топ-10 самых продаваемых продуктов
top_products = product_sales.sort_values(by='quantity', ascending=False).head(10)
print("🔥 ТОП-10 ПРОДУКТОВ:", top_products)

# Топ-10 наименее продаваемых продуктов
low_products = product_sales.sort_values(by='quantity', ascending=True).head(10)

# Группируем продажи по брендам
brand_sales = product_sales.groupby('brand')['quantity'].sum().reset_index().sort_values(by='quantity', ascending=False)

# Функция для сохранения графиков
def save_and_show_plot(filename):
    plt.savefig(os.path.join(output_folder, filename), dpi=300)
    print(f"📊 График сохранен: {filename}")
    plt.show()

# Визуализация самых продаваемых товаров
plt.figure(figsize=(12, 6))
sns.barplot(data=top_products, x='quantity', y='product_name', palette='viridis')
plt.xlabel('Количество продаж')
plt.ylabel('Продукт')
plt.title('ТОП-10 самых продаваемых товаров')
plt.gca().invert_yaxis()
save_and_show_plot("top_10_products.png")

# Визуализация наименее продаваемых товаров
plt.figure(figsize=(12, 6))
sns.barplot(data=low_products, x='quantity', y='product_name', palette='coolwarm')
plt.xlabel('Количество продаж')
plt.ylabel('Продукт')
plt.title('ТОП-10 наименее продаваемых товаров')
plt.gca().invert_yaxis()
save_and_show_plot("low_10_products.png")

# Визуализация продаж по брендам
plt.figure(figsize=(12, 6))
sns.barplot(data=brand_sales.head(10), x='quantity', y='brand', palette='magma')
plt.xlabel('Количество продаж')
plt.ylabel('Бренд')
plt.title('ТОП-10 самых продаваемых брендов')
plt.gca().invert_yaxis()
save_and_show_plot("top_10_brands.png")
