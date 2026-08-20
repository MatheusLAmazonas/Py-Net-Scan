import asyncio
import re
import socket
import subprocess
import sys
import urllib.request
import uuid

CACHE_FABRICANTES = {}


def obter_ip_local() -> str:
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
    """Obtém o endereço MAC consultando a tabela ARP do SO."""
    if ip == obter_ip_local():
        try:
            mac_num = uuid.getnode()
            mac_hex = f"{mac_num:012X}"
            return ":".join(mac_hex[i : i + 2] for i in range(0, 12, 2))
        except Exception:
            pass

    try:
        output = subprocess.check_output(["arp", "-a"], stderr=subprocess.DEVNULL, text=True)
        for linha in output.splitlines():
            if ip in linha:
                match = re.search(r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})", linha)
                if match:
                    mac_encontrado = match.group(0).upper().replace("-", ":")
                    if mac_encontrado != "FF:FF:FF:FF:FF:FF":
                        return mac_encontrado
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
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=1.0) as response:
            vendor = response.read().decode("utf-8").strip()
            CACHE_FABRICANTES[prefixo] = vendor
            return vendor
    except Exception:
        return "-"


async def _checar_ip_com_ping_async(ip: str) -> bool:
    """Executa um ping assíncrono direcionado ao IP."""
    param_count = "-n" if sys.platform == "win32" else "-c"
    param_wait = "-w" if sys.platform == "win32" else "-W"
    time_val = "300" if sys.platform == "win32" else "1"

    cmd = ["ping", param_count, "1", param_wait, time_val, ip]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL
        )
        res = await asyncio.wait_for(proc.wait(), timeout=0.35)
        return res == 0
    except Exception:
        return False


async def _sondar_ip(ip: str, semaforo_fabricante: asyncio.Semaphore) -> dict | None:
    is_online = await _checar_ip_com_ping_async(ip)

    if not is_online:
        return None

    # Pequena pausa para garantir a atualização da tabela ARP do SO
    await asyncio.sleep(0.05)

    loop = asyncio.get_running_loop()

    # Busca Nome e MAC
    nome_task = loop.run_in_executor(None, _obter_nome_host_sync, ip)
    mac_task = loop.run_in_executor(None, _obter_mac_sync, ip)

    try:
        nome, mac = await asyncio.gather(nome_task, mac_task)
    except Exception:
        nome, mac = "-", "-"

    fabricante = "-"
    if mac != "-":
        # Passa pelo semáforo instanciado dentro do loop ativo
        async with semaforo_fabricante:
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
        "rtt": "< 10 ms",
    }


async def _escanear_async(lista_ips: list[str], max_threads: int = 100) -> list[dict]:
    # Controla o número máximo de requisições simultâneas conforme a escolha da UI
    semaforo_ips = asyncio.Semaphore(max_threads)
    semaforo_fabricante = asyncio.Semaphore(5)

    async def sondar_com_limite(ip):
        async with semaforo_ips:
            return await _sondar_ip(ip, semaforo_fabricante)

    tarefas = [sondar_com_limite(ip) for ip in lista_ips]
    resultados = await asyncio.gather(*tarefas)

    hosts_ativos = [r for r in resultados if r is not None]

    def ip_para_int(item):
        return [int(part) for part in item["ip"].split(".")]

    return sorted(hosts_ativos, key=ip_para_int)


def escanear_faixa(ip_inicio: str, ip_fim: str, max_threads: int = 100) -> list[dict]:
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
        return loop.run_until_complete(_escanear_async(lista_ips, max_threads))
    finally:
        loop.close()