import matplotlib.pyplot as plt


CASOS = ["A", "B", "C"]
NOMBRES = {
    "A": "WiFi estandar",
    "B": "Fibra con reintentos decrecientes",
    "C": "Red movil con copia extra",
}
COLORES = ["tab:blue", "tab:orange", "tab:green"]
C_MAX = 10
K_TABLA = 10
K_LIMITE = 3000
TOL_CONV = 1e-9
RUT_POR_DEFECTO = "24.365.895-K"


def linea(texto="", caracter="=", largo=78):
    if texto == "":
        print(caracter * largo)
    else:
        print(f" {texto} ".center(largo, caracter))


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


def logaritmo_natural(x):
    z = (x - 1) / (x + 1)
    z2 = z * z
    potencia = z
    total = 0.0
    n = 0
    while n < 100000:
        termino = potencia / (2 * n + 1)
        total += termino
        if abs(termino) < 1e-16:
            break
        potencia *= z2
        n += 1
    return 2 * total


def limite_teorico(caso, p):
    if caso == "A":
        return 1 / p
    if caso == "B":
        return -p * logaritmo_natural(p) / (1 - p)
    return 1 / p + 1


def imprimir_tablas(rut, probs, series):
    linea("DATOS DE ENTRADA")
    print(f"RUT utilizado : {rut}")
    d = extraer_digitos(rut)
    print("Digitos d1..d8: " + ", ".join(str(x) for x in d))
    for j in range(3):
        print(f"p{j + 1} = {probs[j]:.4f}")
    print()
    for caso in CASOS:
        linea(f"TABLA CASO {caso}: {NOMBRES[caso]}")
        print(f"{'k':>4} | " + " | ".join(f"{'p' + str(j + 1) + '=' + format(probs[j], '.2f'):>14}" for j in range(3)))
        print("-" * 5 + "+" + "+".join(["-" * 16] * 3))
        for k in range(K_TABLA):
            fila = " | ".join(f"{series[(caso, j)][k]:>14.6f}" for j in range(3))
            print(f"{'S' + str(k + 1):>4} | {fila}")
        print()


def imprimir_convergencia(probs, resultados):
    linea("CONVERGENCIA Y LIMITE EMPIRICO")
    print(f"(k = {K_LIMITE} terminos, tolerancia = {TOL_CONV})")
    print()
    print(f"{'Caso':<5}{'p':<10}{'Converge':<10}{'Limite empirico':>17}{'Limite teorico':>16}{'Diferencia':>14}{'k (error<1e-6)':>16}")
    print("-" * 88)
    for caso in CASOS:
        for j in range(3):
            r = resultados[(caso, j)]
            texto = "SI" if r["converge"] else "NO"
            teorico = limite_teorico(caso, r["p"])
            diferencia = abs(r["limite"] - teorico)
            print(f"{caso:<5}{'p' + str(j + 1) + '=' + format(r['p'], '.2f'):<10}{texto:<10}{r['limite']:>17.6f}{teorico:>16.6f}{diferencia:>14.2e}{r['k_estable']:>16}")
        print()


def grafico_matplotlib(caso, probs, series, limites):
    k_graf = 20
    for j in range(3):
        k_aprox = k_estable(series[j], limites[j], 0.01)
        if k_aprox * 1.3 > k_graf:
            k_graf = int(k_aprox * 1.3)
    if k_graf > K_LIMITE:
        k_graf = K_LIMITE

    ks = list(range(1, k_graf + 1))
    orden = sorted(range(3), key=lambda j: -limites[j])
    desplazamientos = [6, -14, -28]

    fig, ax = plt.subplots(figsize=(10, 6))
    for j in range(3):
        color = COLORES[j]
        ax.plot(ks, series[j][:k_graf], color=color, linewidth=2,
                label=f"p{j + 1} = {probs[j]:.2f}  (limite = {limites[j]:.4f})")
        ax.axhline(limites[j], color=color, linestyle="--", linewidth=1.2)
        ax.annotate(f"limite p{j + 1} = {limites[j]:.4f}",
                    xy=(k_graf, limites[j]),
                    xytext=(-6, desplazamientos[orden.index(j)]),
                    textcoords="offset points",
                    ha="right", color=color, fontsize=9)

    ax.set_title(f"Caso {caso}: {NOMBRES[caso]}")
    ax.set_xlabel("k (numero de terminos)")
    ax.set_ylabel("S_k (suma parcial)")
    ax.set_xlim(1, k_graf)
    ax.set_ylim(0, max(limites) * 1.15)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(f"grafico_caso_{caso}.png", dpi=150)
    return fig


