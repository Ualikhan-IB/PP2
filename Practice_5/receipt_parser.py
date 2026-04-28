import re
import json
from datetime import datetime

def parse_receipt(filename):
    # Open and read the receipt file with UTF-8 encoding
    with open(filename, 'r', encoding='utf-8') as file:
        text = file.read()
    
    # Initialize the main data structure for storing all parsed information
    receipt_data = {
        'store_info': {},
        'products': [],
        'total': 0.0,
        'payment': {},
        'date_time': {},
        'fiscal_data': {}
    }
    
    print("=" * 60)
    print("ПАРСИНГ ЧЕКА")
    print("=" * 60)
    
    # 1. Extract store information
    print("\n--- ИНФОРМАЦИЯ О МАГАЗИНЕ ---")
    
    # Search for company name after "Филиал" (Branch)
    company_match = re.search(r'Филиал\s+(.+)', text)
    if company_match:
        receipt_data['store_info']['company'] = company_match.group(1).strip() #delete whitespaces
        print(f"Компания: {receipt_data['store_info']['company']}")
    
    # Search for BIN (Business Identification Number)
    bin_match = re.search(r'БИН\s+(\d+)', text)
    if bin_match:
        receipt_data['store_info']['bin'] = bin_match.group(1)
        print(f"БИН: {receipt_data['store_info']['bin']}")
    
    # Search for address starting with "г." (city)
    address_match = re.search(r'г\.\s*([^\n]+)', text) #except begining of the string
    if address_match:
        receipt_data['store_info']['address'] = address_match.group(1).strip()
        print(f"Адрес: {receipt_data['store_info']['address']}")
    
    # 2. Extract product information
    print("\n--- ТОВАРЫ ---")
    
    # Regex pattern for product lines:
    # (\d+)\. - captures product number (1., 2., etc.)
    # \s*([^\n]+?) - captures product name (non-greedy)
    # \s*(\d+[,\d]*) - captures quantity (handles numbers with commas)
    # \s*x\s* - matches the "x" separator
    # \s*(\d+[,\d]*) - captures unit price
    # \s*(\d+[,\d]*) - captures total price
    product_pattern = r'(\d+)\.\s*([^\n]+?)\s*(\d+[,\d]*)\s*x\s*(\d+[,\d]*)\s*(\d+[,\d]*)'
    
    # Find all products matching the pattern
    products = re.findall(product_pattern, text)
    
    total_sum = 0.0
    # Iterate through all found products
    for i, (num, name, quantity, price, cost) in enumerate(products, 1): #index and element starting from 1
        # Clean number formats: remove spaces, replace comma with dot for float conversion
        quantity_num = float(quantity.replace(',', '.').replace(' ', ''))
        price_num = float(price.replace(',', '.').replace(' ', ''))
        cost_num = float(cost.replace(',', '.').replace(' ', ''))
        
        # Create product object with all details
        product = {
            'number': int(num),
            'name': name.strip(),
            'quantity': quantity_num,
            'unit_price': price_num,
            'total_price': cost_num
        }
        
        # Add product to the list
        receipt_data['products'].append(product)
        total_sum += cost_num
        
        # Display product information
        print(f"{i:2d}. {name[:40]:40} {quantity:>6} x {price:>8} = {cost:>10}")
    
    # 3. Extract total amount
    print("\n--- ИТОГОВАЯ СУММА ---")
    
    # Search for "ИТОГО:" (TOTAL:) followed by amount
    total_match = re.search(r'ИТОГО:\s*(\d+[,\d]*)', text)
    if total_match:
        total_str = total_match.group(1).replace(' ', '').replace(',', '.')
        receipt_data['total'] = float(total_str)
        print(f"Итого по чеку: {receipt_data['total']:.2f}")
        print(f"Сумма по товарам: {total_sum:.2f}")
    
    # 4. Extract VAT (НДС)
    vat_match = re.search(r'НДС\s*\d+%:\s*(\d+[,\d]*)', text)
    if vat_match:
        vat_str = vat_match.group(1).replace(' ', '').replace(',', '.')
        receipt_data['vat'] = float(vat_str)
        print(f"НДС: {receipt_data['vat']:.2f}")
    
    # 5. Extract payment information
    print("\n--- ОПЛАТА ---")
    
    # Search for payment method (card/cash) and amount
    payment_match = re.search(r'(Банковская карта|Наличные|Карта):\s*(\d+[,\d]*)', text)
    if payment_match:
        receipt_data['payment']['method'] = payment_match.group(1)
        payment_str = payment_match.group(2).replace(' ', '').replace(',', '.')
        receipt_data['payment']['amount'] = float(payment_str)
        print(f"Метод: {receipt_data['payment']['method']}")
        print(f"Сумма: {receipt_data['payment']['amount']:.2f}")
    
    # 6. Extract date and time
    print("\n--- ДАТА И ВРЕМЯ ---")
    
    # Search for followed by DD.MM.YYYY HH:MM:SS format
    datetime_match = re.search(r'Время:\s*(\d{2})\.(\d{2})\.(\d{4})\s+(\d{2}):(\d{2}):(\d{2})', text)
    if datetime_match:
        day, month, year, hour, minute, second = datetime_match.groups()
        receipt_data['date_time'] = {
            'date': f"{day}.{month}.{year}",
            'time': f"{hour}:{minute}:{second}",
            'datetime': f"{year}-{month}-{day} {hour}:{minute}:{second}"
        }
        print(f"Дата: {receipt_data['date_time']['date']}")
        print(f"Время: {receipt_data['date_time']['time']}")
    
    # 7. Extract fiscal data
    print("\n--- ФИСКАЛЬНЫЕ ДАННЫЕ ---")
    
    # Search for receipt number
    receipt_num_match = re.search(r'Чек\s*№(\d+)', text)
    if receipt_num_match:
        receipt_data['fiscal_data']['receipt_number'] = receipt_num_match.group(1)
        print(f"Номер чека: {receipt_data['fiscal_data']['receipt_number']}")
    
    # Search for fiscal signature
    fiscal_match = re.search(r'Фискальный признак:\s*(\d+)', text)
    if fiscal_match:
        receipt_data['fiscal_data']['fiscal_sign'] = fiscal_match.group(1)
        print(f"Фискальный признак: {receipt_data['fiscal_data']['fiscal_sign']}")
    
    # Search for RNM (Registration Number)
    rnm_match = re.search(r'Код ККМ КГД \(РНМ\):\s*(\d+)', text)
    if rnm_match:
        receipt_data['fiscal_data']['rnm'] = rnm_match.group(1)
        print(f"РНМ: {receipt_data['fiscal_data']['rnm']}")
    
    # Search for ZNM (Factory Number)
    znm_match = re.search(r'ЗНМ:\s*(\w+)', text)
    if znm_match:
        receipt_data['fiscal_data']['znm'] = znm_match.group(1)
        print(f"ЗНМ: {receipt_data['fiscal_data']['znm']}")
    
    return receipt_data

