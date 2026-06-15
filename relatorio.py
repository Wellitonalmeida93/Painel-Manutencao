import os
import sys
import traceback
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage 

# Biblioteca da Microsoft para automação direto na nuvem
from playwright.sync_api import sync_playwright

# --- CONFIGURAÇÕES 100% ONLINE ---
URL_POWER_BI = "https://app.powerbi.com/view?r=eyJrIjoiMjY0OWFhODQtYmU3Yy00NTE3LWIzZDYtZGY5MzUyNTlhYzRkIiwidCI6ImY0Y2Q4NWNjLWQ1YTAtNGVmZC04NzkzLThhNzg5NDE5MGNmYSJ9"
REMETENTE_EMAIL = "welliton.almeida@pizzattolog.com.br"
REMETENTE_SENHA = os.environ.get("SENHA_EMAIL") # Puxa do cofre seguro do GitHub

DESTINATARIOS = [
    "Israel.joia@pizzattolog.com.br",
    "daniel.sacramento@pizzattolog.com.br",
    "lucas.justus@pizzattolog.com.br",
    "magdo.ferreira@pizzattolog.com.br",
    "subcontratados@pizzattolog.com.br"
]

def capturar_print_powerbi(url, caminho_saida):
    print("🤖 [PLAYWRIGHT] Navegador virtual iniciado. Olhando para a internet...")
    try:
        with sync_playwright() as p:
            # Lança o navegador em modo invisível, ideal para servidores
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1600, "height": 1000},
                device_scale_factor=1.2 # Deixa os gráficos do print mais nítidos
            )
            page = context.new_page()
            
            print("⏳ [PLAYWRIGHT] Acessando o link do Power BI Online...")
            page.goto(url)
            
            print("⏳ [PLAYWRIGHT] Aguardando 20 segundos para os gráficos carregarem na tela...")
            page.wait_for_timeout(20000) 
            
            # Tira o print e salva na memória temporária do servidor do GitHub
            page.screenshot(path=caminho_saida)
            print(f"✅ [PLAYWRIGHT] Print tirado e salvo temporariamente.")
            
            browser.close()
            return True
            
    except Exception as e:
        print("\n❌ [ERRO] Falha ao abrir o navegador ou capturar a tela do Power BI:")
        traceback.print_exc(file=sys.stdout)
        return False

def enviar_email(caminho_imagem):
    print("📧 [SMTP] Preparando o disparo do e-mail...")
    if not REMETENTE_SENHA:
        print("❌ [ERRO DE AMBIENTE] A senha secreta não foi encontrada no GitHub Secrets!")
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
               O relatório de abastecimento foi processado na nuvem.<br>
               Confira abaixo o <b>Dashboard Salesco</b> atualizado direto do link público:<br><br>
               Link do painel: <a href="{URL_POWER_BI}">Acessar Power BI Online</a><br><br>
               <img src="cid:{cid_id}" width="1000" style="border: 1px solid #ddd;"><br><br> 
               Atenciosamente,<br>
            </p>
        </body>
        </html>
        """
        msg.attach(MIMEText(corpo_html, 'html'))

        # Lê a imagem que o Playwright acabou de tirar e acopla no e-mail
        with open(caminho_imagem, 'rb') as img_f:
            img = MIMEImage(img_f.read())
            img.add_header('Content-ID', f'<{cid_id}>')
            msg_corpo.attach(img)

        print("⏳ [SMTP] Conectando com segurança aos servidores do Gmail...")
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(REMETENTE_EMAIL, REMETENTE_SENHA)
            server.sendmail(REMETENTE_EMAIL, DESTINATARIOS, msg.as_string())
        
        print("🚀 [SUCESSO] E-mail enviado com o print online para todos!")

    except Exception as e:
        print("\n❌ [ERRO] Falha no envio do e-mail via SMTP do Gmail:")
        traceback.print_exc(file=sys.stdout)

if __name__ == "__main__":
    print("🎬 Iniciando automação 100% Cloud.")
    
    # Salva o print apenas na pasta temporária do servidor do GitHub
    NOME_PRINT = "print_salesco_auto.png"

    sucesso = capturar_print_powerbi(URL_POWER_BI, NOME_PRINT)
    if sucesso:
        enviar_email(NOME_PRINT)
        
        # Limpa o arquivo temporário após o envio para não deixar rastros
        if os.path.exists(NOME_PRINT):
            os.remove(NOME_PRINT)
    else:
        print("🛑 Execução cancelada porque a captura online falhou.")
