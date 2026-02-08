import pandas as pd
import sqlite3
import os

def run_import(csv_file='sales.csv'):
    print("Starting")

    if not os.path.exists(csv_file):
         print("Err csv") 
         return

    try:
        df = pd.read_csv(csv_file, sep=';', encoding='cp1251')

        if df.empty:
             print("empty")
             return
        
        conn = sqlite3.connect('grt.db')
        cursor = conn.cursor()

        for index, row in df.iterrows():

            cursor.execute("""INSERT OR IGNORE INTO Товары (ID, Название, Описание, Цена, Количество) VALUES (?, ?, ?, ?, ?)""", 
                           (row['product_id'], f"Товар {row['product_id']}", f"Autoimport", round(row['total_price'] / row['quantity'],2), 100))
            cursor.execute("""INSERT INTO Продажи (ID_Аппарата, ID_товара, Количество, Сумма_продажи, Дата, Метод_оплаты) VALUES (?, ?, ?, ?, ?, ?)""", 
                           (1, row['product_id'], row['quantity'], row['total_price'], row['timestamp'], row['payment_method']))
        conn.commit()
        print("Import done")

    except Exception as e:
            print("Error")
            if conn:
                conn.rollback()
    finally:
         if conn:
            conn.close()

run_import()