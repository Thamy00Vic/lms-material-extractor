import os
import re
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

# --- CONFIGURAÇÕES ---
BASE_URL = "https://unicorp.loja.srv.br/"
LOGIN_URL = "https://unicorp.loja.srv.br/sga_alunos_login/"

# Dados de acesso
CPF_LOGIN = "836.262.820-07"
SENHA_LOGIN = "01012005"

# Dados da disciplina que você enviou
CURSO_ID = 156
DISCIPLINA_ID = 798
MATRICULA_ID = 6224
NOME_DISCIPLINA = "INTRODUCAO_A_EAD"
TOTAL_UNIDADES = 4


def sanitizar_nome(nome):
  """Remove caracteres que não podem ser usados em nomes de arquivos."""
  nome_limpo = re.sub(r'[\\/*?:"<>|]', "", nome).strip()
  return " ".join(nome_limpo.split())


# Inicializa a sessão HTTP (guarda os cookies do login automaticamente)
session = requests.Session()
session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
})

print("1. Realizando login no portal...")

# Payload padrão de formulários de autenticação
payload_login = {
    "login": CPF_LOGIN,
    "senha": SENHA_LOGIN,
    "cpf": CPF_LOGIN,  # Enviamos variações comuns de nomes de campos
    "password": SENHA_LOGIN,
}

resposta_login = session.post(LOGIN_URL, data=payload_login)

if resposta_login.status_code != 200:
  print(
      f"Erro ao tentar conectar na página de login: Status"
      f" {resposta_login.status_code}"
  )
  exit()

print("Login processado com sucesso!")

# Cria pasta para a disciplina
os.makedirs(NOME_DISCIPLINA, exist_ok=True)

# 2. Percorre cada uma das 4 unidades
for unidade in range(1, TOTAL_UNIDADES + 1):
  url_unidade = urljoin(
      BASE_URL,
      f"teste2?cursoId={CURSO_ID}&disciplinaId={DISCIPLINA_ID}&unidade={unidade}&matriculaId={MATRICULA_ID}",
  )

  pasta_unidade = os.path.join(NOME_DISCIPLINA, f"Unidade_{unidade}")
  os.makedirs(pasta_unidade, exist_ok=True)

  print(f"\n==========================================")
  print(f"Acessando: Unidade {unidade}...")
  print(f"URL: {url_unidade}")

  res_unidade = session.get(url_unidade)

  if res_unidade.status_code != 200:
    print(f"Erro ao abrir Unidade {unidade}: Status {res_unidade.status_code}")
    continue

  soup = BeautifulSoup(res_unidade.text, "html.parser")

  # Busca todos os links ou iframes na página
  links = soup.find_all("a", href=True)
  iframes = soup.find_all("iframe", src=True)

  arquivos_para_baixar = []

  # Procura por links de materiais (E-book, Slide, Mapa Conceitual, PDFs)
  for tag in links:
    texto = tag.get_text(strip=True).lower()
    href = tag["href"]

    # Termos e extensões procurados
    eh_material = any(
        termo in texto for termo in ["e-book", "ebook", "slide", "mapa", "livro"]
    ) or any(
        href.lower().endswith(ext)
        for ext in [".pdf", ".pptx", ".ppt", ".zip", ".rar"]
    )

    if eh_material:
      nome = tag.get_text(strip=True) or href.split("/")[-1].split("?")[0]
      url_completa = urljoin(BASE_URL, href)
      arquivos_para_baixar.append((nome, url_completa))

  # Alguns sistemas colocam os slides/e-books dentro de <iframe>
  for iframe in iframes:
    src = iframe["src"]
    if any(ext in src.lower() for ext in [".pdf", "drive.google", "view"]):
      nome = f"Material_Embutido_Unidade_{unidade}.pdf"
      url_completa = urljoin(BASE_URL, src)
      arquivos_para_baixar.append((nome, url_completa))

  if not arquivos_para_baixar:
    print(
        f"Aviso: Nenhum link direto detectado na Unidade {unidade}. Pode estar"
        " protegido por JavaScript."
    )
    continue

  # 3. Baixa os arquivos encontrados na unidade
  for nome, link_download in arquivos_para_baixar:
    nome_arquivo = sanitizar_nome(nome)
    if not any(
        nome_arquivo.endswith(ext)
        for ext in [".pdf", ".pptx", ".ppt", ".zip", ".rar"]
    ):
      nome_arquivo += ".pdf"

    caminho_arquivo = os.path.join(pasta_unidade, nome_arquivo)

    print(f"Baixando: {nome_arquivo}...")
    try:
      with session.get(link_download, stream=True) as r:
        if r.status_code == 200:
          with open(caminho_arquivo, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
              f.write(chunk)
          print(f"✔ Salvo com sucesso: {nome_arquivo}")
        else:
          print(f"✖ Erro HTTP {r.status_code} ao baixar {link_download}")
    except Exception as e:
      print(f"✖ Falha ao baixar {nome_arquivo}: {e}")

print("\nProcesso finalizado!")