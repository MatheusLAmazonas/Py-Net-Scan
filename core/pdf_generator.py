from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime

def generate_lan_report(filename, scan_results):
    """Gera o relatório em PDF da Rede Local (LAN)."""
    doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('ReportTitle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#1a365d'), spaceAfter=6)
    subtitle_style = ParagraphStyle('ReportSubtitle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#4a5568'), spaceAfter=15)

    story.append(Paragraph("Relatório de Varredura de Rede Local (LAN) - Py-Net-Scan", title_style))
    story.append(Paragraph(f"Data da Varredura: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", subtitle_style))
    story.append(Spacer(1, 10))

    data = [["Status", "Endereço IP", "Nome", "MAC Address", "Fabricante", "Latência"]]
    for item in scan_results:
        data.append([
            item.get('status', 'Online'),
            item.get('ip', 'N/A'),
            item.get('nome', '-'),
            item.get('mac', '-'),
            item.get('fabricante', '-'),
            item.get('rtt', '-')
        ])

    table = Table(data, colWidths=[60, 95, 95, 110, 110, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2b6cb0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7fafc')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
    ]))

    story.append(table)
    doc.build(story)

def generate_ports_report(filename, ip_alvo, nome_alvo, portas_results):
    """Gera o relatório em PDF focado nas portas abertas de um IP específico."""
    doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('ReportTitle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#1a365d'), spaceAfter=6)
    subtitle_style = ParagraphStyle('ReportSubtitle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#4a5568'), spaceAfter=15)

    story.append(Paragraph(f"Relatório de Mapeamento de Portas - Py-Net-Scan", title_style))
    story.append(Paragraph(f"Alvo: {ip_alvo} ({nome_alvo}) | Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", subtitle_style))
    story.append(Spacer(1, 10))

    data = [["Porta", "Protocolo", "Estado", "Serviço", "Versão"]]
    for item in portas_results:
        data.append([
            str(item.get('porta', '')),
            item.get('protocolo', 'TCP'),
            item.get('estado', '-'),
            item.get('servico', '-'),
            item.get('versao', '-')
        ])

    table = Table(data, colWidths=[80, 80, 90, 120, 170])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2b6cb0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7fafc')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
    ]))

    story.append(table)
    doc.build(story)