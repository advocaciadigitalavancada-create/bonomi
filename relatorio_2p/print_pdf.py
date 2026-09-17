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
        "html": os.path.join(BASE_DIR, "relatorio_bonomi_2paginas_color.html"),
        "pdf": os.path.join(BASE_DIR, "relatorio_bonomi_2paginas_color.pdf"),
        "preview_p1": os.path.join(BASE_DIR, "preview_color_p1.png"),
        "preview_p2": os.path.join(BASE_DIR, "preview_color_p2.png"),
    },
    {
        "name": "pb",
        "html": os.path.join(BASE_DIR, "relatorio_bonomi_2paginas_pb.html"),
        "pdf": os.path.join(BASE_DIR, "relatorio_bonomi_2paginas_pb.pdf"),
        "preview_p1": os.path.join(BASE_DIR, "preview_pb_p1.png"),
        "preview_p2": os.path.join(BASE_DIR, "preview_pb_p2.png"),
    }
]

async def render_config(browser, cfg):
    print(f"\n[*] Renderizando versao {cfg['name'].upper()}...")
    page = await browser.new_page(viewport={"width": 794, "height": 1123})
    
    file_uri = "file:///" + cfg["html"].replace("\\", "/")
    await page.goto(file_uri, wait_until="networkidle")
    await page.wait_for_timeout(2000)
    
    pages = await page.query_selector_all(".page")
    print(f"[OK] Total de paginas identificadas: {len(pages)}")
    
    if len(pages) >= 1:
        await pages[0].screenshot(path=cfg["preview_p1"])
        print(f"[OK] Preview P1 salvo: {cfg['preview_p1']}")
    if len(pages) >= 2:
        await pages[1].screenshot(path=cfg["preview_p2"])
        print(f"[OK] Preview P2 salvo: {cfg['preview_p2']}")
        
    await page.pdf(
        path=cfg["pdf"],
        format="A4",
        print_background=True,
        margin={"top": "0", "right": "0", "bottom": "0", "left": "0"}
    )
    print(f"[OK] PDF gerado: {cfg['pdf']}")
    await page.close()

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        for cfg in CONFIGS:
            await render_config(browser, cfg)
        await browser.close()
        
    print("\n[*] Replicando arquivos canonicos para a pasta central relatorios_2p/bonomi/...")
    for cfg in CONFIGS:
        shutil.copy2(cfg["html"], os.path.join(CENTRAL_DIR, os.path.basename(cfg["html"])))
        shutil.copy2(cfg["pdf"], os.path.join(CENTRAL_DIR, os.path.basename(cfg["pdf"])))
        if os.path.exists(cfg["preview_p1"]):
            shutil.copy2(cfg["preview_p1"], os.path.join(CENTRAL_DIR, os.path.basename(cfg["preview_p1"])))
        if os.path.exists(cfg["preview_p2"]):
            shutil.copy2(cfg["preview_p2"], os.path.join(CENTRAL_DIR, os.path.basename(cfg["preview_p2"])))
            
    print("[SUCESSO] Pipeline de geracao e replicacao do relatorio 2P concluido!")

if __name__ == "__main__":
    asyncio.run(main())
