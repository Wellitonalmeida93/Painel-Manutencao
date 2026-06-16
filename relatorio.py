import os
import time
import sys
import traceback
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from playwright.sync_api import sync_playwright

# ==================================================
# CONFIGURAÇÕES
# ==================================================

URL_POWER_BI = "https://app.powerbi.com/view?r=eyJrIjoiZTg0YjIxMjgtYjJhOC00NDY5LWEzYjItNjM0M2IyZTgyMTExIiwidCI6ImY0Y2Q4NWNjLWQ1YTAtNGVmZC04NzkzLThhNzg5NDE5MGNmYSJ9&pageName=2307bfd0ca141332ad94"

REMETENTE_EMAIL = "welliton.almeida@pizzattolog.com.br"
REMETENTE_SENHA = os.environ.get("SENHA_EMAIL")

DESTINATARIOS = [
    "Welliton.almeida@pizzattolog.com.br"
]

# ==================================================
# CAPTURA DO DASHBOARD
# ==================================================

def capturar_print_powerbi(url, caminho_saida):
    print("🤖 [DIAGNÓSTICO] Iniciando Playwright...")

    try:
        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-dev-shm-usage",
                    "--no-sandbox"
                ]
            )

            context = browser.new_context(
                viewport={
                    "width": 1600,
                    "height": 1000
                },
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0 Safari/537.36"
            )

            page = context.new_page()

            print("🌐 Abrindo Power BI...")
            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=120000
            )

            print("⏳ Aguardando carregamento dos componentes...")
            page.wait_for_load_state("networkidle", timeout=120000)

            # Tempo extra para renderizar gráficos
            time.sleep(20)

            print("📸 Capturando tela...")
            page.screenshot(
                path=caminho_saida,
                full_page=False
            )

            browser.close()

            if os.path.exists(caminho_saida):
                tamanho = os.path.getsize(caminho_saida)

                if tamanho > 0:
                    print(f"✅ Print salvo ({tamanho:,} bytes)")
                    return True

            print("❌ Arquivo de imagem não foi criado corretamente.")
            return False

    except Exception:
        print("\n❌ ERRO AO CAPTURAR POWER BI")
        traceback.print_exc(file=sys.stdout)
        return False


# ==================================================
# ENVIO DE E-MAIL
# ==================================================

def enviar_email(caminho_imagem):

    print("📧 Preparando e-mail...")

    if not REMETENTE_SENHA:
        print("❌ SENHA_EMAIL não encontrada nos Secrets.")
        return False

    if not os.path.exists(caminho_imagem):
        print("❌ Imagem não encontrada.")
        return False

    try:

        msg = MIMEMultipart("mixed")

        msg["From"] = REMETENTE_EMAIL
        msg["To"] = ", ".join(DESTINATARIOS)
        msg["Subject"] = "Relatório Diário Salesco - Atualizado"

        corpo = MIMEMultipart("related")
        msg.attach(corpo)

        cid_imagem = "dashboard_salesco"

        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <p>
                    Olá,
                    <br><br>

                    O relatório foi atualizado com sucesso.

                    <br><br>

                    Dashboard Online:
                    <a href="{URL_POWER_BI}">
                        Clique Aqui
                    </a>

                    <br><br>

                    <img src="cid:{cid_imagem}" width="1000">

                    <br><br>

                    Atenciosamente,
                    <br>
                    Automação Salesco
                </p>
            </body>
        </html>
        """

        corpo.attach(MIMEText(html, "html", "utf-8"))

        with open(caminho_imagem, "rb") as imagem:
            img = MIMEImage(imagem.read())

            img.add_header(
                "Content-ID",
                f"<{cid_imagem}>"
            )

            img.add_header(
                "Content-Disposition",
                "inline",
                filename=os.path.basename(caminho_imagem)
            )

            corpo.attach(img)

        print("📡 Conectando ao SMTP...")

        # Microsoft 365 / Outlook
        with smtplib.SMTP("smtp.office365.com", 587) as server:

            server.ehlo()
            server.starttls()
            server.ehlo()

            server.login(
                REMETENTE_EMAIL,
                REMETENTE_SENHA
            )

            server.sendmail(
                REMETENTE_EMAIL,
                DESTINATARIOS,
                msg.as_string()
            )

        print("🚀 E-mail enviado com sucesso!")
        return True

    except Exception:
        print("\n❌ ERRO NO ENVIO DE E-MAIL")
        traceback.print_exc(file=sys.stdout)
        return False


# ==================================================
# EXECUÇÃO
# ==================================================

if __name__ == "__main__":

    print("🎬 Script iniciado")

    pasta_atual = os.path.dirname(
        os.path.abspath(__file__)
    )

    caminho_print = os.path.join(
        pasta_atual,
        "print_salesco_auto.png"
    )

    sucesso_print = capturar_print_powerbi(
        URL_POWER_BI,
        caminho_print
    )

    if sucesso_print:
        enviar_email(caminho_print)
    else:
        print("🛑 Processo encerrado devido à falha na captura.")
