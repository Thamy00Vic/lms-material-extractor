import os
import datetime
import matplotlib.pyplot as plt

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
except ImportError:
    print("ERRO: A biblioteca reportlab não está instalada.")
    exit()

# --- CONFIGURAÇÕES ---
pasta_base = "cursos"
arquivo_log = "log_plataforma.txt"
TOTAL_CURSOS_PLATAFORMA = 52

# Contadores e Listas
total_cursos, total_disciplinas, total_unidades, total_arquivos = 0, 0, 0, 0
cursos_processados_nomes = []
falhas_detalhadas = []

print("🔎 Inspetor Bugiganga: Lendo logs e gerando relatórios. Aguarde...")

if not os.path.exists(pasta_base):
    print("A pasta 'cursos' ainda não existe. Execute os robôs primeiro!")
    exit()

# --- LEITURA DO DIÁRIO DE BORDO DOS ROBÔS ---
avisos_plataforma = {}
if os.path.exists(arquivo_log):
    with open(arquivo_log, "r", encoding="utf-8") as f:
        for linha in f:
            partes = linha.strip().split('|')
            if len(partes) == 4:
                c, d, u, motivo = partes
                # Cria uma chave única para buscar depois
                chave = f"{c}_{d}_{u}"
                avisos_plataforma[chave] = motivo

pastas_cursos = [c for c in os.listdir(pasta_base) if os.path.isdir(os.path.join(pasta_base, c))]
tempos_criacao = []

# --- VARREDURA E AUDITORIA ---
for curso in pastas_cursos:
    caminho_curso = os.path.join(pasta_base, curso)
    tempos_criacao.append(os.path.getctime(caminho_curso))
    total_cursos += 1
    cursos_processados_nomes.append(curso)
    
    disciplinas = os.listdir(caminho_curso)

    if not disciplinas:
        chave_busca = f"{curso}_N/A_N/A"
        motivo_log = avisos_plataforma.get(chave_busca, "Grade de disciplinas não carregada devido à queda de conexão.")
        tipo_erro = "BLOQUEIO NA PLATAFORMA" if chave_busca in avisos_plataforma else "FALHA DE REDE"
        
        falhas_detalhadas.append({"local": f"Curso: {curso}", "tipo": tipo_erro, "motivo": motivo_log})

    for disc in disciplinas:
        caminho_disc = os.path.join(caminho_curso, disc)
        if os.path.isdir(caminho_disc):
            total_disciplinas += 1
            unidades = os.listdir(caminho_disc)

            if not unidades:
                chave_busca = f"{curso}_{disc}_N/A"
                motivo_log = avisos_plataforma.get(chave_busca, "O servidor demorou a responder (timeout).")
                tipo_erro = "CONTEÚDO INDISPONÍVEL" if chave_busca in avisos_plataforma else "FALHA DE ROTA"
                
                falhas_detalhadas.append({"local": f"Curso: {curso} -> Disciplina: {disc}", "tipo": tipo_erro, "motivo": motivo_log})

            for unid in unidades:
                caminho_unid = os.path.join(caminho_disc, unid)
                if os.path.isdir(caminho_unid):
                    total_unidades += 1
                    arquivos = os.listdir(caminho_unid)

                    if not arquivos:
                        chave_busca = f"{curso}_{disc}_{unid}"
                        motivo_log = avisos_plataforma.get(chave_busca, "A conexão foi interrompida durante a transferência.")
                        tipo_erro = "CONTEÚDO FUTURO/BLOQUEADO" if chave_busca in avisos_plataforma else "FALHA DE DOWNLOAD"
                        
                        falhas_detalhadas.append({"local": f"Curso: {curso} -> Disciplina: {disc} -> Unidade: {unid}", "tipo": tipo_erro, "motivo": motivo_log})
                    else:
                        total_arquivos += len(arquivos)

# --- CÁLCULO DE ETA E GRÁFICOS ---
cursos_restantes = max(0, TOTAL_CURSOS_PLATAFORMA - total_cursos)
texto_estimativa = "Dados insuficientes para calcular o tempo."

if total_cursos > 0 and tempos_criacao:
    tempo_decorrido = datetime.datetime.now().timestamp() - min(tempos_criacao)
    if tempo_decorrido > 60 and total_cursos > 1:
        segundos_restantes = (tempo_decorrido / total_cursos) * cursos_restantes
        texto_estimativa = f"Em velocidade média atual, estima-se que a sincronização dos {cursos_restantes} cursos restantes seja concluída em aproximadamente <b>{int(segundos_restantes // 3600)} horas e {int((segundos_restantes % 3600) // 60)} minutos</b>."

nome_grafico = "grafico_progresso.png"
plt.figure(figsize=(5, 3))
if sum([total_cursos, cursos_restantes]) > 0:
    plt.pie([total_cursos, cursos_restantes], labels=['Concluídos', 'Pendentes'], colors=['#005b96', '#d3d3d3'], autopct='%1.1f%%', startangle=140)
    plt.title('Progresso de Extração', fontsize=12)
    plt.tight_layout()
    plt.savefig(nome_grafico, dpi=150)
    plt.close()

