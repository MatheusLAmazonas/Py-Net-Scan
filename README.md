# Py-Net-Scan

Integrantes:
Eduardo Luis Franczak,
Kainã Gulecz Czezeski,
Matheus Luiz Amazonas

# Resumo
Esta automação propõe o desenvolvimento de uma plataforma integrada de diagnóstico de rede para técnicos N1/N2, que elimina a dependência de credenciais administrativas em roteadores ao realizar varreduras automáticas para mapear dispositivos conectados, identificando em tempo real informações cruciais como IPs, endereços MAC e hostnames em uma única interface moderna e amigável, otimizando o tempo de resposta e acelerando a resolução de chamados no ambiente corporativo.

# Ferramentas e Tecnologias
<br>**Linguagem:** Python 3.x<br>
**Interface Gráfica (GUI):** PySide6 (Qt para Python)<br>
**Rede e Protocolos:** Socket, Scapy, Asyncio, Ipaddress<br>
**Concorrência:** Threading, Asyncio (I/O assíncrono)<br>
**Requisições:** Requests

# Pré-requisitos do Sistema
<br>**Python 3.10+** instalado.<br>
**Permissões de Administrador / Root:** Necessárias para que bibliotecas de baixo nível (como o *Scapy*) possam enviar e capturar pacotes de rede (ICMP/ARP) na camada de enlace.<br>
**Npcap (Windows) ou libpcap (Linux):** Requerido pelo *Scapy* para manipulação direta de pacotes de rede.

### Módulos Nativos do Python
`socket`, `threading`, `asyncio`, `ipaddress`

# Como Instalar?
```bash
git clone https://github.com/MatheusLAmazonas/Py-Net-Scan.git
cd Py-Net-Scan
pip install -r requirements.txt
python app.py
```
