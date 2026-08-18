from PySide6.QtCore import QThread, Signal
from core.icmp_scanner import escanear_faixa
from core.wan_scanner import escanear_ip_publico

class ICMPWorkerThread(QThread):
    # Sinal emitido ao terminar com a lista de dispositivos encontrados
    concluido = Signal(list)

    def __init__(self, ip_de: str, ip_ate: str):
        super().__init__()
        self.ip_de = ip_de
        self.ip_ate = ip_ate

    def run(self):
        resultados = escanear_faixa(self.ip_de, self.ip_ate)
        self.concluido.emit(resultados)

class WANWorkerThread(QThread):
    concluido = Signal(list)

    def __init__(self, ip_target: str, portas: list[int] = None):
        super().__init__()
        self.ip_target = ip_target
        self.portas = portas

    def run(self):
        # Passa a lista personalizada de portas para a função
        resultados = escanear_ip_publico(self.ip_target, self.portas)
        self.concluido.emit(resultados)
