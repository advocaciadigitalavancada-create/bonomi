import asyncio
import os
import shutil
from playwright.async_api import async_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CENTRAL_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "relatorios_2p", "bonomi"))
os.makedirs(CENTRAL_DIR, exist_ok=True)

CONFIGS = [
    {
        "name": "color",
        "html": os.path.join(BASE_DIR, "relatorio_bonomi_4paginas_color.html"),
        "pdf": os.path.join(BASE_DIR, "relatorio_bonomi_4paginas_color.pdf"),
        "previews": [
            os.path.join(BASE_DIR, "preview_color_p1.png"),
            os.path.join(BASE_DIR, "preview_color_p2.png"),
            os.path.join(BASE_DIR, "preview_color_p3.png"),
            os.path.join(BASE_DIR, "preview_color_p4.png"),
        ]
    },
    {
        "name": "pb",
        "html": os.path.join(BASE_DIR, "relatorio_bonomi_4paginas_pb.html"),
        "pdf": os.path.join(BASE_DIR, "relatorio_bonomi_4paginas_pb.pdf"),
        "previews": [
            os.path.join(BASE_DIR, "preview_pb_p1.png"),
            os.path.join(BASE_DIR, "preview_pb_p2.png"),
            os.path.join(BASE_DIR, "preview_pb_p3.png"),
            os.path.join(BASE_DIR, "preview_pb_p4.png"),
        ]
    }
]

async def render_config(browser, cfg):
    print(f"\n[*] Renderizando versao 4P {cfg['name'].upper()}...")
    page = await browser.new_page(viewport={"width": 794, "height": 1123})
    
    file_uri = "file:///" + cfg["html"].replace("\\", "/")
    await page.goto(file_uri, wait_until="networkidle")
    await page.wait_for_timeout(2000)
    
    pages = await page.query_selector_all(".page")
    print(f"[OK] Total de paginas identificadas: {len(pages)}")
    
    for i, p_el in enumerate(pages):
        if i < len(cfg["previews"]):
            target_path = cfg["previews"][i]
            await p_el.screenshot(path=target_path)
            print(f"[OK] Preview P{i+1} salvo: {os.path.basename(target_path)}")
        
    saved_pdf = None
    candidates = [
        cfg["pdf"],
        cfg["pdf"].replace(".pdf", "_atualizado.pdf"),
        cfg["pdf"].replace(".pdf", "_respiro.pdf"),
        cfg["pdf"].replace(".pdf", "_novo2.pdf")
    ]
    for cand in candidates:
        try:
            await page.pdf(
                path=cand,
                format="A4",
                print_background=True,
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"}
            )
            saved_pdf = cand
            print(f"[OK] PDF 4P gerado: {cand}")
            break
        except PermissionError:
            continue
    if not saved_pdf:
        print(f"[ERRO] Nao foi possivel salvar PDF para {cfg['name']} (todos os arquivos bloqueados).")
    cfg["pdf"] = saved_pdf
    await page.close()

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        for cfg in CONFIGS:
            await render_config(browser, cfg)
        await browser.close()
        
    print("\n[*] Replicando arquivos canonicos para a pasta central relatorios_2p/bonomi/...")
    # Copiar QR codes
    for qr_name in ["qr_bonomi_site.png", "qr_carlos_pix.png", "qr_carlos_whatsapp.png"]:
        src_qr = os.path.join(BASE_DIR, qr_name)
        if os.path.exists(src_qr):
            shutil.copy2(src_qr, os.path.join(CENTRAL_DIR, qr_name))
            
    for cfg in CONFIGS:
        shutil.copy2(cfg["html"], os.path.join(CENTRAL_DIR, os.path.basename(cfg["html"])))
        if os.path.exists(cfg["pdf"]):
            try:
                shutil.copy2(cfg["pdf"], os.path.join(CENTRAL_DIR, os.path.basename(cfg["pdf"])))
            except Exception as e:
                print(f"[AVISO] Nao foi possivel replicar {os.path.basename(cfg['pdf'])} para a central: {e}")
        for prev in cfg["previews"]:
            if os.path.exists(prev):
                shutil.copy2(prev, os.path.join(CENTRAL_DIR, os.path.basename(prev)))
            
    print("[SUCESSO] Pipeline de geracao e replicacao do relatorio 4P concluido com sucesso!")

if __name__ == "__main__":
    asyncio.run(main())
