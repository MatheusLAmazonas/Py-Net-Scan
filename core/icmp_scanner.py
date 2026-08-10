import asyncio
import re
import socket
import subprocess
import urllib.request
import uuid

CACHE_FABRICANTES = {}

# Portas padrão de dispositivos locais para contornar o bloqueio de firewall ICMP
PORTAS_DESCOBERTA = [445, 135, 80, 443, 8080, 53, 62078]

def obter_ip_local() -> str:
    """Descobre o IP da máquina local na rede."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
        s.close()
        return ip_local
    except Exception:
        return "127.0.0.1"

def _obter_nome_host_sync(ip: str) -> str:
    try:
        nome, _, _ = socket.gethostbyaddr(ip)
        return nome
    except Exception:
        return "-"

def _obter_mac_sync(ip: str) -> str:
    """Extrai o MAC da tabela ARP local ou da placa de rede própria se for o IP local."""
    # 1. Se for a própria máquina local, pega o MAC via hardware/uuid
    if ip == obter_ip_local():
        try:
            mac_num = uuid.getnode()
            mac_hex = f"{mac_num:012X}"
            return ":".join(mac_hex[i:i+2] for i in range(0, 12, 2))
        except Exception:
            pass

    # 2. Se for outro IP na rede, busca no ARP do SO
    try:
        output = subprocess.check_output(["arp", "-a", ip], stderr=subprocess.DEVNULL, text=True)
        match = re.search(r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})", output)
        if match:
            return match.group(0).upper().replace("-", ":")
    except Exception:
        pass

    return "-"

def _obter_fabricante_sync(mac: str) -> str:
    if mac == "-" or len(mac) < 8:
        return "-"
    
    prefixo = mac[:8].upper()
    if prefixo in CACHE_FABRICANTES:
        return CACHE_FABRICANTES[prefixo]

    try:
        url = f"https://api.macvendors.com/{mac}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=0.8) as response:
            vendor = response.read().decode('utf-8').strip()
            CACHE_FABRICANTES[prefixo] = vendor
            return vendor
    except Exception:
        return "-"

async def _checar_ip_com_ping(ip: str) -> bool:
    """Executa o ping nativo do sistema operacional."""
    loop = asyncio.get_running_loop()
    try:
        cmd = ["ping", "-n", "1", "-w", "500", ip]
        res = await loop.run_in_executor(
            None, 
            lambda: subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
        )
        return res == 0
    except Exception:
        return False

async def _checar_porta_tcp(ip: str, porta: int, timeout: float = 0.2) -> bool:
    """Testa conexões TCP rápidas."""
    try:
        conn = asyncio.open_connection(ip, porta)
        _, writer = await asyncio.wait_for(conn, timeout=timeout)
        writer.close()
        await writer.wait_closed()
        return True
    except Exception:
        return False

async def _sondar_ip(ip: str) -> dict | None:
    """Sonda o IP via Ping e Portas TCP em paralelo."""
    is_online = await _checar_ip_com_ping(ip)
    
    # Se o ping falhou (bloqueio de Firewall), testa portas comuns
    if not is_online:
        tarefas_portas = [_checar_porta_tcp(ip, p) for p in PORTAS_DESCOBERTA]
        resultados = await asyncio.gather(*tarefas_portas)
        if any(resultados):
            is_online = True

    if not is_online:
        return None

    # Se o host está ativo, enriquece com Nome, MAC e Fabricante
    loop = asyncio.get_running_loop()
    
    nome_task = loop.run_in_executor(None, _obter_nome_host_sync, ip)
    mac_task = loop.run_in_executor(None, _obter_mac_sync, ip)

    try:
        nome, mac = await asyncio.gather(nome_task, mac_task)
    except Exception:
        nome, mac = "-", "-"

    fabricante = "-"
    if mac != "-":
        try:
            fabricante = await loop.run_in_executor(None, _obter_fabricante_sync, mac)
        except Exception:
            fabricante = "-"

    return {
        "status": "Online",
        "ip": ip,
        "nome": nome,
        "mac": mac,
        "fabricante": fabricante,
        "rtt": "< 10 ms"
    }

async def _escanear_async(lista_ips: list[str]) -> list[dict]:
    tarefas = [_sondar_ip(ip) for ip in lista_ips]
    resultados = await asyncio.gather(*tarefas)

    hosts_ativos = [r for r in resultados if r is not None]

    def ip_para_int(item):
        return [int(part) for part in item["ip"].split(".")]

    return sorted(hosts_ativos, key=ip_para_int)

def escanear_faixa(ip_inicio: str, ip_fim: str) -> list[dict]:
    """Ponto de entrada chamado por ui/threads.py."""
    try:
        prefixo = ".".join(ip_inicio.split(".")[:3])
        num_inicio = int(ip_inicio.split(".")[3])
        num_fim = int(ip_fim.split(".")[3])
        
        lista_ips = [f"{prefixo}.{i}" for i in range(num_inicio, num_fim + 1)]
    except Exception:
        return []

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_escanear_async(lista_ips))
    finally:
        loop.close()