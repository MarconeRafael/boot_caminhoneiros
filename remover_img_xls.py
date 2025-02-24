from openpyxl import Workbook
import xlrd
import os
import openpyxl
import zipfile

file_path = 'data/caminhao/Fretes 21-02-2025 13_50.xlsx'

def check_if_valid_xlsx(file_path):
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.testzip()  # Verifica se o arquivo ZIP está intacto
        print(f"O arquivo {file_path} é um arquivo .xlsx válido.")
    except zipfile.BadZipFile:
        print(f"O arquivo {file_path} não é um arquivo .xlsx válido.")
    except Exception as e:
        print(f"Erro ao verificar o arquivo: {e}")

# Testa se o arquivo é válido
check_if_valid_xlsx(file_path)

def remove_images_from_xlsx(file_path):
    try:
        workbook = openpyxl.load_workbook(file_path)
        
        for sheet in workbook.sheetnames:
            worksheet = workbook[sheet]
            
            # Verifica se há imagens na planilha
            if hasattr(worksheet, '_images') and worksheet._images:
                for image in list(worksheet._images):
                    worksheet._images.remove(image)
                print(f"Imagens removidas da planilha: {sheet}")
            else:
                print(f"Nenhuma imagem encontrada na planilha: {sheet}")
        
        workbook.save(file_path)
        print(f"Imagens removidas do arquivo: {file_path}")
    except Exception as e:
        print(f"Erro ao remover imagens: {e}")


# Verifica se o arquivo .xlsx foi criado antes de prosseguir

remove_images_from_xlsx(file_path)