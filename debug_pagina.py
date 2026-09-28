import requests

BASE_URL = "https://unicorp.loja.srv.br/"
LOGIN_URL = "https://unicorp.loja.srv.br/sga_alunos_login/"

session = requests.Session()
session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
})

# Faz o login
session.post(
    LOGIN_URL,
    data={
        "login": "836.262.820-07",
        "senha": "01012005",
        "cpf": "836.262.820-07",
    },
)

# Acessa a Unidade 1
url_unidade = "https://unicorp.loja.srv.br/teste2?cursoId=156&disciplinaId=798&unidade=1&matriculaId=6224"
res = session.get(url_unidade)

# Salva o HTML retornado em um arquivo para análise
with open("pagina_unidade1.html", "w", encoding="utf-8") as f:
  f.write(res.text)

print("Arquivo 'pagina_unidade1.html' gerado com sucesso!")