import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import calendar
'''
На это у меня уже нет сил. Часть сделана, но выдает ошибки. 7 утра уже, когда я это пишу. Крч удачи
'''
print('♦♦♦♦♦♦♦♦♦♦ ДИНАМИКА ПРОДАЖ ПО КЛИЕНТАМ ♦♦♦♦♦♦♦♦♦♦')

# Создаем папку для сохранения графиков
output_folder = "charts"
os.makedirs(output_folder, exist_ok=True)

# Загружаем датасеты
print("💾 Загружаем датасеты...")
OUTLETS = pd.read_csv('outlets.csv', delimiter=';', dtype=str)
SELLOUT = pd.read_csv('SELLOUT_TIME.csv', delimiter=';', dtype=str)

# Приведение типов
print("🔄 Приведение данных к нужным типам...")
SELLOUT['sell_date'] = pd.to_datetime(SELLOUT['sell_date'], format='%Y-%m-%d', errors='coerce')
SELLOUT['cnt'] = pd.to_numeric(SELLOUT['cnt'], errors='coerce').fillna(0).astype(int)
SELLOUT['outlet_id'] = SELLOUT['outlet_id'].astype(str)
OUTLETS['outlet_id'] = OUTLETS['outlet_id'].astype(str)

# Объединение данных
print("🔗 Объединение SELLOUT и OUTLETS...")
SELLOUT = SELLOUT.merge(OUTLETS, on='outlet_id', how='left')
SELLOUT['org_name'] = SELLOUT['org_name'].fillna('Неизвестный клиент')

# Группировка продаж по клиентам
print("📊 Группировка продаж по клиентам...")
client_sales = SELLOUT.groupby('org_name')['cnt'].sum().reset_index()
client_sales = client_sales.sort_values(by='cnt', ascending=False)

# Определение сегментов
print("📏 Определение границ сегментов...")
quantiles = client_sales['cnt'].quantile([0.2, 0.8])
low_threshold, high_threshold = quantiles[0.2], quantiles[0.8]

# Функция категоризации
def categorize_client(sales):
    if sales >= high_threshold:
        return 'Top'
    elif sales <= low_threshold:
        return 'Low'
    else:
        return 'Medium'

# Добавление сегментации
client_sales['Segment'] = client_sales['cnt'].apply(categorize_client)

# Цвета сегментов
segment_colors = {'Top': 'green', 'Medium': 'orange', 'Low': 'red'}

# Динамика по месяцам
print("📅 Анализ динамики продаж по месяцам...")
SELLOUT['month'] = SELLOUT['sell_date'].dt.month
client_monthly_sales = SELLOUT.groupby(['org_name', 'month'])['cnt'].sum().unstack().fillna(0)

# Визуализация
print("📊 Визуализация данных...")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# График распределения клиентов по сегментам
sns.countplot(x=client_sales['Segment'], palette=segment_colors, order=['Top', 'Medium', 'Low'], ax=axes[0, 0])
axes[0, 0].set_title('Распределение клиентов по сегментам')
axes[0, 0].set_xlabel('Сегмент')
axes[0, 0].set_ylabel('Количество клиентов')
axes[0, 0].grid()

# ТОП-10 клиентов (цвета по сегменту)
top_clients = client_sales.head(10)
sns.barplot(y=top_clients['org_name'], x=top_clients['cnt'],
            palette=[segment_colors[s] for s in top_clients['Segment']], ax=axes[0, 1])
axes[0, 1].set_title('Топ-10 клиентов по закупкам')
axes[0, 1].set_xlabel('Объем закупок')
axes[0, 1].set_ylabel('Клиент')
axes[0, 1].grid()

# Клиенты с наименьшими закупками
low_clients = client_sales.tail(10)
sns.barplot(y=low_clients['org_name'], x=low_clients['cnt'],
            palette=[segment_colors[s] for s in low_clients['Segment']], ax=axes[1, 0])
axes[1, 0].set_title('Клиенты с наименьшими закупками')
axes[1, 0].set_xlabel('Объем закупок')
axes[1, 0].set_ylabel('Клиент')
axes[1, 0].grid()

# Динамика продаж топ-5 клиентов
print("📈 Определение топ-5 клиентов по динамике...")
top_5_clients = client_monthly_sales.sum(axis=1).nlargest(5).index
for client in top_5_clients:
    segment = client_sales.loc[client_sales['org_name'] == client, 'Segment'].values[0]
    axes[1, 1].plot(client_monthly_sales.columns, client_monthly_sales.loc[client],
                     marker='o', label=client, color=segment_colors[segment])
axes[1, 1].set_title('Динамика закупок топ-5 клиентов')
axes[1, 1].set_xlabel('Месяц')
axes[1, 1].set_ylabel('Объем закупок')
axes[1, 1].legend()
axes[1, 1].grid()
axes[1, 1].set_xticks(client_monthly_sales.columns)
axes[1, 1].set_xticklabels([calendar.month_abbr[m] for m in client_monthly_sales.columns], rotation=45)

plt.tight_layout()
plt.savefig(os.path.join(output_folder, "client_analysis.png"))
plt.show()

print('✅ Анализ завершен! Все графики сохранены в папку charts/')
