import os
import pandas as pd

# Caminho do arquivo de entrada (Excel) e do arquivo de saída (Excel)
xls_dir = 'data/xls'
xls_file_path = os.path.join(xls_dir, 'fretes.xls')
xlsx_file_path = os.path.join(xls_dir, 'fretes.xlsx')

# Verifica se o arquivo .xls existe
if not os.path.exists(xls_file_path):
    raise FileNotFoundError(f"Arquivo .xls não encontrado: {xls_file_path}")

try:
    # Lê o arquivo .xls usando pandas com o motor 'xlrd'
    print(f"Convertendo arquivo .xls para .xlsx: {xls_file_path}")
    df = pd.read_excel(xls_file_path, engine='xlrd')

    # Salva o arquivo como .xlsx
    df.to_excel(xlsx_file_path, index=False)
    print(f"Arquivo convertido para .xlsx: {xlsx_file_path}")

except Exception as e:
    print(f"Erro ao processar o arquivo .xls para .xlsx: {e}")
