import os
import time
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from keys import email_, senha_

# Função para verificar se o arquivo foi baixado
def is_downloaded(filename="fretes.xls", timeout=5):
    download_dir = os.path.abspath("./data")
    start_time = time.time()
    while time.time() - start_time < timeout:
        # Verifica se algum arquivo está presente no diretório de download
        files = os.listdir(download_dir)
        if len(files) == 1:  # Espera que haja apenas um arquivo na pasta
            return files[0]
        time.sleep(1)
    return None

# Função para renomear e mover o arquivo para a pasta xls
def rename_and_move_file(downloaded_filename):
    xls_dir = os.path.join(os.path.abspath("./data"), "xls")
    if not os.path.exists(xls_dir):
        os.makedirs(xls_dir)
    
    old_path = os.path.join(os.path.abspath("./data"), downloaded_filename)
    new_path = os.path.join(xls_dir, "fretes.xls")
    
    # Renomeia o arquivo para "fretes.xls" e move para a pasta xls
    shutil.move(old_path, new_path)
    print(f"Arquivo renomeado e movido para: {new_path}")

# Configuração do Selenium para usar o ChromeDriver
options = webdriver.ChromeOptions()
prefs = {"download.default_directory": os.path.abspath("./data")}
options.add_experimental_option("prefs", prefs)
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
# Para depuração, remova o headless se estiver ativado
# options.add_argument("--headless")

# Inicializa o navegador
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# URLs
url_login = (
    "https://sso-external.fretebras.com.br/realms/companies/protocol/openid-connect/auth?"
    "state=ea61138d7983caf7813ce0462afbde55&scope=profile%20email%20openid&response_type=code&"
    "approval_prompt=auto&redirect_uri=https%3A%2F%2Ffretebras.com.br%2Fsso%2Fsrc%2Findex.php&"
    "client_id=central-assinante#/"
)
url_fretes = "https://novacentral.fretebras.com.br/meus-fretes"

try:
    print("Abrindo a página de login...")
    driver.get(url_login)

    print("Aguardando o campo de e-mail (input real) ficar visível...")
    username_input = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.ID, "username"))
    )
    print("Campo de e-mail visível. Enviando e-mail...")
    username_input.clear()
    username_input.send_keys(email_)

    print("Aguardando o campo de senha (input real) ficar visível...")
    password_input = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.ID, "password"))
    )
    print("Campo de senha visível. Enviando senha...")
    password_input.clear()
    password_input.send_keys(senha_ + Keys.RETURN)

    print("Aguardando redirecionamento após login...")
    WebDriverWait(driver, 15).until(
        EC.url_contains("fretebras.com.br")
    )
    print("Redirecionamento detectado.")

    print("Acessando a página de fretes...")
    driver.get(url_fretes)

    print("Aguardando o botão 'Download da listagem' ficar presente...")
    # Usando XPath refinado para garantir a seleção do botão correto
    download_button = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//fuel-button[normalize-space(text())='Download da listagem' and @variant='secondary' and @disabled='false']"))
    )
    print("Botão 'Download da listagem' encontrado. Tentando clicar via JavaScript...")
    driver.execute_script("arguments[0].click();", download_button)

    print("Aguardando o download ser concluído...")
    downloaded_filename = is_downloaded("fretes.xls", timeout=5)

    if downloaded_filename:
        print(f"Arquivo {downloaded_filename} baixado.")
        rename_and_move_file(downloaded_filename)  # Renomeia e move o arquivo
    else:
        print("Erro: O download não foi concluído dentro do tempo esperado.")

except Exception as e:
    print(f"Erro ao baixar o arquivo: {e}")

finally:
    driver.quit()
    print("Navegador fechado.")
