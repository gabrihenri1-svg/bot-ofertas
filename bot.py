import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler
from PIL import Image
import requests
import io

TOKEN = os.getenv("BOT_TOKEN") or "COLE_SEU_TOKEN_AQUI"
CLIPDROP_API_KEY = os.getenv("CLIPDROP_API_KEY") or ""

def colocar_fundo_branco(caminho_png_transparente):
    """Pega PNG transparente e coloca fundo branco 1080x1080"""
    img = Image.open(caminho_png_transparente).convert("RGBA")
    # cria fundo branco quadrado
    tamanho = 1080
    fundo = Image.new("RGB", (tamanho, tamanho), (255, 255, 255))
    # redimensiona produto mantendo proporção
    img.thumbnail((tamanho-100, tamanho-100), Image.LANCZOS)
    x = (tamanho - img.width) // 2
    y = (tamanho - img.height) // 2
    fundo.paste(img, (x, y), img)
    saida = "produto_final.jpg"
    fundo.save(saida, "JPEG", quality=95)
    return saida

async def limpar_imagem(caminho_entrada):
    # tenta Clipdrop se tiver chave
    if CLIPDROP_API_KEY:
        try:
            url = "https://clipdrop-api.co/remove-background/v1"
            with open(caminho_entrada, 'rb') as f:
                r = requests.post(url, files={'image_file': f}, headers={'x-api-key': CLIPDROP_API_KEY}, timeout=30)
            if r.status_code == 200:
                open("sem_fundo.png","wb").write(r.content)
                return colocar_fundo_branco("sem_fundo.png")
        except Exception as e:
            print(e)
    # fallback: sem Clipdrop, só coloca borda branca
    try:
        img = Image.open(caminho_entrada).convert("RGB")
        img.thumbnail((980, 980), Image.LANCZOS)
        fundo = Image.new("RGB", (1080,1080), (255,255,255))
        fundo.paste(img, ((1080-img.width)//2, (1080-img.height)//2))
        fundo.save("produto_final.jpg","JPEG",quality=95)
        return "produto_final.jpg"
    except:
        return caminho_entrada

async def handle_foto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚡️ Recebendo... gerando versão loja oficial...")
    file = await update.message.photo[-1].get_file()
    await file.download_to_drive("original.jpg")
    final = await limpar_imagem("original.jpg")
    await update.message.reply_photo(photo=open(final,'rb'), caption="✅ Finalizada - Fundo branco infinito 1080x1080 pronta pra Shopee/Magalu/Insta")

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Radar de ofertas pronto!\n\nManda qualquer foto de produto que eu devolvo no padrão loja oficial (fundo branco infinito).")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", handle_start))
app.add_handler(MessageHandler(filters.PHOTO, handle_foto))
print("Bot rodando fundo branco...")
app.run_polling()
