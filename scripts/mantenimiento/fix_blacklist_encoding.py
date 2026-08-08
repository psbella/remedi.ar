"""mantenimiento/fix_blacklist_encoding.py - Repara el mojibake acumulado en
data/blacklist.json (223 claves, ver AVISO de blacklist.py en el log de CI).

CONTEXTO
--------
Antes del fix de encoding en admin.js (commit 2e1b222), cada vez que se
usaba el panel admin para bloquear un outlier, el ciclo leer-modificar-
escribir releía blacklist.json con un decode incorrecto (atob() tratando
UTF-8 como Latin-1) y volvía a escribir TODO el archivo -- no solo la
entrada nueva. Resultado: claves que sobrevivieron varias corridas del
panel antes del fix acumularon hasta 10 rondas de la misma corrupcion.

Por que este script NO revierte el encoding matematicamente
-------------------------------------------------------------
Se probo invertir la corrupcion aplicando N rondas de
`texto.encode('latin1').decode('utf-8')`. Para la mayoria de las claves
esto converge a texto que ya no dispara el heuristico de blacklist.py,
pero no siempre es el texto correcto: encontramos casos donde el resultado
"limpio" era 'acetilcisteã\xad' na' en lugar de 'acetilcisteina'. El
heuristico de deteccion no distingue una ronda de mas de una reversion
correcta. Por eso NO se usa como estrategia de reparacion aca.

Estrategia real: droga, marca, presentacion y laboratorio para un
medicamento dado son datos deterministicos que ya existen, sin corromper,
en alguna corrida historica de data/medicamentos.json (json generado por
el ETL desde el PDF oficial, nunca tocado por admin.js). Este script
escanea TODO el historial git de medicamentos.json, arma un indice
marca/presentacion/laboratorio -> droga (y variantes con los otros
campos como clave cuando corresponde), y usa ese indice para reconstruir
el campo corrupto de cada entrada de la blacklist.

Solo se corrige una entrada cuando el cruce da un resultado UNICO
(sin ambiguedad). Las entradas sin match o ambiguas se listan al final
para revision manual y blacklist.json queda intacto para esas.

Uso (correr una sola vez desde la raiz del repo):
    python3 scripts/mantenimiento/fix_blacklist_encoding.py
    python3 scripts/mantenimiento/fix_blacklist_encoding.py --aplicar   # escribe blacklist.json

Sin --aplicar hace dry-run: solo imprime el resumen, no modifica nada.
"""

import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BLACKLIST_PATH = REPO_ROOT / "data" / "blacklist.json"
MEDICAMENTOS_PATH = "data/medicamentos.json"


def _parece_corrupta(texto):
    """Mismo heuristico que scripts/etl/blacklist.py, duplicado a proposito
    para no crear un acoplamiento entre un script de uso unico y el ETL."""
    return 'Ã' in texto or 'â€' in texto or any(0x80 <= ord(c) <= 0x9f for c in texto)


def make_key(m):
    """Debe coincidir exactamente con etl/blacklist.py:make_key."""
    return '|'.join([
        (m.get('droga')        or '').strip().lower(),
        (m.get('marca')        or '').strip().lower(),
        (m.get('presentacion') or '').strip().lower(),
        (m.get('laboratorio')  or '').strip().lower(),
    ])


