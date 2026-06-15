import os
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage 

# Bibliotecas para automação do navegador
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURAÇÕES ---
URL_POWER_BI = "https://app.powerbi.com/view?r=eyJrIjoiMjY0OWFhODQtYmU3Yy00NTE3LWIzZDYtZDY5MzUyNTlhYzRkIiwidCI6ImY0Y2Q4NWNjLWQ1YTAtNGVmZC04NzkzLThhNzg5NDE5MGNmYSJ9"
REMETENTE_EMAIL = "welliton.almeida@pizzattolog.com.br"
REMETENTE_SENHA = os.environ.get("SENHA_EMAIL") 

DESTINATARIOS = [
    "Israel.joia@pizzattolog.com.br",
    "daniel.sacramento@pizzattolog.com.br",
    "lucas.justus@pizzattolog.com.br",
    "magdo.ferreira@pizzattolog.com.br",
    "subcontratados@pizzattolog.com.br"
]

def capturar_print_powerbi(url, caminho_saida):
    print("🤖 Iniciando captura do Power BI...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Modo invisível moderno e estável
    chrome_options.add_argument("--window-size=1600,1000") 
    chrome_options.add_argument("--force-device-scale-factor=1.2") 
    chrome_options.add_argument("--no-sandbox") 
    chrome_options.add_argument("--disable-dev-shm-usage") 
    chrome_options.add_argument("--disable-gpu")  # Desativa aceleração de hardware (essencial p/ nuvem)

    try:
        servico = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=servico, options=chrome_options)
    except Exception as err_driver:
        print(f"❌ Erro ao inicializar o Chrome/WebDriver: {err_driver}")
        return False

    try:
        driver.get(url)
        print("⏳ Aguardando 20 segundos para carregamento dos dados...")
        time.sleep(20) 
        
        driver.save_screenshot(caminho_saida)
        print(f"✅ Print salvo com sucesso em: {caminho_saida}")
        return True
    except Exception as e:
        print(f"❌ Erro durante a navegação/captura: {e}")
        return False
    finally:
        try:
            driver.quit()
        except:
            pass

def enviar_email(caminho_imagem):
    print("📧 Preparando e-mail para envio...")
    
    if not REMETENTE_SENHA:
        print("❌ Erro crítico: A variável secreta 'SENHA_EMAIL' está vazia ou não foi configurada no GitHub!")
        return

    try:
        msg = MIMEMultipart('mixed')
        msg['From'] = REMETENTE_EMAIL
        msg['To'] = ", ".join(DESTINATARIOS)
        msg['Subject'] = "Relatório Diário Salesco - Atualizado"

        msg_corpo = MIMEMultipart('related')
        msg.attach(msg_corpo)

        cid_id = "dashboard_pbi"
        corpo_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <p>Olá,<br><br>
               O relatório de abastecimento foi processado.<br>
               Confira abaixo o <b>Dashboard Salesco</b> atualizado:<br><br>
               Acesse o painel interativo online: <a href="{URL_POWER_BI}">Clique Aqui</a><br><br>
               <img src="cid:{cid_id}" width="1000" style="border: 1px solid #ddd;"><br><br> 
               Atenciosamente,<br>
            </p>
        </body>
        </html>
        """
        msg_corpo.attach(MIMEText(corpo_html, 'html'))

        with open(caminho_imagem, 'rb') as img_f:
            img = MIMEImage(img_f.read())
            img.add_header('Content-ID', f'<{cid_id}>')
            msg_corpo.attach(img)

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(REMETENTE_EMAIL, REMETENTE_SENHA)
            server.sendmail(REMETENTE_EMAIL, DESTINATARIOS, msg.as_string())
        
        print("🚀 Relatório enviado com sucesso para todos os destinatários!")

    except Exception as e:
        print(f"❌ Erro ao enviar e-mail por SMTP: {e}")

if __name__ == "__main__":
    pasta_atual = os.path.dirname(os.path.abspath(__file__))
    CADA_PRINT = os.path.join(pasta_atual, "print_salesco_auto.png")

    sucesso = capturar_print_powerbi(URL_POWER_BI, CADA_PRINT)
    
    if sucesso:
        enviar_email(CADA_PRINT)
    else:
        print("🛑 Processo interrompido devido a falhas na captura da imagem.")
