import os
import time
import sys
import traceback
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage 

# Bibliotecas para automação do navegador
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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
    print("🤖 [DIAGNÓSTICO] Iniciando a rotina do Selenium...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  
    chrome_options.add_argument("--window-size=1600,1000") 
    chrome_options.add_argument("--force-device-scale-factor=1.2") 
    chrome_options.add_argument("--no-sandbox") 
    chrome_options.add_argument("--disable-dev-shm-usage") 
    chrome_options.add_argument("--disable-gpu") 

    driver = None
    try:
        print("⏳ [DIAGNÓSTICO] Tentando instanciar o webdriver.Chrome()...")
        driver = webdriver.Chrome(options=chrome_options)
        print("✅ [DIAGNÓSTICO] Navegador iniciado com sucesso!")
        
        print(f"⏳ [DIAGNÓSTICO] Acessando a URL do Power BI...")
        driver.get(url)
        
        print("⏳ [DIAGNÓSTICO] Aguardando 20 segundos para renderização dos gráficos...")
        time.sleep(20) 
        
        driver.save_screenshot(caminho_saida)
        print(f"✅ [DIAGNÓSTICO] Print gravado no disco virtual: {caminho_saida}")
        return True
        
    except Exception as e:
        print("\n❌ [ERRO CRÍTICO NO SELENIUM] Ocorreu uma falha no navegador:")
        traceback.print_exc(file=sys.stdout)
        return False
    finally:
        if driver:
            try:
                driver.quit()
                print("🤖 [DIAGNÓSTICO] Instância do Chrome encerrada corretamente.")
            except:
                pass

def enviar_email(caminho_imagem):
    print("📧 [DIAGNÓSTICO] Iniciando rotina de e-mail...")
    
    if not REMETENTE_SENHA:
        print("❌ [ERRO DE AMBIENTE] A chave 'SENHA_EMAIL' não foi mapeada ou está vazia no GitHub Secrets!")
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
               Acesse online: <a href="{URL_POWER_BI}">Clique Aqui</a><br><br>
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

        print("⏳ [DIAGNÓSTICO] Conectando ao servidor SMTP do Gmail...")
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(REMETENTE_EMAIL, REMETENTE_SENHA)
            server.sendmail(REMETENTE_EMAIL, DESTINATARIOS, msg.as_string())
        
        print("🚀 [SUCESSO] Relatório enviado com sucesso!")

    except Exception as e:
        print("\n❌ [ERRO CRÍTICO NO E-MAIL] Falha ao enviar via SMTP:")
        traceback.print_exc(file=sys.stdout)

if __name__ == "__main__":
    print("🎬 [DIAGNÓSTICO] Script iniciado.")
    pasta_atual = os.path.dirname(os.path.abspath(__file__))
    CADA_PRINT = os.path.join(pasta_atual, "print_salesco_auto.png")

    sucesso = capturar_print_powerbi(URL_POWER_BI, CADA_PRINT)
    if sucesso:
        enviar_email(CADA_PRINT)
    else:
        print("🛑 [INFO] Execução abortada devido à falha no print.")
