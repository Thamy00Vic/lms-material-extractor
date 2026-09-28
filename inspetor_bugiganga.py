import os
import datetime
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
except ImportError:
    print("ERRO: A biblioteca reportlab não está instalada.")
    print("Por favor, execute no terminal: pip install reportlab")
    exit()

# --- CONFIGURAÇÕES ---
pasta_base = "cursos"

# Variáveis para contar
total_cursos = 0
total_disciplinas = 0
total_unidades = 0
total_arquivos = 0
alertas = []

print("🔎 Inspetor Bugiganga: A gerar relatório gerencial em formato PDF. Aguarde...")

if not os.path.exists(pasta_base):
    print("A pasta 'cursos' ainda não existe. Execute os robôs de extração primeiro!")
    exit()

# Percorre as pastas
for curso in os.listdir(pasta_base):
    caminho_curso = os.path.join(pasta_base, curso)
    if os.path.isdir(caminho_curso):
        total_cursos += 1
        disciplinas = os.listdir(caminho_curso)

        if not disciplinas:
            alertas.append(f"Curso sem disciplinas baixadas: {curso}")

        for disc in disciplinas:
            caminho_disc = os.path.join(caminho_curso, disc)
            if os.path.isdir(caminho_disc):
                total_disciplinas += 1
                unidades = os.listdir(caminho_disc)

                if not unidades:
                     alertas.append(f"Disciplina vazia: {curso} -> {disc}")

                for unid in unidades:
                    caminho_unid = os.path.join(caminho_disc, unid)
                    if os.path.isdir(caminho_unid):
                        total_unidades += 1
                        arquivos = os.listdir(caminho_unid)

                        if not arquivos:
                            alertas.append(f"Falta material: {curso} -> {disc} -> {unid}")
                        else:
                            total_arquivos += len(arquivos)

data_atual = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M")

# ==========================================
# CRIAÇÃO DO DOCUMENTO PDF
# ==========================================
nome_arquivo = "Relatorio_Inspetor_Bugiganga.pdf"
doc = SimpleDocTemplate(nome_arquivo, pagesize=A4)
styles = getSampleStyleSheet()

# Estilos customizados para o PDF
estilo_titulo = ParagraphStyle(name='Titulo', parent=styles['Heading1'], alignment=TA_CENTER, spaceAfter=20)
estilo_subtitulo = ParagraphStyle(name='Subtitulo', parent=styles['Heading2'], spaceAfter=10)
estilo_normal = ParagraphStyle(name='Normal_Justificado', parent=styles['Normal'], alignment=TA_JUSTIFY, spaceAfter=10, fontSize=11, leading=14)
estilo_topico = ParagraphStyle(name='Topico', parent=styles['Normal'], spaceAfter=5, fontSize=11, leftIndent=20)

elementos = []

# Título Principal
elementos.append(Paragraph("RELATÓRIO GERENCIAL — AUTOMAÇÃO DE BACKUP", estilo_titulo))

# Cabeçalho
elementos.append(Paragraph(f"<b>Gerado por:</b> Inspetor Bugiganga<br/><b>Data da verificação:</b> {data_atual}", estilo_normal))
elementos.append(Spacer(1, 10))

# Resumo Executivo
elementos.append(Paragraph("RESUMO EXECUTIVO", estilo_subtitulo))
elementos.append(Paragraph("O processo de automação destinado à realização do backup da plataforma académica encontra-se em andamento. Até ao momento, foram realizadas as etapas de mapeamento, processamento e sincronização dos conteúdos identificados. Abaixo, são apresentados os indicadores consolidados referentes aos materiais processados e armazenados com sucesso no repositório local.", estilo_normal))
elementos.append(Spacer(1, 10))

# Indicadores
elementos.append(Paragraph("INDICADORES DE PROGRESSO", estilo_subtitulo))
elementos.append(Paragraph(f"• <b>Cursos mapeados e processados:</b> {total_cursos}", estilo_topico))
elementos.append(Paragraph(f"• <b>Disciplinas processadas:</b> {total_disciplinas}", estilo_topico))
elementos.append(Paragraph(f"• <b>Unidades de estudo verificadas:</b> {total_unidades}", estilo_topico))
elementos.append(Paragraph(f"• <b>Arquivos armazenados (PDFs e imagens):</b> {total_arquivos}", estilo_topico))
elementos.append(Spacer(1, 10))

# Pendências
elementos.append(Paragraph("PENDÊNCIAS E OCORRÊNCIAS", estilo_subtitulo))
if alertas:
    elementos.append(Paragraph("Durante a execução do processo, foram identificadas algumas falhas no download de determinados ficheiros. As respetivas pastas foram criadas e estruturadas normalmente, porém parte dos conteúdos não pôde ser descarregada durante a execução atual. As ocorrências podem estar relacionadas a instabilidades temporárias no servidor de origem ou na ligação de rede.", estilo_normal))
    elementos.append(Paragraph("Os itens pendentes permanecerão registados para que sejam submetidos a novas tentativas de processamento nas próximas execuções da automação.", estilo_normal))
    elementos.append(Paragraph("<b>Detalhamento das ocorrências para reprocessamento:</b>", estilo_normal))
    
    for aviso in alertas:
        elementos.append(Paragraph(f"• {aviso}", estilo_topico))
else:
    elementos.append(Paragraph("Nenhuma ocorrência registada. Todos os diretórios verificados estão íntegros e com os respetivos ficheiros armazenados com sucesso.", estilo_normal))

elementos.append(Spacer(1, 10))

# Considerações Finais
elementos.append(Paragraph("CONSIDERAÇÕES FINAIS", estilo_subtitulo))
elementos.append(Paragraph("O processo de backup permanece em execução, com o conteúdo já processado devidamente organizado e armazenado no repositório local. As pendências identificadas serão acompanhadas nas próximas execuções, visando à conclusão da sincronização dos materiais restantes.", estilo_normal))

# Constrói o PDF e guarda no disco
doc.build(elementos)

print(f"✅ Missão cumprida! O ficheiro '{nome_arquivo}' foi gerado com sucesso na sua pasta.")