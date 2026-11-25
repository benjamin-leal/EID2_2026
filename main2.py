import os
import sys
import matplotlib.pyplot as plt

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

USAR_COLOR = sys.stdout.isatty()
if USAR_COLOR and os.name == "nt":
    os.system("")

RUT_POR_DEFECTO = "22.735.368-6"
EQUIPO = "Grupo 1"

TEMA = {
    "fondo": "#0B1020",
    "panel": "#121A33",
    "texto": "#E8ECF8",
    "suave": "#8F9BBF",
    "rejilla": "#26324F",
    "curvas": ["#FF6B9D", "#4DE1C1", "#FFC857"],
}

CODIGOS = {
    "negrita": "1",
    "rojo": "31",
    "verde": "32",
    "amarillo": "33",
    "magenta": "35",
    "cian": "36",
    "gris": "90",
}

CASOS = ["A", "B", "C"]
NOMBRES = {
    "A": "WiFi estándar",
    "B": "Fibra con reintentos decrecientes",
    "C": "Red móvil con copia extra",
}
C_MAX = 10
K_TABLA = 10
K_LIMITE = 3000
TOL_CONV = 1e-9
ANCHO_PANTALLA = 82


def pintar(texto, *estilos):
    if not USAR_COLOR or not estilos:
        return texto
    codigo = ";".join(CODIGOS[e] for e in estilos)
    return f"\033[{codigo}m{texto}\033[0m"


def celda(texto, ancho, alineacion="<", *estilos):
    return pintar(f"{texto:{alineacion}{ancho}}", *estilos)


def borde(anchos, izquierda, union, derecha):
    return izquierda + union.join("─" * (a + 2) for a in anchos) + derecha


def fila_caja(celdas):
    return "│ " + " │ ".join(celdas) + " │"


def banner(titulo, subtitulo):
    interior = ANCHO_PANTALLA - 2
    print(pintar("╔" + "═" * interior + "╗", "cian", "negrita"))
    print(pintar("║", "cian", "negrita") + pintar(titulo.center(interior), "negrita") + pintar("║", "cian", "negrita"))
    print(pintar("║", "cian", "negrita") + pintar(subtitulo.center(interior), "gris") + pintar("║", "cian", "negrita"))
    print(pintar("╚" + "═" * interior + "╝", "cian", "negrita"))


def seccion(texto):
    print()
    print(pintar("▌ ", "magenta", "negrita") + pintar(texto.upper(), "negrita"))
    print(pintar("  " + "─" * (ANCHO_PANTALLA - 4), "gris"))


def recuadro(titulo, lineas, estilo):
    ancho = max(max(len(l) for l in lineas) + 2, len(titulo) + 5)
    print(pintar("╭─ " + titulo + " " + "─" * (ancho - len(titulo) - 3) + "╮", estilo, "negrita"))
    for l in lineas:
        print(pintar("│", estilo) + " " + l.ljust(ancho - 2) + " " + pintar("│", estilo))
    print(pintar("╰" + "─" * ancho + "╯", estilo, "negrita"))


def barra(valor, largo=22):
    escala = C_MAX * 2
    llenos = round(min(valor, escala) / escala * largo)
    return "█" * llenos + "░" * (largo - llenos)


def extraer_digitos(rut):
    digitos = []
    for c in rut:
        if c in "0123456789":
            digitos.append(int(c))
    return digitos[:8]


def calcular_probabilidades(rut):
    d = extraer_digitos(rut)
    p1 = (d[0] + d[2] + d[4] + 1) * 2 / 100
    p2 = (d[1] + d[3] + d[5] + 1) * 3 / 100
    p3 = (d[6] + d[7] + 1) * 4 / 100
    return [p1, p2, p3]


