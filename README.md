🎓 Extrator de Materiais EAD (LMS Material Extractor)
Um ecossistema de automação em Python projetado para realizar o backup completo e estruturado de uma plataforma de ensino a distância (EAD). O sistema simula a navegação de um usuário, desvia inteligentemente de conteúdos bloqueados e gera relatórios de auditoria com qualidade executiva.

🎯 Para que serve este projeto?
Plataformas LMS (Learning Management Systems) costumam organizar seus materiais em centenas de unidades isoladas. Realizar o download manual de todo esse acervo exige semanas de trabalho braçal, agravado pelo fato de que muitos conteúdos sofrem "liberação progressiva" (bloqueios por data ou pré-requisito).

Este projeto automatiza 100% dessa tarefa através de Web Scraping Avançado, garantindo que nenhum PDF, slide ou e-book fique para trás, enquanto documenta o que não pôde ser baixado.

🤖 Como funciona: A Tropa de Robôs
A arquitetura do projeto divide o trabalho pesado entre três agentes autônomos. Cada um possui uma responsabilidade exclusiva:

1. Troinha 01 (baixar_materiais.py)
É o extrator principal. Ele faz o login na plataforma e entra curso por curso, do primeiro ao último.

Inteligência de Retomada: Antes de tentar baixar um PDF, ele olha a pasta no seu HD. Se o arquivo já estiver lá, ele pula, economizando banda e tempo.

Mapeamento de Bloqueios: Se ele tentar entrar em uma unidade vazia ou bloqueada pelo professor, ele não trava. Ele anota o erro em um "diário de bordo" (o arquivo log_plataforma.txt) e segue a vida.

2. Troinha 02 (baixar_materiais_reverso.py)
É o acelerador (concorrência). Ele tem o mesmo cérebro do Troinha 1, mas uma rota diferente: ele lê a lista de cursos de trás para frente (do último para o primeiro).

Por que usá-lo? Você pode rodar o Troinha 1 e o Troinha 2 ao mesmo tempo no seu computador em dois terminais separados. Um limpa o site subindo e o outro descendo. O tempo de backup cai pela metade e eles nunca esbarram nos mesmos arquivos ao mesmo tempo.

3. Inspetor Bugiganga (inspetor_bugiganga.py)
É o auditor offline. Ele não acessa a internet. O trabalho dele é cruzar os dados da pasta no seu HD com o diário de bordo deixado pelos robôs e emitir pareceres em PDF:

Relatório Executivo: Voltado para a Diretoria/Presidência. Contém a volumetria total, um gráfico de progresso limpo, estimativa de tempo e uma lista numerada oficial de todos os cursos concluídos.

Anexo Técnico: Voltado para a equipe de TI. Ele lê o diário dos robôs e separa os erros por cor: laranja para "A plataforma bloqueou esse conteúdo" e vermelho para "A sua internet caiu na hora de baixar".

🛠️ Tecnologias Utilizadas
Python 3: Linguagem base de toda a arquitetura.

Playwright: Responsável por abrir o navegador "fantasma" (Chromium), clicar em botões, interceptar requisições de rede escondidas no site e fazer os downloads forçados.

ReportLab: Biblioteca de design usada pelo Inspetor para desenhar e diagramar os PDFs do zero.

Matplotlib: Responsável por renderizar os gráficos de pizza baseados nos dados de extração.

🚀 Como instalar e rodar
1. Clone o projeto e instale as ferramentas necessárias:
Abra o seu terminal e rode os comandos abaixo na sequência:

Bash
git clone https://github.com/Thamy00Vic/lms-material-extractor.git
cd lms-material-extractor
pip install playwright reportlab matplotlib
python -m playwright install chromium
2. Configure suas credenciais:
Abra os arquivos baixar_materiais.py e baixar_materiais_reverso.py e insira seus dados nas variáveis localizadas nas primeiras linhas:

Python
CPF_LOGIN = "SEU_CPF_AQUI"
SENHA_LOGIN = "SUA_SENHA_AQUI"
3. Dê o play na extração:
Abra dois terminais na mesma pasta para ativar a concorrência máxima:

No terminal 1, rode: python baixar_materiais.py

No terminal 2, rode: python baixar_materiais_reverso.py

4. Audite os resultados:
A qualquer momento (mesmo com os robôs trabalhando), você pode abrir um terceiro terminal e rodar:

Bash
python inspetor_bugiganga.py
Os PDFs serão gerados instantaneamente na sua pasta.
