# 🎓 Extrator de Materiais EAD (LMS Material Extractor)

Um ecossistema de automação em Python projetado para realizar o backup completo e estruturado de uma plataforma de ensino a distância (EAD). O sistema simula a navegação de um usuário, desvia inteligentemente de conteúdos bloqueados e gera relatórios de auditoria com qualidade executiva.

## 🎯 Para que serve este projeto?
Plataformas LMS (Learning Management Systems) costumam organizar seus materiais em centenas de unidades isoladas. Realizar o download manual de todo esse acervo exige semanas de trabalho braçal, agravado pelo fato de que muitos conteúdos sofrem "liberação progressiva" (bloqueios por data ou pré-requisito). 

Este projeto automatiza 100% dessa tarefa através de **Web Scraping Avançado**, garantindo que nenhum PDF, slide ou e-book fique para trás, enquanto documenta o que não pôde ser baixado.

---

## 🤖 Como funciona: A Tropa de Robôs

A arquitetura do projeto divide o trabalho pesado entre três agentes autônomos. Cada um possui uma responsabilidade exclusiva:

### 1. Troinha 01 (`baixar_materiais.py`)
É o **extrator principal**. Ele faz o login na plataforma e entra curso por curso, do primeiro ao último. 
* **Inteligência de Retomada:** Antes de tentar baixar um PDF, ele olha a pasta no seu HD. Se o arquivo já estiver lá, ele pula, economizando banda e tempo.
* **Mapeamento de Bloqueios:** Se ele tentar entrar em uma unidade vazia ou bloqueada pelo professor, ele não trava. Ele anota o erro em um "diário de bordo" (o arquivo `log_plataforma.txt`) e segue a vida.

###
2. Configure suas credenciais:
Abra os arquivos baixar_materiais.py e baixar_materiais_reverso.py e insira seus dados nas variáveis localizadas nas primeiras linhas:
CPF_LOGIN = "SEU_CPF_AQUI"
SENHA_LOGIN = "SUA_SENHA_AQUI"

###
3. Dê o play na extração:
Abra dois terminais na mesma pasta para ativar a concorrência máxima:

No terminal 1, rode: python baixar_materiais.py

No terminal 2, rode: python baixar_materiais_reverso.py

4. Audite os resultados:
A qualquer momento (mesmo com os robôs trabalhando), você pode abrir um terceiro terminal e rodar:
python inspetor_bugiganga.py

###
Os PDFs serão gerados instantaneamente na sua pasta.

🛡️ Notas de Segurança e Privacidade
Este projeto foi arquitetado respeitando a segurança de dados. O arquivo .gitignore impede que senhas gravadas sem querer, diários de bordo e arquivos de material didático (.pdf, .png) protegidos por direitos autorais sejam enviados para o GitHub. Apenas o código e a arquitetura da solução se tornam públicos. Lembre-se de sempre apagar suas senhas do código antes de dar git push.