def construir_indices_historicos():
    """Escanea todos los commits que tocaron medicamentos.json y arma
    varios indices para cruzar contra las entradas corruptas de la
    blacklist segun que combinacion de campos este limpia.

    Devuelve un dict de indices, cada uno mapeando una clave compuesta
    (campos limpios, unidos con '|||') a un set de valores candidatos
    para el campo a reconstruir. Un match solo se acepta si el set tiene
    un unico elemento.
    """
    commits = subprocess.run(
        ['git', 'log', '--format=%H', '--', MEDICAMENTOS_PATH],
        cwd=REPO_ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace', check=True
    ).stdout.split()

    print(f"   Escaneando {len(commits)} commits de medicamentos.json...", file=sys.stderr)

    idx_marca_pres_a_droga = defaultdict(set)
    idx_marca_a_droga      = defaultdict(set)
    idx_marca_lab_a_pres_droga = defaultdict(set)
    idx_pres_lab_a_marca_droga = defaultdict(set)

    for c in commits:
        r = subprocess.run(['git', 'show', f'{c}:{MEDICAMENTOS_PATH}'],
                            cwd=REPO_ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
        if r.returncode != 0:
            continue
        try:
            data = json.loads(r.stdout)
        except json.JSONDecodeError:
            continue
        for m in data.get('medicamentos', []):
            marca_u = (m.get('marca') or '').strip().upper()
            pres_l  = (m.get('presentacion') or '').strip().lower()
            lab_l   = (m.get('laboratorio') or '').strip().lower()
            droga_l = (m.get('droga') or '').strip().lower()
            if not marca_u or not droga_l:
                continue
            idx_marca_pres_a_droga[(marca_u, pres_l)].add(droga_l)
            idx_marca_a_droga[marca_u].add(droga_l)
            idx_marca_lab_a_pres_droga[(marca_u, lab_l)].add((pres_l, droga_l))
            idx_pres_lab_a_marca_droga[(pres_l, lab_l)].add((marca_u, droga_l))

    return {
        'marca_pres_a_droga': idx_marca_pres_a_droga,
        'marca_a_droga': idx_marca_a_droga,
        'marca_lab_a_pres_droga': idx_marca_lab_a_pres_droga,
        'pres_lab_a_marca_droga': idx_pres_lab_a_marca_droga,
    }


def _normalizar_ambiguedad_trivial(valores):
    """Si el unico desacuerdo entre los candidatos es un punto final
    (ej. 'ác' vs 'ác.'), se queda con la forma mas larga (con punto).
    Si hay una diferencia real de contenido, no resuelve nada."""
    sin_punto = {v.rstrip('.') for v in valores}
    if len(sin_punto) == 1:
        return max(valores, key=len)
    return None


def reparar(blacklist, indices):
    """Intenta reparar cada entrada corrupta. Devuelve:
    (blacklist_nueva, reparadas, sin_resolver)
    donde blacklist_nueva tiene las claves y los sub-campos ya corregidos
    para las entradas reparadas, y sin_resolver es la lista de claves
    (originales, corruptas) que no se pudieron reconstruir con certeza.
    """
    nueva = {}
    reparadas = []
    sin_resolver = []

    for k, v in blacklist.items():
        if not _parece_corrupta(k):
            nueva[k] = v
            continue

        campos_corruptos = {c for c in ('droga', 'marca', 'presentacion', 'laboratorio')
                             if _parece_corrupta(v.get(c, ''))}

        v2 = dict(v)
        resuelto = False

        if campos_corruptos == {'droga'}:
            marca_u = (v['marca'] or '').strip().upper()
            pres_l  = (v['presentacion'] or '').strip().lower()
            candidatos = indices['marca_pres_a_droga'].get((marca_u, pres_l), set())
            droga = None
            if len(candidatos) == 1:
                droga = next(iter(candidatos))
            elif len(candidatos) > 1:
                droga = _normalizar_ambiguedad_trivial(candidatos)
            if droga:
                v2['droga'] = droga
                resuelto = True

        elif campos_corruptos == {'laboratorio'}:
            marca_u = (v['marca'] or '').strip().upper()
            pres_l  = (v['presentacion'] or '').strip().lower()
            candidatos = indices['marca_pres_a_droga'].get((marca_u, pres_l), set())
            posibles_labs = set()
            for (m_u, lab_l), pares in indices['marca_lab_a_pres_droga'].items():
                if m_u == marca_u and any(p == pres_l for p, _ in pares):
                    posibles_labs.add(lab_l)
            if len(posibles_labs) == 1 and len(candidatos) == 1:
                v2['laboratorio'] = next(iter(posibles_labs))
                v2['droga'] = next(iter(candidatos))
                resuelto = True

        elif campos_corruptos == {'presentacion'}:
            marca_u = (v['marca'] or '').strip().upper()
            lab_l   = (v['laboratorio'] or '').strip().lower()
            pares = indices['marca_lab_a_pres_droga'].get((marca_u, lab_l), set())
            drogas = {d for _, d in pares}
            if len(pares) == 1:
                pres, droga = next(iter(pares))
                v2['presentacion'] = pres
                v2['droga'] = droga
                resuelto = True
            elif len(drogas) == 1 and len(pares) > 1:
                pass

        if resuelto:
            nueva_clave = make_key(v2)
            if nueva_clave in nueva:
                existente = nueva[nueva_clave]
                if (v2.get('bloqueado_en') or '') < (existente.get('bloqueado_en') or ''):
                    nueva[nueva_clave] = v2
            else:
                nueva[nueva_clave] = v2
            reparadas.append((k, nueva_clave, campos_corruptos))
        else:
            nueva[k] = v
            sin_resolver.append((k, campos_corruptos))

    return nueva, reparadas, sin_resolver


def _truncar(s, n=60):
    s = s or ''
    return s if len(s) <= n else s[:n] + f'...[{len(s)} chars]'


def main():
    aplicar = '--aplicar' in sys.argv

    with open(BLACKLIST_PATH, encoding='utf-8') as f:
        blacklist = json.load(f)

    indices = construir_indices_historicos()
    nueva, reparadas, sin_resolver = reparar(blacklist, indices)

    print(f"\nEntradas corruptas totales: {len(sin_resolver) + sum(1 for _ in reparadas)}")
    print(f"Reparadas con certeza: {len(reparadas)}")
    print(f"Sin resolver (revisar a mano): {len(sin_resolver)}")

    if sin_resolver:
        print("\n--- Claves que quedan sin resolver (cadenas truncadas para lectura) ---")
        for k, campos in sin_resolver:
            v = blacklist[k]
            print(f"  campos corruptos: {sorted(campos)}")
            print(f"    marca={_truncar(v.get('marca'))!r} "
                  f"presentacion={_truncar(v.get('presentacion'))!r} "
                  f"laboratorio={_truncar(v.get('laboratorio'))!r}")

    if aplicar:
        with open(BLACKLIST_PATH, 'w', encoding='utf-8') as f:
            json.dump(nueva, f, ensure_ascii=False, indent=2, sort_keys=True)
        print(f"\n{BLACKLIST_PATH} actualizado ({len(reparadas)} entradas corregidas).")
    else:
        print("\nDry-run (no se escribio nada). Correr con --aplicar para guardar los cambios.")


if __name__ == '__main__':
    main()
