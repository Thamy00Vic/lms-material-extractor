import os
import re
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright

LOGIN_URL = "https://unicorp.loja.srv.br/sga_alunos_login/"
CPF_LOGIN = "836.262.820-07"
SENHA_LOGIN = "01012005"


def limpar_nome(nome):
  if not nome:
    return "Sem_Nome"
  nome_limpo = re.sub(r'[\\/*?:"<>|]', "", nome)
  return re.sub(r"\s+", " ", nome_limpo).strip()


def material_ja_existe(pasta_destino, nome_base):
  """Verifica se o PDF ou a imagem já foi baixada."""
  caminho_pdf = os.path.join(pasta_destino, f"{nome_base}.pdf")
  caminho_png = os.path.join(pasta_destino, f"{nome_base}.png")
  return (os.path.exists(caminho_pdf) and os.path.getsize(caminho_pdf) > 1000) or (
      os.path.exists(caminho_png) and os.path.getsize(caminho_png) > 1000
  )


with sync_playwright() as p:
  browser = p.chromium.launch(headless=False)
  context = browser.new_context(accept_downloads=True)
  page = context.new_page()

  ultimo_pdf_url = [None]

  def interceptar_respostas(res):
    u = res.url.lower()
    ct = res.headers.get("content-type", "").lower()
    if ".pdf" in u or "application/pdf" in ct:
      ultimo_pdf_url[0] = res.url

  page.on("response", interceptar_respostas)

  print("1. Realizando login...")
  page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=60000)

  try:
    page.locator(
        'input[type="text"], input[name*="login"], input[name*="cpf"], input:visible'
    ).first.fill(CPF_LOGIN)
    page.locator('input[type="password"]').fill(SENHA_LOGIN)
    page.locator(
        'button[type="submit"], input[type="submit"], button:has-text("Entrar"), button:has-text("Acessar")'
    ).first.click()
  except Exception as e:
    print(f"Aviso no login: {e}")

  page.wait_for_timeout(4000)
  print("✔ Login concluído com sucesso!")

  print("2. Carregando catálogo de cursos...")
  page.goto(
      "https://unicorp.loja.srv.br/sga_alunos/meusCursos",
      wait_until="domcontentloaded",
      timeout=60000,
  )
  page.wait_for_timeout(3000)

  if "painel" in page.url:
    page.goto(
        "https://unicorp.loja.srv.br/sga_alunos/minhasMatriculas",
        wait_until="domcontentloaded",
        timeout=60000,
    )
    page.wait_for_timeout(3000)

  links_todos_cursos = page.locator('a[href*="teste?"]').all()
  lista_cursos_urls = []
  
  for elem in links_todos_cursos:
    href = elem.get_attribute("href") or ""
    if "matriculaId" in href and href not in lista_cursos_urls:
      lista_cursos_urls.append(href)

  print(f"\nTotal de cursos identificados: {len(lista_cursos_urls)}")

  # =========================================================================
  # PROCESSAMENTO DE CADA CURSO
  # =========================================================================
  for idx_c, link_curso in enumerate(lista_cursos_urls):
    print(f"\n=================================================================")
    print(f"[{idx_c + 1}/{len(lista_cursos_urls)}] ABRINDO CURSO...")

    if idx_c > 0:
        try:
          page.goto("https://unicorp.loja.srv.br/sga_alunos/minhasMatriculas", wait_until="domcontentloaded", timeout=60000)
          page.wait_for_timeout(2500)
        except Exception:
          pass

    url_curso = urljoin("https://unicorp.loja.srv.br/sga_alunos/", link_curso)

    # Tenta abrir o curso, com tratamento de reconexão se o portal abortar (ERR_ABORTED)
    try:
      page.goto(url_curso, wait_until="domcontentloaded", timeout=60000)
      page.wait_for_timeout(3500)
    except Exception as e:
      print(f"Instabilidade no servidor ao abrir o curso. Tentando recarregar...")
      try:
          page.reload(wait_until="domcontentloaded", timeout=60000)
          page.wait_for_timeout(3500)
      except Exception:
          print(f"Pulo: Não foi possível acessar a grade do curso.")
          continue

    nome_curso = f"Curso_{idx_c + 1}"
    try:
      banner = page.locator(".widget-header h3 strong, .widget-header strong, h3.widget-content-light").first
      if banner.count() > 0 and len(banner.inner_text().strip()) > 3:
        nome_curso = limpar_nome(banner.inner_text().split("\n")[0].strip())
    except Exception:
      pass

    print(f"CURSO CONFIRMADO: {nome_curso}")

    paineis = page.locator("#faq1 .panel").all()
    print(f"Disciplinas encontradas: {len(paineis)}")

    if len(paineis) == 0:
        continue

    for idx_d, painel in enumerate(paineis):
      try:
        titulo_elem = painel.locator(".panel-title strong, .panel-title a")
        if titulo_elem.count() == 0:
          continue

        texto_titulo = titulo_elem.first.inner_text().strip()
        nome_disciplina = limpar_nome(texto_titulo)
      except Exception:
        continue
      
      print(f"\n--- [{idx_d + 1}/{len(paineis)}] DISCIPLINA: {nome_disciplina} ---")

      try:
        link_acc = painel.locator("a.accordion-toggle")
        if link_acc.count() > 0:
            link_acc.click()
            page.wait_for_timeout(500)
      except Exception:
        pass

      try:
        links_unidades = painel.locator('.panel-body a[href*="teste2?"]').all()
        unidades_urls = []
        for lu in links_unidades:
          h_u = lu.get_attribute("href") or ""
          t_u = (lu.inner_text() or "").strip()
          if "unidade=" in h_u and t_u.lower().startswith("unidade"):
            if (t_u, h_u) not in unidades_urls:
              unidades_urls.append((t_u, h_u))
      except Exception:
        continue

      for txt_unid, href_unid in unidades_urls:
        unidade_nome = limpar_nome(txt_unid)
        pasta_destino = os.path.join("cursos", nome_curso, nome_disciplina, unidade_nome)
        os.makedirs(pasta_destino, exist_ok=True)

        # Retomada Inteligente
        if material_ja_existe(pasta_destino, "Slides") and material_ja_existe(pasta_destino, "E-book"):
          print(f"   ⏩ {unidade_nome}: Já baixado, pulando...")
          continue

        url_unidade_completa = urljoin("https://unicorp.loja.srv.br/sga_alunos/", href_unid)
        print(f"   --> Acessando {unidade_nome}...")

        try:
          # Alterado para "commit" para não travar se a página demorar a montar os recursos
          page.goto(url_unidade_completa, wait_until="commit", timeout=60000)
          page.wait_for_timeout(3000)
        except Exception as e:
          print(f"Erro ao abrir {unidade_nome}. O portal demorou muito a responder.")
          continue

        try:
            linhas_mats = page.locator('table a[href*="teste3"]').all()
            mats_para_baixar = []
            for lm in linhas_mats:
              t_mat = (lm.inner_text() or "").strip()
              h_mat = lm.get_attribute("href") or ""
              if any(m in t_mat.lower() for m in ["slide", "e-book", "ebook"]):
                mats_para_baixar.append((t_mat, h_mat))
        except Exception:
            continue

        for rotulo_mat, link_mat in mats_para_baixar:
          nome_arquivo_base = limpar_nome(rotulo_mat)

          if material_ja_existe(pasta_destino, nome_arquivo_base):
            print(f"       ⏩ {nome_arquivo_base} já existe.")
            continue

          url_mat_completa = urljoin("https://unicorp.loja.srv.br/sga_alunos/", link_mat)
          ultimo_pdf_url[0] = None

          try:
            page.goto(url_mat_completa, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(3000)
          except Exception:
            print(f"Erro ao acessar leitor do {nome_arquivo_base}.")
            continue

          caminho_pdf = os.path.join(pasta_destino, f"{nome_arquivo_base}.pdf")
          baixou = False

          # 1. Tentativa botão visualizador
          try:
              btn_doc = page.locator('text="Clique para Visualizar/Baixar o documento"')
              if btn_doc.count() > 0:
                  with page.expect_download(timeout=6000) as d_info:
                    btn_doc.first.click()
                  d = d_info.value
                  d.save_as(caminho_pdf)
                  print(f"       ✔ PDF baixado: {nome_arquivo_base}.pdf")
                  baixou = True
          except Exception:
              pass

          # 2. Tentativa toolbar nativo
          if not baixou:
            try:
              btn_toolbar = page.locator('button#download, #download, button[title*="Download"]')
              if btn_toolbar.count() > 0 and btn_toolbar.first.is_visible():
                with page.expect_download(timeout=6000) as d_info:
                  btn_toolbar.first.click()
                d = d_info.value
                d.save_as(caminho_pdf)
                print(f"       ✔ PDF via toolbar: {nome_arquivo_base}.pdf")
                baixou = True
            except Exception:
              pass

          # 3. Tentativa rede
          if not baixou and ultimo_pdf_url[0]:
            try:
              res_pdf = context.request.get(ultimo_pdf_url[0])
              if res_pdf.status == 200:
                with open(caminho_pdf, "wb") as f:
                  f.write(res_pdf.body())
                print(f"       ✔ PDF via rede: {nome_arquivo_base}.pdf")
                baixou = True
            except Exception:
              pass

          # 4. Fallback print da tela
          if not baixou:
            caminho_img = os.path.join(pasta_destino, f"{nome_arquivo_base}.png")
            try:
              page.screenshot(path=caminho_img)
              print(f"       ✔ Backup visual salvo: {nome_arquivo_base}.png")
            except Exception:
              pass

        try:
          page.goto(url_curso, wait_until="domcontentloaded", timeout=60000)
          page.wait_for_timeout(2000)
        except Exception:
          pass

  print("\n=======================================================")
  print("Todos os materiais pendentes foram finalizados!")
  browser.close()