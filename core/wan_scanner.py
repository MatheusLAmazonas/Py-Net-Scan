import asyncio
import socket

PORTAS_PADRAO = [
    21, 22, 23, 25, 53, 80, 110, 139, 143, 443, 445, 
    1433, 1521, 3306, 3389, 5432, 5900, 8080, 8443, 8888
]

async def _testar_porta_tcp(ip: str, porta: int, timeout: float = 1.0) -> dict:
    """Tenta conectar na porta e define o estado como Aberta ou Fechada/Bloqueada."""
    try:
        servico = socket.getservbyport(porta, "tcp")
    except Exception:
        servico = "desconhecido"

    try:
        conn = asyncio.open_connection(ip, porta)
        reader, writer = await asyncio.wait_for(conn, timeout=timeout)
        writer.close()
        await writer.wait_closed()

        return {
            "porta": porta,
            "protocolo": "TCP",
            "estado": "🟢 Aberta",
            "servico": servico,
            "versao": "-"
        }
    except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
        return {
            "porta": porta,
            "protocolo": "TCP",
            "estado": "🔴 Fechada / Bloqueada",
            "servico": servico,
            "versao": "-"
        }

async def _escanear_portas_async(ip: str, portas: list[int] = None) -> list[dict]:
    if portas is None:
        portas = PORTAS_PADRAO

    tarefas = [_testar_porta_tcp(ip, porta) for porta in portas]
    resultados = await asyncio.gather(*tarefas)

    return sorted(resultados, key=lambda x: x["porta"])

def escanear_ip_publico(ip: str, portas: list[int] = None) -> list[dict]:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_escanear_portas_async(ip, portas))
    finally:
        loop.close()