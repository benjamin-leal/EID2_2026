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


# =====================================================================
# PERSONA 1: nucleo matematico y tablas (puntos 1 y 2)
# =====================================================================

def extraer_digitos(rut):
    # TODO: devolver lista con los primeros 8 digitos del RUT (sin puntos ni guion)
    return [0, 0, 0, 0, 0, 0, 0, 0]


def calcular_probabilidades(rut):
    # TODO: calcular p1, p2, p3 con las formulas del enunciado
    # Prueba: con "24.365.895-K" debe dar [0.22, 0.57, 0.60]
    return [0.1, 0.2, 0.3]


def sumas_parciales(caso, p, k_max):
    # TODO: devolver la lista [S1, S2, ..., S_kmax] para el caso "A", "B" o "C"
    # A: i*(1-p)**(i-1)*p    B: (1/i)*(1-p)**(i-1)*p    C: (i+1)*(1-p)**(i-1)*p
    return [0.0] * k_max


def imprimir_tablas(rut, probs, series):
    # TODO: imprimir el RUT usado, los digitos, p1, p2, p3 y las 3 tablas
    # (una por caso, columnas p1 p2 p3, filas S1..S10)
    # series[(caso, j)] es la lista de sumas parciales del caso y la probabilidad j (0, 1, 2)
    print("TODO: imprimir_tablas")


# =====================================================================
# PERSONA 2: convergencia y graficos con matplotlib (puntos 3 y 4)
# =====================================================================

def analizar_convergencia(sumas):
    # TODO: devolver (converge: bool, limite_empirico: float)
    # Idea: converge si |S_k - S_(k-1)| < TOL_CONV al final de la lista
    return False, 0.0


def k_estable(sumas, limite, tolerancia_relativa):
    # TODO: devolver el primer k donde |S_k - limite| <= tolerancia_relativa * limite
    return len(sumas)


def imprimir_convergencia(probs, resultados):
    # TODO: para cada una de las 9 combinaciones imprimir si converge y su limite
    # resultados[(caso, j)] = {"p": ..., "converge": ..., "limite": ..., "k_estable": ...}
    print("TODO: imprimir_convergencia")


def grafico_matplotlib(caso, probs, series, limites):
    # TODO: con matplotlib, graficar S_k vs k con las 3 curvas (una por probabilidad)
    # y una linea horizontal punteada (axhline) en el limite de cada curva con su valor anotado.
    # Guardar con fig.savefig(f"grafico_caso_{caso}.png") y devolver la figura.
    # series[j] es la lista de sumas de la probabilidad j; limites[j] su limite
    print(f"TODO: grafico_matplotlib caso {caso}")
    return None


# =====================================================================
# PERSONA 3: viabilidad, recomendacion y programa principal (punto 5)
# =====================================================================

def logaritmo_natural(x):
    # TODO (opcional): ln(x) hecho a mano, para el limite teorico del caso B
    return 0.0


def limite_teorico(caso, p):
    # A: 1/p    B: -p*ln(p)/(1-p)    C: 1/p + 1
    return 0.0


def tabla_viabilidad(resultados):
    # TODO: tabla de 9 filas (caso, p, limite, cumple <= C_MAX)
    print("TODO: tabla_viabilidad")


def recomendar(resultados):
    # TODO: recomendar una combinacion (caso y p) y justificarla con la convergencia
    print("TODO: recomendar")


def leer_rut():
    try:
        texto = input(f"Ingrese el RUT elegido (Enter para usar {RUT_POR_DEFECTO}): ").strip()
    except EOFError:
        texto = ""
    if texto == "":
        return RUT_POR_DEFECTO
    return texto


def main():
    rut = leer_rut()
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

    plt.show()


if __name__ == "__main__":
    main()