def sumas_parciales(caso, p, k_max):
    q = 1 - p
    potencia = 1.0
    acumulado = 0.0
    sumas = []
    for i in range(1, k_max + 1):
        if caso == "A":
            termino = i * potencia * p
        elif caso == "B":
            termino = potencia * p / i
        else:
            termino = (i + 1) * potencia * p
        acumulado += termino
        sumas.append(acumulado)
        potencia *= q
    return sumas


def analizar_convergencia(sumas):
    ultima = abs(sumas[-1] - sumas[-2])
    anterior = abs(sumas[-2] - sumas[-3])
    converge = ultima < TOL_CONV and anterior < TOL_CONV
    return converge, sumas[-1]


def k_estable(sumas, limite, tolerancia_relativa):
    margen = tolerancia_relativa * limite
    for k in range(1, len(sumas) + 1):
        if abs(sumas[k - 1] - limite) <= margen:
            return k
    return len(sumas)


def imprimir_tablas(rut, probs, series):
    banner("EVALUACIÓN INTEGRADA DE DESEMPEÑO N°2", "MATE1133 · Límites, Sucesiones y Series")
    seccion("Datos de entrada")
    d = extraer_digitos(rut)
    print(f"  RUT utilizado   {pintar(rut, 'amarillo', 'negrita')}")
    print("  Dígitos d1..d8  " + pintar("  ".join(str(x) for x in d), "cian"))
    for j in range(3):
        print(f"  p{j + 1} = {pintar(format(probs[j], '.4f'), 'verde', 'negrita')}")

    anchos = [14, 14, 14]
    sangria = " " * 8
    for caso in CASOS:
        seccion(f"Tabla caso {caso} · {NOMBRES[caso]}")
        print(sangria + borde(anchos, "┌", "┬", "┐"))
        encabezado = [celda(f"p{j + 1} = {probs[j]:.4f}", anchos[j], "^", "negrita", "cian") for j in range(3)]
        print(sangria + fila_caja(encabezado))
        print(sangria + borde(anchos, "├", "┼", "┤"))
        for k in range(K_TABLA):
            etiqueta = pintar(f"{'S' + str(k + 1):>6}  ", "gris")
            fila = [celda(f"{series[(caso, j)][k]:.6f}", anchos[j], ">") for j in range(3)]
            print(etiqueta + fila_caja(fila))
        print(sangria + borde(anchos, "└", "┴", "┘"))


def imprimir_convergencia(resultados):
    seccion("Convergencia y límite empírico")
    print(pintar(f"  k = {K_LIMITE} términos · tolerancia {TOL_CONV}", "gris"))
    anchos = [5, 12, 13, 16, 9]
    titulos = ["Caso", "p", "Estado", "Límite empírico", "k estable"]
    print(borde(anchos, "┌", "┬", "┐"))
    print(fila_caja([celda(t, a, "^", "negrita", "cian") for t, a in zip(titulos, anchos)]))
    for caso in CASOS:
        print(borde(anchos, "├", "┼", "┤"))
        for j in range(3):
            r = resultados[(caso, j)]
            if r["converge"]:
                estado = celda("✔ converge", anchos[2], "^", "verde", "negrita")
            else:
                estado = celda("✘ diverge", anchos[2], "^", "rojo", "negrita")
            print(fila_caja([
                celda(caso, anchos[0], "^", "amarillo", "negrita"),
                celda(f"p{j + 1} = {r['p']:.4f}", anchos[1], "^"),
                estado,
                celda(f"{r['limite']:.6f}", anchos[3], ">"),
                celda(str(r["k_estable"]), anchos[4], ">"),
            ]))
    print(borde(anchos, "└", "┴", "┘"))


