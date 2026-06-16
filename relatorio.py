import os
import time
import sys
import traceback
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage 
from playwright.sync_api import sync_playwright

# --- CONFIGURAÇÕES ---
URL_POWER_BI = "https://powerbi.com"
REMETENTE_EMAIL = "welliton.almeida@pizzattolog.com.br"
REMETENTE_SENHA = os.environ.get("SENHA_EMAIL") 

DESTINATARIOS = [
    "Israel.joia@pizzattolog.com.br",
    "daniel.sacramento@pizzattolog.com.br",
    "lucas.justus@pizzattolog.com.br",
    "magdo.ferreira@pizzattolog.com.br",
    "subcontratados@pizzattolog.com.br",
    "Welliton.almeida@pizzattolog.com.br"
]

def capturar_print_powerbi(url, caminho_saida):
    print("🤖 [DIAGNÓSTICO] Iniciando a rotina do Playwright...")
    try:
        with sync_playwright() as p:
            print("⏳ [DIAGNÓSTICO] Abrindo navegador virtual Chromium...")
            browser = p.chromium.launch(headless=True)
            
            # Força uma resolução de tela cheia padrão de monitor (1600x1000)
            context = browser.new_context(viewport={"width": 1600, "height": 1000})
            page = context.new_page()
            
            print("⏳ [DIAGNÓSTICO] Acessando a URL do Power BI...")
            page.goto(url)
            
            print("⏳ [DIAGNÓSTICO] Aguardando 25 segundos para renderização dos gráficos...")
            time.sleep(25)
            
            # Salva o print da página inteira
            page.screenshot(path=caminho_saida, full_page=True)
            print(f"✅ [DIAGNÓSTICO] Print gravado em: {caminho_saida}")
            
            browser.close()
            return True
            
    except Exception as e:
        print("\n❌ [ERRO CRÍTICO NO PLAYWRIGHT] Falha ao capturar a tela:")
        traceback.print_exc(file=sys.stdout)
        return False

def enviar_email(caminho_imagem):
    print("📧 [DIAGNÓSTICO] Iniciando rotina de e-mail...")
    if not REMETENTE_SENHA:
        print("❌ [ERRO DE AMBIENTE] A chave 'SENHA_EMAIL' não foi mapeada no GitHub Secrets!")
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
        with smtplib.SMTP("://gmail.com", 587) as server:
            server.starttls()
            server.login(REMETENTE_EMAIL, REMETENTE_SENHA)
            server.sendmail(REMETENTE_EMAIL, DESTINATARIOS, msg.as_string())
        
        print("🚀 [SUCESSO] Relatório enviado por e-mail com sucesso!")

    except Exception as e:
        print("\n❌ [ERRO CRÍTICO NO E-MAIL] Falha ao enviar via SMTP:")
        traceback.print_exc(file=sys.stdout)

if __name__ == "__main__":
    print("🎬 [DIAGNÓSTICO] Script iniciado na nuvem.")
    pasta_atual = os.path.dirname(os.path.abspath(__file__))
    CADA_PRINT = os.path.join(pasta_atual, "print_salesco_auto.png")

    sucesso = capturar_print_powerbi(URL_POWER_BI, CADA_PRINT)
    if sucesso:
        enviar_email(CADA_PRINT)
    else:
        print("🛑 [INFO] Execução abortada devido à falha no print.")