def save_as_json(data, filename='receipt.json'):
    # Save the parsed data to a JSON file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n Данные сохранены в {filename}")

def print_pretty_receipt(data):
    """Display formatted receipt in console"""
    
    print("\n" + "=" * 60)
    print(" " * 20 + "ФИСКАЛЬНЫЙ ЧЕК")
    print("=" * 60)
    
    # Display store header information
    if 'company' in data['store_info']:
        print(f"\n{data['store_info']['company']:^60}")
    if 'bin' in data['store_info']:
        print(f"БИН: {data['store_info']['bin']:>54}")
    if 'address' in data['store_info']:
        print(f"{data['store_info']['address']:^60}")
    
    # Products table header
    print("\n" + "-" * 60)
    print(f"{'№':3} {'НАИМЕНОВАНИЕ':<35} {'КОЛ-ВО':>8} {'ЦЕНА':>8} {'СУММА':>8}")
    print("-" * 60)
    
    # List all products
    for i, product in enumerate(data['products'], 1):
        name = product['name'][:35]  # shortened long names
        print(f"{i:3} {name:<35} {product['quantity']:8.2f} {product['unit_price']:8.2f} {product['total_price']:8.2f}")
    
    print("-" * 60)
    
    # Display total amount
    print(f"\n{'ИТОГО:':>48} {data['total']:>10.2f}")
    
    # Display VAT if present
    if 'vat' in data:
        print(f"{'в т.ч. НДС:':>48} {data['vat']:>10.2f}")
    
    # Display payment information
    if data['payment']:
        print(f"\n{data['payment']['method'] + ':':>48} {data['payment']['amount']:>10.2f}")
    
    # Display date and time
    if data['date_time']:
        print(f"\n{'Время:':>48} {data['date_time']['date']} {data['date_time']['time']}")
    
    # Display fiscal signature
    if 'fiscal_sign' in data['fiscal_data']:
        print(f"\n{'Фискальный признак:':>48} {data['fiscal_data']['fiscal_sign']}")
    
    print("=" * 60)

# Main program entry point
if __name__ == "__main__":
    # Parse the receipt file
    result = parse_receipt('raw.txt')
    
    # Display formatted receipt
    print_pretty_receipt(result)
    
    # Save to JSON file
    save_as_json(result)
    
    # Calculate and display additional statistics
    print("\n СТАТИСТИКА:")
    print(f"   Всего товаров: {len(result['products'])}")
    
    # Find the most expensive product
    if result['products']:
        most_expensive = max(result['products'], key=lambda x: x['unit_price'])
        print(f"   Самый дорогой товар: {most_expensive['name'][:30]}... ({most_expensive['unit_price']:.2f} ₸)")
        
        # Count prescription products (marked with [RX])
        rx_products = [p for p in result['products'] if '[RX]' in p['name']]
        print(f"   Рецептурных товаров: {len(rx_products)}")