def tabla_viabilidad(resultados):
    linea(f"TABLA DE VIABILIDAD (C_max = {C_MAX} transmisiones esperadas)")
    print(f"{'Caso':<6}{'p':<10}{'Converge':<10}{'Limite empirico':>17}{'Cumple (<= C_max)':>20}")
    print("-" * 63)
    for caso in CASOS:
        for j in range(3):
            r = resultados[(caso, j)]
            cumple = r["converge"] and r["limite"] <= C_MAX
            texto = "SI" if cumple else "NO"
            conv = "SI" if r["converge"] else "NO"
            print(f"{caso:<6}{'p' + str(j + 1) + '=' + format(r['p'], '.2f'):<10}{conv:<10}{r['limite']:>17.4f}{texto:>20}")
        print()


def recomendar(resultados):
    linea("RECOMENDACION")
    viables = []
    for caso in CASOS:
        for j in range(3):
            r = resultados[(caso, j)]
            if r["converge"] and r["limite"] <= C_MAX:
                viables.append((r["limite"], r["k_estable"], caso, j))
    if len(viables) == 0:
        print("Ninguna combinacion cumple el umbral C_max. No hay combinacion recomendable.")
        print()
        return
    mejor = viables[0]
    for v in viables:
        if v[0] < mejor[0] or (v[0] == mejor[0] and v[1] < mejor[1]):
            mejor = v
    limite, k_est, caso, j = mejor
    r = resultados[(caso, j)]
    print(f"Combinacion recomendada: Caso {caso} ({NOMBRES[caso]}) con p{j + 1} = {r['p']:.2f}")
    print()
    print("Justificacion:")
    print(f"  - La serie converge: la diferencia entre S_k y S_(k-1) es menor que {TOL_CONV} al final de {K_LIMITE} terminos.")
    print(f"  - Su limite empirico es {limite:.4f}, que cumple el umbral C_max = {C_MAX}.")
    print(f"  - Entre las {len(viables)} combinaciones que cumplen el umbral, es la de menor costo esperado.")
    print(f"  - Se estabiliza (error menor a 1e-6) desde k = {k_est} terminos.")
    print(f"  - Coincide con el limite teorico {limite_teorico(caso, r['p']):.4f}.")
    print()
    print("Combinaciones que no cumplen el umbral:")
    hay_no_viables = False
    for c in CASOS:
        for jj in range(3):
            rr = resultados[(c, jj)]
            if not (rr["converge"] and rr["limite"] <= C_MAX):
                hay_no_viables = True
                print(f"  - Caso {c}, p{jj + 1} = {rr['p']:.2f}: limite {rr['limite']:.4f} > {C_MAX}")
    if not hay_no_viables:
        print("  (ninguna)")
    print()


def leer_rut():
    try:
        texto = input(f"Ingrese el RUT elegido (Enter para usar {RUT_POR_DEFECTO}): ").strip()
    except EOFError:
        texto = ""
    if texto == "":
        return RUT_POR_DEFECTO
    if len(extraer_digitos(texto)) < 8:
        print("El RUT debe tener al menos 8 digitos. Se usa el RUT por defecto.")
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
                "k_estable": k_estable(sumas, limite, 1e-6),
            }

    imprimir_tablas(rut, probs, series)
    imprimir_convergencia(probs, resultados)

    for caso in CASOS:
        series_caso = [series[(caso, j)] for j in range(3)]
        limites_caso = [resultados[(caso, j)]["limite"] for j in range(3)]
        grafico_matplotlib(caso, probs, series_caso, limites_caso)

    tabla_viabilidad(resultados)
    recomendar(resultados)

    print("Graficos guardados: grafico_caso_A.png, grafico_caso_B.png, grafico_caso_C.png")
    plt.show()


if __name__ == "__main__":
    main()