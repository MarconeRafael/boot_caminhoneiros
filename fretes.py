import pandas as pd

def carregar_fretes(caminho_arquivo="data/xls/fretes.xlsx"):
    try:
        # Usando openpyxl para ler arquivos .xlsx
        fretes_df = pd.read_excel(caminho_arquivo, engine="openpyxl")
        
        # Limpeza e formatação da coluna 'Preço'
        fretes_df['Preço'] = fretes_df['Preço'].astype(str)                           # Garante que tudo seja string
        fretes_df['Preço'] = fretes_df['Preço'].str.replace('R$', '', regex=True)    # Remove 'R$'
        fretes_df['Preço'] = fretes_df['Preço'].str.replace(' ', '', regex=False)     # Remove espaços
        fretes_df['Preço'] = fretes_df['Preço'].str.replace('.', '', regex=False)     # Remove pontos (separadores de milhar)
        fretes_df['Preço'] = fretes_df['Preço'].str.replace(',', '.', regex=False)    # Substitui vírgulas por pontos
        
        # Converte para float; se não for possível, vira NaN
        fretes_df['Preço'] = pd.to_numeric(fretes_df['Preço'], errors='coerce')
        
        # Criando um dicionário com chave (origem, destino) → Preço
        fretes_dict = {}
        for _, row in fretes_df.iterrows():
            origem = row['Origem']
            destino = row['Destino']
            preco = row['Preço']
            if pd.isna(preco):
                fretes_dict[(origem, destino)] = "Preço não especificado"
            else:
                fretes_dict[(origem, destino)] = f"R${preco:.2f}"
        
        # Lista formatada para visualização (incluindo origem e destino)
        lista_fretes_str = "\n".join(
            f"{origem} para {destino} por: {preco}" 
            for (origem, destino), preco in fretes_dict.items()
        )

        return fretes_df, fretes_dict, lista_fretes_str

    except Exception as e:
        print(f"Erro ao ler a lista de fretes: {e}")
        return None, None, None

# Se executado diretamente, imprime a lista de fretes
if __name__ == "__main__":
    _, _, lista_fretes = carregar_fretes()
    if lista_fretes:
        print("Lista de fretes:")
        print(lista_fretes)
