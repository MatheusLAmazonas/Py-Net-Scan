import ipaddress


def validar_ip(ip: str) -> tuple[bool, str]:
    """Valida um endereço IPv4.

    Retorna (True, "") se válido, ou (False, mensagem_de_erro) se inválido.
    """
    ip = ip.strip()

    if not ip:
        return False, "O campo de IP não pode estar vazio."

    try:
        ipaddress.IPv4Address(ip)
        return True, ""
    except ValueError:
        return False, f"'{ip}' não é um endereço IPv4 válido (ex: 192.168.1.1)."


def validar_faixa_ip(ip_de: str, ip_ate: str) -> tuple[bool, str]:
    """Valida a faixa de IP inicial/final para o scan LAN.

    Verifica: formato individual de cada IP, mesma sub-rede /24 (os três
    primeiros octetos precisam ser iguais, já que a varredura é feita
    variando apenas o último octeto) e ordem lógica (início <= fim).
    """
    ok_de, msg_de = validar_ip(ip_de)
    if not ok_de:
        return False, f"IP inicial inválido: {msg_de}"

    ok_ate, msg_ate = validar_ip(ip_ate)
    if not ok_ate:
        return False, f"IP final inválido: {msg_ate}"

    octetos_de = ip_de.strip().split(".")
    octetos_ate = ip_ate.strip().split(".")

    if octetos_de[:3] != octetos_ate[:3]:
        return False, (
            "Os IPs 'De' e 'Até' precisam estar na mesma sub-rede "
            f"(ex: {'.'.join(octetos_de[:3])}.1 até {'.'.join(octetos_de[:3])}.254)."
        )

    ultimo_de = int(octetos_de[3])
    ultimo_ate = int(octetos_ate[3])

    if ultimo_de > ultimo_ate:
        return False, (
            "O IP inicial ('De') deve ser menor ou igual ao IP final ('Até'). "
            f"Você informou {ip_de} até {ip_ate}."
        )

    return True, ""


def validar_lista_portas(texto: str) -> tuple[bool, str, list[int]]:
    """Valida a string de portas digitada pelo usuário.

    Aceita números isolados separados por vírgula e intervalos "inicio-fim".
    Retorna (True, "", lista_de_portas) se tudo certo, ou
    (False, mensagem_de_erro, []) se houver qualquer trecho inválido.

    Uma string vazia é considerada válida (o scanner usa a lista padrão de portas).
    """
    texto = texto.strip()
    if not texto:
        return True, "", []

    portas: set[int] = set()
    partes_invalidas: list[str] = []

    for parte_bruta in texto.split(","):
        parte = parte_bruta.strip()
        if not parte:
            continue

        if "-" in parte:
            fragmentos = parte.split("-")
            if len(fragmentos) != 2 or not all(f.strip().isdigit() for f in fragmentos):
                partes_invalidas.append(parte_bruta.strip())
                continue

            inicio, fim = int(fragmentos[0]), int(fragmentos[1])
            if not (0 < inicio <= 65535 and 0 < fim <= 65535):
                partes_invalidas.append(f"{parte_bruta.strip()} (fora do intervalo 1-65535)")
                continue
            if inicio > fim:
                partes_invalidas.append(f"{parte_bruta.strip()} (início maior que o fim)")
                continue

            portas.update(range(inicio, fim + 1))

        elif parte.isdigit():
            valor = int(parte)
            if not (0 < valor <= 65535):
                partes_invalidas.append(f"{parte_bruta.strip()} (fora do intervalo 1-65535)")
                continue
            portas.add(valor)

        else:
            partes_invalidas.append(parte_bruta.strip())

    if partes_invalidas:
        return False, (
            "Entrada de portas inválida: " + ", ".join(partes_invalidas) +
            ". Use números (ex: 80), intervalos (ex: 22-25) separados por vírgula."
        ), []

    if not portas:
        return False, "Nenhuma porta válida foi informada.", []

    return True, "", sorted(portas)