def grafico_estilizado(caso, probs, series, limites):
    k_1pct = [k_estable(series[j], limites[j], 0.01) for j in range(3)]
    k_graf = min(max(20, int(max(k_1pct) * 1.35)), K_LIMITE)
    ks = list(range(1, k_graf + 1))
    y_tope = max(limites) * 1.18
    orden = sorted(range(3), key=lambda j: -limites[j])
    saltos = [8, -18, -32]

    fig, ax = plt.subplots(figsize=(11, 6.6))
    fig.patch.set_facecolor(TEMA["fondo"])
    ax.set_facecolor(TEMA["panel"])

    for j in range(3):
        color = TEMA["curvas"][j]
        y = series[j][:k_graf]
        for grosor, opacidad in ((9, 0.06), (5.5, 0.12)):
            ax.plot(ks, y, color=color, linewidth=grosor, alpha=opacidad, solid_capstyle="round")
        ax.plot(ks, y, color=color, linewidth=2.3, solid_capstyle="round",
                label=f"p{j + 1} = {probs[j]:.4f}  ·  límite {limites[j]:.4f}  ·  k ≈ {k_1pct[j]}")
        ax.fill_between(ks, y, color=color, alpha=0.06)
        ax.axhline(limites[j], color=color, linestyle=(0, (6, 4)), linewidth=1.1, alpha=0.85)
        if k_1pct[j] <= k_graf:
            ax.scatter([k_1pct[j]], [series[j][k_1pct[j] - 1]], s=75, color=TEMA["fondo"],
                       edgecolor=color, linewidth=2, zorder=5)
        ax.annotate(f"límite p{j + 1} = {limites[j]:.4f}", xy=(k_graf, limites[j]),
                    xytext=(-8, saltos[orden.index(j)]), textcoords="offset points",
                    ha="right", fontsize=9.5, fontweight="bold", color=color)

    ax.scatter([], [], s=60, color=TEMA["fondo"], edgecolor=TEMA["texto"], linewidth=1.8,
               label="punto donde la curva queda a menos del 1 % de su límite")

    ax.set_xlim(1, k_graf)
    ax.set_ylim(0, y_tope)
    ax.grid(True, color=TEMA["rejilla"], linewidth=0.7, alpha=0.8)
    ax.set_axisbelow(True)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(TEMA["rejilla"])
    ax.tick_params(colors=TEMA["suave"], labelsize=9)
    ax.set_xlabel("k  (términos acumulados)", color=TEMA["suave"], fontsize=10, labelpad=8)
    ax.set_ylabel("S_k  (costo esperado parcial)", color=TEMA["suave"], fontsize=10, labelpad=8)

    ax.legend(loc="lower right", frameon=True, facecolor=TEMA["fondo"], edgecolor=TEMA["rejilla"],
              labelcolor=TEMA["texto"], fontsize=8.6)

    fig.text(0.06, 0.945, f"Caso {caso} · {NOMBRES[caso]}", color=TEMA["texto"],
             fontsize=18, fontweight="bold", ha="left")
    fig.text(0.06, 0.903, "Sumas parciales S_k y el valor límite al que se estabiliza cada curva",
             color=TEMA["suave"], fontsize=10.5, ha="left")
    fig.text(0.97, 0.018, f"EID N°2 · MATE1133 · {EQUIPO}", color=TEMA["suave"], fontsize=8, ha="right")
    fig.subplots_adjust(left=0.08, right=0.97, top=0.86, bottom=0.11)
    fig.savefig(f"grafico_caso_{caso}.png", dpi=160, facecolor=fig.get_facecolor())
    return fig


