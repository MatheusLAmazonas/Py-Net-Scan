import sys
import os
from PySide6.QtCore import QProcess, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from ui.threads import ICMPWorkerThread, WANWorkerThread


class TerminalWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Display do terminal
        self.output_terminal = QTextEdit()
        self.output_terminal.setReadOnly(True)

        # Campo para digitar o comando
        self.input_comando = QLineEdit()
        self.input_comando.setPlaceholderText("Digite um comando (ex: ping 127.0.0.1)...")

        layout.addWidget(self.output_terminal)
        layout.addWidget(self.input_comando)

        # Processo assíncrono para execução no SO
        self.processo = QProcess(self)
        self.processo.readyReadStandardOutput.connect(self.ler_saida_padrao)
        self.processo.readyReadStandardError.connect(self.ler_saida_erro)
        self.processo.finished.connect(self.processo_finalizado)

        self.input_comando.returnPressed.connect(self.executar_comando)

        # Codificação de caracteres dinâmica por plataforma
        self.encoding = "cp850" if sys.platform == "win32" else "utf-8"

        # Aplica o estilo inicial (Light)
        self.atualizar_tema(is_dark=False)

    def atualizar_tema(self, is_dark: bool):
        """Atualiza dinamicamente as cores do terminal para Dark ou Light Mode."""
        if is_dark:
            bg_color = "#1e1e1e"
            text_color = "#ffffff"
            border_color = "#555555"
            input_bg = "#3b3b3b"
            input_text = "#ffffff"
        else:
            bg_color = "#ffffff"
            text_color = "#1e1e1e"
            border_color = "#c0c0c0"
            input_bg = "#ffffff"
            input_text = "#1e1e1e"

        self.output_terminal.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: {bg_color};
                color: {text_color};
                font-family: Consolas, 'Courier New', Monospace;
                font-size: 9pt;
                border: 1px solid {border_color};
            }}
            """
        )

        self.input_comando.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: {input_bg};
                color: {input_text};
                font-family: Consolas, 'Courier New', Monospace;
                border: 1px solid {border_color};
                padding: 3px;
            }}
            """
        )

    def executar_comando(self):
        comando = self.input_comando.text().strip()
        if not comando:
            return

        self.input_comando.clear()

        # Limpar tela localmente (funciona em Windows, Linux e macOS)
        if comando.lower() in ["cls", "clear"]:
            self.output_terminal.clear()
            return

        self.output_terminal.append(f"> {comando}")

        # Identificação e execução por Sistema Operacional
        if sys.platform == "win32":
            self.processo.start("cmd.exe", ["/c", comando])
        else:
            # Atende macOS e Linux utilizando a variável de ambiente do Shell do usuário
            shell = os.environ.get("SHELL", "/bin/sh")
            self.processo.start(shell, ["-c", comando])

    def ler_saida_padrao(self):
        dados = self.processo.readAllStandardOutput()
        texto = dados.data().decode(self.encoding, errors="replace")
        self.output_terminal.insertPlainText(texto)
        self.output_terminal.ensureCursorVisible()

    def ler_saida_erro(self):
        dados = self.processo.readAllStandardError()
        texto = dados.data().decode(self.encoding, errors="replace")
        self.output_terminal.insertPlainText(texto)
        self.output_terminal.ensureCursorVisible()

    def processo_finalizado(self):
        self.output_terminal.append("> Concluído.\n")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyNetScan")
        self.resize(1200, 750)

        self.worker = None
        self.worker_wan = None

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout_principal = QVBoxLayout(central_widget)
        layout_principal.setContentsMargins(5, 5, 5, 5)

        # -------------------------------------------------------------
        # 1. BARRA SUPERIOR DE BOTÕES
        # -------------------------------------------------------------
        painel_topo = QWidget()
        painel_topo.setObjectName("painel_topo")
        painel_topo.setFixedHeight(50)

        layout_topo = QHBoxLayout(painel_topo)
        layout_topo.setContentsMargins(5, 5, 5, 5)
        layout_topo.setSpacing(5)

        self.btn_init = QPushButton("▶ Iniciar Scan LAN")
        self.btn_stop = QPushButton("■ Parar")
        self.btn_tema = QPushButton("Dark Mode")
        self.btn_stop.setEnabled(False)

        self.btn_init.setFixedSize(140, 32)
        self.btn_stop.setFixedSize(90, 32)
        self.btn_tema.setFixedSize(120, 32)

        layout_topo.addWidget(self.btn_init)
        layout_topo.addWidget(self.btn_stop)
        layout_topo.addWidget(self.btn_tema)
        layout_topo.addStretch()

        layout_principal.addWidget(painel_topo)

        # -------------------------------------------------------------
        # 2. CONTEÚDO PRINCIPAL (SPLITTER ESQUERDA / DIREITA)
        # -------------------------------------------------------------
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # =============================================================
        # LADO ESQUERDO: PAINEL DE PARÂMETROS, SCANNER E TERMINAL
        # =============================================================
        widget_esquerdo = QWidget()
        layout_esquerdo = QVBoxLayout(widget_esquerdo)
        layout_esquerdo.setContentsMargins(5, 0, 5, 0)

        # --- Subpainel 1: Scanner LAN ---
        gb_scanner = QGroupBox("Scanner de Rede Local (LAN)")
        layout_gb_scanner = QVBoxLayout(gb_scanner)

        # Faixa de IP
        gb_ip_range = QGroupBox("Faixa de IP")
        layout_ip = QVBoxLayout(gb_ip_range)

        layout_de = QHBoxLayout()
        layout_de.addWidget(QLabel("De:"))
        self.input_ip_de = QLineEdit("192.168.1.1")
        layout_de.addWidget(self.input_ip_de)
        layout_ip.addLayout(layout_de)

        layout_ate = QHBoxLayout()
        layout_ate.addWidget(QLabel("Até:"))
        self.input_ip_ate = QLineEdit("192.168.1.254")
        layout_ate.addWidget(self.input_ip_ate)
        layout_ip.addLayout(layout_ate)

        layout_mask = QHBoxLayout()
        layout_mask.addWidget(QLabel("Máscara:"))
        self.combo_mask = QComboBox()
        self.combo_mask.addItems(["/24 (255.255.255.0)", "/16 (255.255.0.0)", "/8 (255.0.0.0)"])
        layout_mask.addWidget(self.combo_mask)
        layout_ip.addLayout(layout_mask)

        layout_gb_scanner.addWidget(gb_ip_range)

        # Opções LAN
        gb_opcoes = QGroupBox("Opções LAN")
        layout_opcoes = QVBoxLayout(gb_opcoes)

        layout_threads = QHBoxLayout()
        layout_threads.addWidget(QLabel("Threads:"))
        self.spin_threads = QSpinBox()
        self.spin_threads.setRange(1, 500)
        self.spin_threads.setValue(100)
        layout_threads.addWidget(self.spin_threads)
        layout_opcoes.addLayout(layout_threads)

        layout_gb_scanner.addWidget(gb_opcoes)
        layout_esquerdo.addWidget(gb_scanner)

        # --- Subpainel 2: Scan de IP Público (WAN) ---
        gb_wan = QGroupBox("Scan de IP Público (WAN)")
        layout_gb_wan = QVBoxLayout(gb_wan)

        layout_ip_wan = QHBoxLayout()
        layout_ip_wan.addWidget(QLabel("IP Público:"))
        self.input_ip_publico = QLineEdit()
        self.input_ip_publico.setPlaceholderText("Ex: 200.221.2.45")
        layout_ip_wan.addWidget(self.input_ip_publico)
        layout_gb_wan.addLayout(layout_ip_wan)

        layout_portas_wan = QHBoxLayout()
        layout_portas_wan.addWidget(QLabel("Portas:"))
        self.input_portas_wan = QLineEdit("")
        self.input_portas_wan.setPlaceholderText("Ex: 80, 443, 22-25")
        layout_portas_wan.addWidget(self.input_portas_wan)
        layout_gb_wan.addLayout(layout_portas_wan)

        self.btn_scan_wan = QPushButton("Mapear Portas WAN")
        layout_gb_wan.addWidget(self.btn_scan_wan)

        layout_esquerdo.addWidget(gb_wan)

        # --- Subpainel 3: Mini Terminal (Abaixo do Scan WAN) ---
        gb_terminal = QGroupBox("Terminal")
        layout_gb_terminal = QVBoxLayout(gb_terminal)
        
        self.terminal = TerminalWidget()
        layout_gb_terminal.addWidget(self.terminal)

        layout_esquerdo.addWidget(gb_terminal)

        # =============================================================
        # LADO DIREITO: PAINÉIS DE DISPOSITIVOS E PORTAS
        # =============================================================
        widget_direito = QWidget()
        layout_direito = QVBoxLayout(widget_direito)
        layout_direito.setContentsMargins(5, 0, 5, 0)

        # Painel Superior: Dispositivos LAN
        gb_dispositivos = QGroupBox("Dispositivos LAN")
        layout_gb_disp = QVBoxLayout(gb_dispositivos)

        self.tabela_dispositivos = QTableWidget(0, 6)
        self.tabela_dispositivos.setHorizontalHeaderLabels(
            ["Status", "IP", "Nome", "MAC Address", "Fabricante", "Tempo de resposta"]
        )
        self.tabela_dispositivos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout_gb_disp.addWidget(self.tabela_dispositivos)

        self.lbl_resumo = QLabel("0 Dispositivo(s) encontrado(s)")
        self.lbl_resumo.setStyleSheet("font-weight: bold; padding: 4px; background-color: #D8D8D8;")
        layout_gb_disp.addWidget(self.lbl_resumo)

        layout_direito.addWidget(gb_dispositivos, stretch=1)

        # Painel Inferior: Mapeamento de Portas
        gb_detalhes = QGroupBox("Mapeamento de Portas")
        layout_detalhes_main = QHBoxLayout(gb_detalhes)

        self.tabela_portas = QTableWidget(0, 5)
        self.tabela_portas.setHorizontalHeaderLabels(["Porta", "Protocolo", "Estado", "Serviço", "Versão"])
        self.tabela_portas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout_detalhes_main.addWidget(self.tabela_portas, stretch=2)

        # Detalhes do Alvo
        widget_info = QWidget()
        layout_info = QVBoxLayout(widget_info)
        layout_info.addWidget(QLabel("<b>Detalhes do Alvo:</b>"))
        self.lbl_detalhe_ip = QLabel("IP Alvo: -")
        self.lbl_detalhe_nome = QLabel("Nome: -")
        layout_info.addWidget(self.lbl_detalhe_ip)
        layout_info.addWidget(self.lbl_detalhe_nome)
        layout_info.addStretch()

        layout_detalhes_main.addWidget(widget_info, stretch=1)

        layout_direito.addWidget(gb_detalhes, stretch=1)

        # Splitter Layout
        splitter.addWidget(widget_esquerdo)
        splitter.addWidget(widget_direito)
        splitter.setSizes([340, 860])

        layout_principal.addWidget(splitter)

        # -------------------------------------------------------------
        # 3. BARRA DE STATUS E EVENTOS
        # -------------------------------------------------------------
        self.statusBar().showMessage("Pronto")

        self.btn_init.clicked.connect(self.iniciar_scan)
        self.btn_stop.clicked.connect(self.parar_scan)
        self.btn_scan_wan.clicked.connect(self.iniciar_scan_ip_publico_manual)
        self.tabela_dispositivos.itemDoubleClicked.connect(self.ao_clicar_duplo_dispositivo)

        # =============================================================
        # 4. CONFIGURAÇÃO DO DARK MODE
        # =============================================================
        self.is_dark_mode = False
        self.btn_tema.clicked.connect(self.toggle_theme)

    def toggle_theme(self):
        """Alterna entre o tema claro (padrão) e o tema escuro."""
        self.is_dark_mode = not self.is_dark_mode

        if self.is_dark_mode:
            self.btn_tema.setText("Light Mode")
            dark_style = """
                QWidget { 
                    background-color: #2b2b2b; 
                    color: #ffffff; 
                }
                QTableWidget { 
                    background-color: #3b3b3b; 
                    color: #ffffff; 
                    gridline-color: #555555; 
                }
                QHeaderView::section { 
                    background-color: #1e1e1e; 
                    color: #ffffff; 
                    border: 1px solid #444;
                }
                QPushButton { 
                    background-color: #0078d7; 
                    color: white; 
                    border-radius: 4px; 
                    padding: 5px; 
                }
                QPushButton:hover { 
                    background-color: #005a9e; 
                }
                QPushButton:disabled {
                    background-color: #555555;
                    color: #888888;
                }
                QGroupBox { 
                    border: 1px solid #555555; 
                    margin-top: 15px; 
                    border-radius: 3px;
                }
                QGroupBox::title { 
                    subcontrol-origin: margin; 
                    subcontrol-position: top left;
                    padding: 0 5px; 
                    background-color: #2b2b2b; 
                    color: #ffffff; 
                }
                QLineEdit, QComboBox, QSpinBox {
                    background-color: #3b3b3b;
                    color: #ffffff;
                    border: 1px solid #555555;
                    padding: 2px;
                }
                QCheckBox {
                    color: #ffffff;
                }
            """
            self.setStyleSheet(dark_style)
            self.lbl_resumo.setStyleSheet(
                "font-weight: bold; padding: 4px; background-color: #444444; color: #ffffff;"
            )
        else:
            self.btn_tema.setText("Dark Mode")
            self.setStyleSheet("")
            self.lbl_resumo.setStyleSheet("font-weight: bold; padding: 4px; background-color: #D8D8D8;")

        # Atualiza o terminal com o estado atual do tema
        self.terminal.atualizar_tema(self.is_dark_mode)

    def extrair_lista_portas(self) -> list[int] | None:
        texto = self.input_portas_wan.text().strip()
        if not texto:
            return None

        portas = set()
        partes = texto.split(",")
        for parte in partes:
            parte = parte.strip()
            if "-" in parte:
                try:
                    inicio, fim = parte.split("-")
                    portas.update(range(int(inicio), int(fim) + 1))
                except ValueError:
                    continue
            elif parte.isdigit():
                portas.add(int(parte))

        return sorted(list(portas)) if portas else None

    def iniciar_scan(self):
        ip_de = self.input_ip_de.text().strip()
        ip_ate = self.input_ip_ate.text().strip()
        num_threads = self.spin_threads.value()  # Resgata o valor selecionado na UI

        self.tabela_dispositivos.setRowCount(0)
        self.lbl_resumo.setText("Escaneando a rede...")
        self.btn_init.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.statusBar().showMessage(f"Escaneando faixa {ip_de} até {ip_ate}")

        # Passa o número de threads para o WorkerThread
        self.worker = ICMPWorkerThread(ip_de, ip_ate, num_threads)
        self.worker.concluido.connect(self.ao_concluir_scan)
        self.worker.start()

    def parar_scan(self):
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        if self.worker_wan and self.worker_wan.isRunning():
            self.worker_wan.terminate()
            self.worker_wan.wait()

        self.btn_init.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.btn_scan_wan.setEnabled(True)
        self.statusBar().showMessage("Varredura cancelada.")

    def ao_concluir_scan(self, dispositivos: list[dict]):
        self.btn_init.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.statusBar().showMessage("Pronto")

        self.lbl_resumo.setText(f"{len(dispositivos)} Dispositivo(s) encontrado(s)")

        for item in dispositivos:
            linha = self.tabela_dispositivos.rowCount()
            self.tabela_dispositivos.insertRow(linha)

            self.tabela_dispositivos.setItem(linha, 0, QTableWidgetItem("🟢 Online"))
            self.tabela_dispositivos.setItem(linha, 1, QTableWidgetItem(item.get("ip", "")))
            self.tabela_dispositivos.setItem(linha, 2, QTableWidgetItem(item.get("nome", "-")))
            self.tabela_dispositivos.setItem(linha, 3, QTableWidgetItem(item.get("mac", "-")))
            self.tabela_dispositivos.setItem(linha, 4, QTableWidgetItem(item.get("fabricante", "-")))
            self.tabela_dispositivos.setItem(linha, 5, QTableWidgetItem(item.get("rtt", "")))

    def ao_clicar_duplo_dispositivo(self, item: QTableWidgetItem):
        linha = item.row()
        ip_selecionado = self.tabela_dispositivos.item(linha, 1).text()
        nome_selecionado = self.tabela_dispositivos.item(linha, 2).text()

        self.executar_scan_portas(ip_selecionado, nome_selecionado)

    def iniciar_scan_ip_publico_manual(self):
        ip_publico = self.input_ip_publico.text().strip()
        if not ip_publico:
            self.statusBar().showMessage("Por favor, informe um IP Público válido.")
            return

        self.executar_scan_portas(ip_publico, "IP Público External")

    def executar_scan_portas(self, ip_alvo: str, nome_alvo: str = "-"):
        self.lbl_detalhe_ip.setText(f"IP Alvo: {ip_alvo}")
        self.lbl_detalhe_nome.setText(f"Nome: {nome_alvo}")
        self.tabela_portas.setRowCount(0)

        portas_personalizadas = self.extrair_lista_portas()

        self.btn_scan_wan.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.statusBar().showMessage(f"Escaneando portas em {ip_alvo}...")

        self.worker_wan = WANWorkerThread(ip_alvo, portas_personalizadas)
        self.worker_wan.concluido.connect(self.exibir_portas_abertas)
        self.worker_wan.start()

    def exibir_portas_abertas(self, portas_abertas: list[dict]):
        self.btn_scan_wan.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.statusBar().showMessage("Varredura de portas concluída.")

        self.tabela_portas.setRowCount(0)

        for item in portas_abertas:
            linha = self.tabela_portas.rowCount()
            self.tabela_portas.insertRow(linha)

            self.tabela_portas.setItem(linha, 0, QTableWidgetItem(str(item.get("porta"))))
            self.tabela_portas.setItem(linha, 1, QTableWidgetItem(item.get("protocolo", "TCP")))
            self.tabela_portas.setItem(linha, 2, QTableWidgetItem(item.get("estado", "-")))
            self.tabela_portas.setItem(linha, 3, QTableWidgetItem(item.get("servico", "-")))
            self.tabela_portas.setItem(linha, 4, QTableWidgetItem(item.get("versao", "-")))