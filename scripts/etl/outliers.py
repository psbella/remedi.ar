"""etl/outliers.py - Deteccion de precios outlier/obsoletos y calculo de vigencia."""

import re
import json
import statistics
from collections import defaultdict
from datetime import datetime

from .config import OUTLIER_CONFIG, OUTLIER_REPORT, AR_TZ


# ─────────────────────────────────────────────────────────────────────────────
# DETECCION DE OUTLIERS
# ─────────────────────────────────────────────────────────────────────────────
def calcular_stats_por_droga(medicamentos):
    """Agrupa los precios validos (>0) por droga y calcula mediana, cuartiles
    y el fence inferior de Tukey (q1 - IQR_FACTOR * iqr) para cada grupo.
    Devuelve un dict {droga: stats} usado como base para evaluar_outlier.
    """
    grupos = defaultdict(list)
    for m in medicamentos:
        droga  = (m.get('droga') or '').strip().lower()
        precio = m.get('precio')
        if droga and precio and precio > 0:
            grupos[droga].append(precio)

    stats = {}
    for droga, precios in grupos.items():
        n        = len(precios)
        mediana  = statistics.median(precios)
        sorted_p = sorted(precios)
        q1  = statistics.median(sorted_p[:n // 2])     if n >= 2 else sorted_p[0]
        q3  = statistics.median(sorted_p[(n+1) // 2:]) if n >= 2 else sorted_p[-1]
        iqr = q3 - q1
        stats[droga] = {
            "n":         n,
            "mediana":   round(mediana, 2),
            "q1":        round(q1, 2),
            "q3":        round(q3, 2),
            "iqr":       round(iqr, 2),
            "fence_low": round(q1 - OUTLIER_CONFIG["IQR_FACTOR"] * iqr, 2),
        }
    return stats

def evaluar_outlier(med, stats_droga):
    """Evalua un medicamento contra las stats de su droga (ver
    calcular_stats_por_droga) y devuelve (score, flags, tipo, razones).
    Un precio invalido o <= 0 se marca directo como outlier. Los demas
    casos se comparan contra el precio minimo absoluto, un umbral critico
    respecto a la mediana, un umbral relativo y el fence de Tukey.
    """
    precio   = med.get('precio')
    droga    = (med.get('droga') or '').strip().lower()
    flags    = []
    score    = OUTLIER_CONFIG["SCORE_NORMAL"]
    tipo     = None
    razones  = []

    if not precio or precio <= 0:
        return OUTLIER_CONFIG["SCORE_OUTLIER"], ['precio_obsoleto'], 'invalido', ['precio_invalido_o_cero']

    stats    = stats_droga.get(droga, {})
    n        = stats.get("n", 0)
    mediana  = stats.get("mediana", 0)
    fence_lw = stats.get("fence_low", 0)

    if precio < OUTLIER_CONFIG["PRECIO_MINIMO_ARS"]:
        flags.append('precio_bajo')
        score = min(score, 45)
        tipo  = tipo or 'bajo_absoluto'
        razones.append(f"precio ${precio:,.2f} < minimo ${OUTLIER_CONFIG['PRECIO_MINIMO_ARS']:,}")

    if mediana > 0 and precio < mediana * OUTLIER_CONFIG["UMBRAL_CRITICO"]:
        flags.append('precio_obsoleto')
        score = min(score, OUTLIER_CONFIG["SCORE_OUTLIER"])
        tipo  = 'bajo_critico'
        razones.append(f"precio ${precio:,.2f} < 10% mediana ${mediana:,.2f}")

    elif n >= OUTLIER_CONFIG["MIN_REGISTROS"] and mediana > 0:
        if precio < mediana * OUTLIER_CONFIG["UMBRAL_RELATIVO"]:
            flags.append('precio_sospechoso')
            score = min(score, 35)
            tipo  = tipo or 'bajo_relativo'
            razones.append(f"precio ${precio:,.2f} < 25% mediana ${mediana:,.2f} (n={n})")
        elif fence_lw > 0 and precio < fence_lw:
            flags.append('precio_sospechoso')
            score = min(score, 40)
            tipo  = tipo or 'bajo_iqr'
            razones.append(f"precio ${precio:,.2f} < fence_low ${fence_lw:,.2f}")

    return score, flags, tipo, razones

def detectar_escala(medicamentos, stats_droga):
    """Detecta inconsistencias de escala dentro de una misma droga+marca:
    agrupa por precio-por-unidad (ppu = precio / cantidad extraida de la
    presentacion) y marca como sospechosos los registros cuyo ppu es menos
    del 20% de la mediana del grupo (ej. un envase mal cargado con la
    cantidad de otra presentacion). Modifica medicamentos in-place y
    devuelve la cantidad de registros marcados.
    """
    def extraer_cant(pres):
        nums = re.findall(r'\b(\d+)\b', str(pres or ''))
        return int(nums[0]) if nums else None

    grupos = defaultdict(list)
    for i, m in enumerate(medicamentos):
        droga  = (m.get('droga') or '').strip().lower()
        marca  = (m.get('marca') or '').strip().upper()
        precio = m.get('precio')
        cant   = extraer_cant(m.get('presentacion'))
        if precio and precio > 0 and cant and cant > 0:
            grupos[(droga, marca)].append({'idx': i, 'precio': precio, 'cantidad': cant, 'ppu': precio / cant})

    marcados = 0
    for items in grupos.values():
        if len(items) < 2:
            continue
        med_ppu = statistics.median([it['ppu'] for it in items])
        if med_ppu <= 0:
            continue
        for item in items:
            if item['ppu'] < med_ppu * 0.20:
                m = medicamentos[item['idx']]
                if 'precio_obsoleto' not in m.get('flags', []):
                    m.setdefault('flags', [])
                    if 'precio_sospechoso' not in m['flags']:
                        m['flags'].append('precio_sospechoso')
                    m['vigencia_score'] = min(m.get('vigencia_score', 100), 35)
                    m.setdefault('outlier_razones', []).append(
                        f"ppu ${item['ppu']:,.2f} << mediana_grupo ${med_ppu:,.2f}"
                    )
                    if not m.get('precio_outlier_tipo'):
                        m['precio_outlier_tipo'] = 'inconsistencia_escala'
                    marcados += 1
    return marcados

def calcular_vigencia(medicamentos):
    """Orquesta el calculo de vigencia completo: stats por droga, evaluacion
    de outlier por registro (evaluar_outlier) y deteccion de inconsistencias
    de escala (detectar_escala). Escribe el reporte de outliers en
    OUTLIER_REPORT y devuelve la lista de medicamentos con vigencia_score,
    flags, precio_outlier_tipo y outlier_razones seteados.
    """
    print("\nCalculando estadisticas de outliers...")
    stats = calcular_stats_por_droga(medicamentos)
    print(f"   {len(stats)} drogas distintas")

    for m in medicamentos:
        score, flags, tipo, razones = evaluar_outlier(m, stats)
        m['vigencia_score']      = score
        m['flags']               = flags
        m['precio_outlier_tipo'] = tipo
        m['outlier_razones']     = razones

    n_escala = detectar_escala(medicamentos, stats)

    outliers = [m for m in medicamentos if m.get('flags')]
    reporte  = {
        "timestamp":       datetime.now(AR_TZ).isoformat(),
        "total_registros": len(medicamentos),
        "total_outliers":  len(outliers),
        "outliers": [
            {
                "droga":             m.get('droga'),
                "marca":             m.get('marca'),
                "presentacion":      m.get('presentacion'),
                "laboratorio":       m.get('laboratorio'),
                "precio":            m.get('precio'),
                "precio_outlier_tipo": m.get('precio_outlier_tipo'),
                "razones":           m.get('outlier_razones', []),
                "mediana_droga":     stats.get((m.get('droga') or '').strip().lower(), {}).get('mediana'),
                "n_droga":           stats.get((m.get('droga') or '').strip().lower(), {}).get('n'),
            }
            for m in outliers
        ]
    }

    OUTLIER_REPORT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTLIER_REPORT, 'w', encoding='utf-8') as f:
        json.dump(reporte, f, ensure_ascii=False, indent=2)

    total    = len(medicamentos)
    criticos = [o for o in reporte['outliers'] if o['precio_outlier_tipo'] == 'bajo_critico']
    print(f"\nOUTLIERS: {len(outliers)}/{total} ({100*len(outliers)/total:.1f}%) | Escala: +{n_escala} | Criticos: {len(criticos)}")
    for o in sorted(criticos, key=lambda x: x['precio'] or 0)[:10]:
        print(f"   {o['marca']} ({o['droga']}): ${o['precio']:,.2f}  [mediana: ${o['mediana_droga']:,.2f}]")
    print(f"   Reporte: {OUTLIER_REPORT}")

    return medicamentos