def tabla_viabilidad(resultados):
    seccion(f"Tabla de viabilidad · C máx = {C_MAX} transmisiones esperadas")
    anchos = [5, 12, 14, 12, 24]
    titulos = ["Caso", "p", "Límite", "¿Cumple?", "Costo  (mitad = C máx)"]
    print(borde(anchos, "┌", "┬", "┐"))
    print(fila_caja([celda(t, a, "^", "negrita", "cian") for t, a in zip(titulos, anchos)]))
    for caso in CASOS:
        print(borde(anchos, "├", "┼", "┤"))
        for j in range(3):
            r = resultados[(caso, j)]
            cumple = r["converge"] and r["limite"] <= C_MAX
            estilo = "verde" if cumple else "rojo"
            texto = "✔ SÍ" if cumple else "✘ NO"
            print(fila_caja([
                celda(caso, anchos[0], "^", "amarillo", "negrita"),
                celda(f"p{j + 1} = {r['p']:.4f}", anchos[1], "^"),
                celda(f"{r['limite']:.4f}", anchos[2], ">"),
                celda(texto, anchos[3], "^", estilo, "negrita"),
                celda(barra(r["limite"]), anchos[4], "<", estilo),
            ]))
    print(borde(anchos, "└", "┴", "┘"))


def recomendar(resultados):
    seccion("Recomendación")
    viables = []
    for caso in CASOS:
        for j in range(3):
            r = resultados[(caso, j)]
            if r["converge"] and r["limite"] <= C_MAX:
                viables.append((r["limite"], r["k_estable"], caso, j))
    if len(viables) == 0:
        recuadro("Sin recomendación", [
            "Ninguna combinación cumple el umbral C máx.",
            "No hay una combinación recomendable para este sistema.",
        ], "rojo")
        return
    viables.sort()
    limite, k_est, caso, j = viables[0]
    r = resultados[(caso, j)]
    lineas = [
        f"Caso {caso} ({NOMBRES[caso]}) con p{j + 1} = {r['p']:.4f}",
        "",
        "Justificación:",
        f"  • La serie converge: la diferencia entre S_k y S_(k-1) es menor que {TOL_CONV}",
        f"    al final de {K_LIMITE} términos.",
        f"  • Su límite empírico es {limite:.4f}, y cumple el umbral C máx = {C_MAX}.",
        f"  • Entre las {len(viables)} combinaciones que cumplen el umbral, es la de menor costo esperado.",
        f"  • Se estabiliza (a menos del 1 % de su límite) desde k = {k_est} términos.",
    ]
    recuadro("Combinación recomendada", lineas, "verde")


def leer_rut():
    print(pintar("  Al presionar Enter se aplica el RUT por defecto de un compañero del grupo: ", "gris") + pintar(RUT_POR_DEFECTO, "amarillo", "negrita"))
    try:
        texto = input(pintar("Ingrese el RUT elegido: ", "cian")).strip()
    except EOFError:
        texto = ""
    if texto == "":
        print(pintar("Se aplicó el RUT por defecto de un compañero del grupo.", "amarillo"))
        return RUT_POR_DEFECTO
    if len(extraer_digitos(texto)) < 8:
        print(pintar("El RUT debe tener al menos 8 dígitos. Se aplicó el RUT por defecto de un compañero del grupo.", "amarillo"))
        return RUT_POR_DEFECTO
    return texto


def main():
    rut = leer_rut()
    print()
    probs = calcular_probabilidades(rut)

    series = {}
    resultados = {}
    for caso in CASOS:
        for j in range(3):
            sumas = sumas_parciales(caso, probs[j], K_LIMITE)
            converge, limite = analizar_convergencia(sumas)
            series[(caso, j)] = sumas
            resultados[(caso, j)] = {
                "p": probs[j],
                "converge": converge,
                "limite": limite,
                "k_estable": k_estable(sumas, limite, 0.01),
            }

    imprimir_tablas(rut, probs, series)
    imprimir_convergencia(resultados)

    for caso in CASOS:
        series_caso = [series[(caso, j)] for j in range(3)]
        limites_caso = [resultados[(caso, j)]["limite"] for j in range(3)]
        grafico_estilizado(caso, probs, series_caso, limites_caso)

    tabla_viabilidad(resultados)
    recomendar(resultados)
    print()
    print(pintar("  Gráficos guardados: grafico_caso_A.png · grafico_caso_B.png · grafico_caso_C.png", "gris"))
    plt.show()


if __name__ == "__main__":
    main()