# --- ESTILOS COMUNS ---
data_atual = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M")
styles = getSampleStyleSheet()
estilo_titulo = ParagraphStyle(name='Titulo', parent=styles['Heading1'], alignment=TA_CENTER, spaceAfter=20, textColor="#002244")
estilo_subtitulo = ParagraphStyle(name='Subtitulo', parent=styles['Heading2'], spaceAfter=10, textColor="#003366")
estilo_normal = ParagraphStyle(name='Normal_Justificado', parent=styles['Normal'], alignment=TA_JUSTIFY, spaceAfter=10, fontSize=11, leading=14)
estilo_topico = ParagraphStyle(name='Topico', parent=styles['Normal'], spaceAfter=5, fontSize=10, leftIndent=15)
estilo_falha_local = ParagraphStyle(name='FalhaLocal', parent=styles['Normal'], spaceAfter=2, fontSize=10, leftIndent=10, fontName='Helvetica-Bold')
estilo_falha_motivo = ParagraphStyle(name='FalhaMotivo', parent=styles['Normal'], spaceAfter=10, fontSize=10, leftIndent=20, textColor="#555555")

# ==========================================
# PDF 1: RELATÓRIO EXECUTIVO (PRESIDÊNCIA)
# ==========================================
doc_exec = SimpleDocTemplate("Relatorio_Executivo_Presidencia.pdf", pagesize=A4)
elem_exec = []
elem_exec.append(Paragraph("RELATÓRIO EXECUTIVO — BACKUP DE PLATAFORMA", estilo_titulo))
elem_exec.append(Paragraph(f"<b>Data:</b> {data_atual}<br/><b>Status:</b> Em Andamento", estilo_normal))
elem_exec.append(Spacer(1, 10))
elem_exec.append(Paragraph("PROJEÇÃO E VOLUMETRIA GERAL", estilo_subtitulo))
elem_exec.append(Paragraph(f"• <b>Total de Arquivos Salvos:</b> {total_arquivos} (PDFs, imagens e documentos)", estilo_topico))
elem_exec.append(Paragraph(f"• <b>Cursos Processados:</b> {total_cursos} de {TOTAL_CURSOS_PLATAFORMA}", estilo_topico))
elem_exec.append(Spacer(1, 5))
elem_exec.append(Paragraph(texto_estimativa, estilo_normal))

if os.path.exists(nome_grafico):
    elem_exec.append(RLImage(nome_grafico, width=350, height=210))
    elem_exec.append(Spacer(1, 10))

# --- LISTA NUMERADA DE CURSOS ADICIONADA AQUI ---
elem_exec.append(Paragraph("RELAÇÃO DE CURSOS PROCESSADOS", estilo_subtitulo))
if cursos_processados_nomes:
    # Ordena alfabeticamente e adiciona a numeração (1., 2., 3...)
    for idx, nome_c in enumerate(sorted(cursos_processados_nomes), start=1):
        elem_exec.append(Paragraph(f"{idx}. {nome_c}", estilo_topico))
else:
    elem_exec.append(Paragraph("Nenhum curso concluído até o momento.", estilo_normal))

elem_exec.append(Spacer(1, 15))
elem_exec.append(Paragraph("<i>Nota: O detalhamento técnico de conectividade encontra-se no Anexo Técnico.</i>", ParagraphStyle(name='Nota', parent=estilo_normal, fontSize=9, textColor="#666666")))

doc_exec.build(elem_exec)

# ==========================================
# PDF 2: ANEXO TÉCNICO DETALHADO
# ==========================================
doc_tec = SimpleDocTemplate("Anexo_Tecnico_Falhas.pdf", pagesize=A4)
elem_tec = []
elem_tec.append(Paragraph("LOG DE AUDITORIA E PENDÊNCIAS", estilo_titulo))
elem_tec.append(Paragraph(f"<b>Data da verificação:</b> {data_atual}", estilo_normal))
elem_tec.append(Spacer(1, 10))

if falhas_detalhadas:
    for falha in falhas_detalhadas:
        cor_tipo = "#b30000" if "FALHA" in falha['tipo'] else "#cc8800"
        estilo_dinamico = ParagraphStyle(name='Dyn', parent=estilo_falha_local, textColor=cor_tipo)
        
        elem_tec.append(Paragraph(f"[{falha['tipo']}] {falha['local']}", estilo_dinamico))
        elem_tec.append(Paragraph(f"Detalhe: {falha['motivo']}", estilo_falha_motivo))
else:
    elem_tec.append(Paragraph("✔️ Nenhuma falha identificada.", estilo_normal))

doc_tec.build(elem_tec)

if os.path.exists(nome_grafico):
    os.remove(nome_grafico)

print("✅ PDFs atualizados com o cruzamento de logs e lista numerada!")