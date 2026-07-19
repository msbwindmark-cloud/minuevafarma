import json
import urllib.request
import urllib.parse

CIMA_BASE = "https://cima.aemps.es/cima/rest"


def _get(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "MiNuevaFarma/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def buscar_por_nombre(nombre, pagina=1):
    q = urllib.parse.quote(nombre)
    url = f"{CIMA_BASE}/medicamentos?nombre={q}&pagina={pagina}"
    data = _get(url)
    return data.get("resultados", [])


def ficha_resumida(nombre_o_cn):
    cn = str(nombre_o_cn).strip()
    palabras = cn.split()
    intentos = [cn] + palabras[:2] + ([palabras[0]] if palabras else [])
    for intento in intentos:
        if not intento:
            continue
        try:
            res = buscar_por_nombre(intento, 1)
        except Exception:
            res = []
        if res:
            m = res[0]
            return _procesar_m(m)
    return None


def _procesar_m(m):
    ficha = {
        "nregistro": m.get("nregistro"),
        "nombre": m.get("nombre", ""),
        "labtitular": m.get("labtitular", ""),
        "receta": m.get("receta", False),
        "cpresc": m.get("cpresc", ""),
        "dosis": m.get("dosis", ""),
        "forma": (m.get("formaFarmaceutica") or {}).get("nombre", ""),
        "vtm": (m.get("vtm") or {}).get("nombre", ""),
        "foto": (m.get("fotos") or [{}])[0].get("url", ""),
        "prospecto_html": "",
        "ft_html": "",
        "composicion": m.get("composicion", ""),
        "excipientes": m.get("excipientes", ""),
        "indicaciones": m.get("indicaciones", ""),
        "via_administracion": ", ".join([v.get("nombre", "") for v in m.get("viasAdministracion", [])]),
    }
    for d in m.get("docs", []):
        if d.get("tipo") == 2:
            ficha["prospecto_html"] = d.get("urlHtml", "")
        if d.get("tipo") == 1:
            ficha["ft_html"] = d.get("urlHtml", "")
    return ficha
