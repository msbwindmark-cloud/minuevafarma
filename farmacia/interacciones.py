import requests, logging
logger = logging.getLogger(__name__)
BASE = "https://cima.aemps.es/cima/rest"

def interaccion(nreg1, nreg2):
    try:
        r = requests.get(f"{BASE}/interacciones", params={"nregistro1": nreg1, "nregistro2": nreg2}, timeout=8)
        if r.status_code == 200:
            data = r.json()
            return data
    except Exception as e:
        logger.warning("CIMA interacciones error: %s", e)
    return None

def chequear(cns):
    """Recibe lista de nregistro (cn). Devuelve lista de pares con interaccion."""
    res = []
    cns = [c for c in cns if c]
    for i in range(len(cns)):
        for j in range(i + 1, len(cns)):
            d = interaccion(cns[i], cns[j])
            if d and d.get("interaccion") is not None:
                res.append({
                    "a": cns[i], "b": cns[j],
                    "interaccion": d.get("interaccion"),
                    "nivel": d.get("nivelInteraccion"),
                    "descripcion": d.get("descripcion") or d.get("notas") or "",
                })
    return res
