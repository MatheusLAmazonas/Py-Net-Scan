from PySide6.QtCore import Qt
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
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ui.threads import ICMPWorkerThread


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyNetScan")
        self.resize(1200, 700)

        self.worker = None

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

        self.btn_init = QPushButton("▶ Iniciar")
        self.btn_stop = QPushButton("■ Parar")
        self.btn_stop.setEnabled(False)

        self.btn_init.setFixedSize(90, 32)
        self.btn_stop.setFixedSize(90, 32)

        layout_topo.addWidget(self.btn_init)
        layout_topo.addWidget(self.btn_stop)
        layout_topo.addStretch()

        layout_principal.addWidget(painel_topo)

        # -------------------------------------------------------------
        # 2. CONTEÚDO PRINCIPAL (SPLITTER ESQUERDA / DIREITA)
        # -------------------------------------------------------------
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # =============================================================
        # LADO ESQUERDO: PAINEL DE PARÂMETROS / SCANNER
        # =============================================================
        widget_esquerdo = QWidget()
        layout_esquerdo = QVBoxLayout(widget_esquerdo)
        layout_esquerdo.setContentsMargins(5, 0, 5, 0)

        # --- Subpainel: Scanner ---
        gb_scanner = QGroupBox("Scanner")
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

        # Opções
        gb_opcoes = QGroupBox("Opções")
        layout_opcoes = QVBoxLayout(gb_opcoes)

        self.chk_tcp = QCheckBox("Verificar portas (TCP)")
        self.chk_tcp.setChecked(True)
        layout_opcoes.addWidget(self.chk_tcp)

        layout_portas = QHBoxLayout()
        layout_portas.addWidget(QLabel("Portas comuns:"))
        self.input_portas = QLineEdit("80,443,22,8080")
        layout_portas.addWidget(self.input_portas)
        layout_opcoes.addLayout(layout_portas)

        self.chk_ping = QCheckBox("Ping antes do scan")
        self.chk_ping.setChecked(True)
        layout_opcoes.addWidget(self.chk_ping)

        self.chk_dns = QCheckBox("Resolver nomes (DNS)")
        self.chk_dns.setChecked(True)
        layout_opcoes.addWidget(self.chk_dns)

        layout_threads = QHBoxLayout()
        layout_threads.addWidget(QLabel("Threads:"))
        self.spin_threads = QSpinBox()
        self.spin_threads.setRange(1, 500)
        self.spin_threads.setValue(100)
        layout_threads.addWidget(self.spin_threads)
        layout_opcoes.addLayout(layout_threads)

        layout_gb_scanner.addWidget(gb_opcoes)

        # Perfil de Scan
        gb_perfil = QGroupBox("Perfil de Scan")
        layout_perfil = QVBoxLayout(gb_perfil)

        self.combo_perfil = QComboBox()
        self.combo_perfil.addItems(["Padrão", "Rápido", "Completo (Nmap)"])
        layout_perfil.addWidget(self.combo_perfil)

        layout_btn_perfil = QHBoxLayout()
        self.btn_salvar_perfil = QPushButton("Salvar")
        self.btn_remover_perfil = QPushButton("Remover")
        layout_btn_perfil.addWidget(self.btn_salvar_perfil)
        layout_btn_perfil.addWidget(self.btn_remover_perfil)
        layout_perfil.addLayout(layout_btn_perfil)

        layout_gb_scanner.addWidget(gb_perfil)
        layout_esquerdo.addWidget(gb_scanner)

        # =============================================================
        # LADO DIREITO: ABAS, TABELAS E DETALHES
        # =============================================================
        widget_direito = QWidget()
        layout_direito = QVBoxLayout(widget_direito)
        layout_direito.setContentsMargins(5, 0, 5, 0)

        # Abas Superiores
        self.tabs = QTabWidget()

        # Aba 1: Dispositivos
        tab_dispositivos = QWidget()
        layout_tab_disp = QVBoxLayout(tab_dispositivos)

        self.tabela_dispositivos = QTableWidget(0, 6)
        self.tabela_dispositivos.setHorizontalHeaderLabels(
            ["Status", "IP", "Nome", "MAC Address", "Fabricante", "Tempo de resposta"]
        )
        self.tabela_dispositivos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout_tab_disp.addWidget(self.tabela_dispositivos)

        self.lbl_resumo = QLabel("0 Dispositivo(s) encontrado(s)")
        self.lbl_resumo.setStyleSheet("font-weight: bold; padding: 4px; background-color: #D8D8D8;")
        layout_tab_disp.addWidget(self.lbl_resumo)

        # Adicionando abas ao QTabWidget
        self.tabs.addTab(tab_dispositivos, "Dispositivos")
        self.tabs.addTab(QWidget(), "Portas")
        self.tabs.addTab(QWidget(), "Mapa de rede")

        layout_direito.addWidget(self.tabs)

        # Painel Inferior: Detalhes de Portas e Serviços
        gb_detalhes = QGroupBox("Portas e Serviços")
        layout_detalhes_main = QHBoxLayout(gb_detalhes)

        # Tabela de Portas do Host Selecionado
        self.tabela_portas = QTableWidget(0, 5)
        self.tabela_portas.setHorizontalHeaderLabels(["Porta", "Protocolo", "Estado", "Serviço", "Versão"])
        self.tabela_portas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout_detalhes_main.addWidget(self.tabela_portas, stretch=2)

        # Área de Texto/Informações Adicionais
        widget_info = QWidget()
        layout_info = QVBoxLayout(widget_info)
        layout_info.addWidget(QLabel("<b>Detalhes do serviço:</b>"))
        self.lbl_detalhe_ip = QLabel("IP: -")
        self.lbl_detalhe_nome = QLabel("Nome: -")
        layout_info.addWidget(self.lbl_detalhe_ip)
        layout_info.addWidget(self.lbl_detalhe_nome)
        layout_info.addStretch()

        layout_detalhes_main.addWidget(widget_info, stretch=1)

        layout_direito.addWidget(gb_detalhes)

        # Adiciona lado esquerdo e direito ao Splitter
        splitter.addWidget(widget_esquerdo)
        splitter.addWidget(widget_direito)
        splitter.setSizes([320, 880])

        layout_principal.addWidget(splitter)

        # -------------------------------------------------------------
        # 3. BARRA DE STATUS E EVENTOS
        # -------------------------------------------------------------
        self.statusBar().showMessage("Pronto")

        # Conectar eventos de botões
        self.btn_init.clicked.connect(self.iniciar_scan)
        self.btn_stop.clicked.connect(self.parar_scan)

    def iniciar_scan(self):
        ip_de = self.input_ip_de.text().strip()
        ip_ate = self.input_ip_ate.text().strip()

        # Reseta a interface
        self.tabela_dispositivos.setRowCount(0)
        self.lbl_resumo.setText("Escaneando a rede...")
        self.btn_init.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.statusBar().showMessage(f"Escaneando faixa {ip_de} até {ip_ate}...")

        # Dispara o escaneamento na thread
        self.worker = ICMPWorkerThread(ip_de, ip_ate)
        self.worker.concluido.connect(self.ao_concluir_scan)
        self.worker.start()

    def parar_scan(self):
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
            self.ao_concluir_scan([])
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