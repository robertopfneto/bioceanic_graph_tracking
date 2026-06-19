"""
dados.py — Dados da Rota Bioceânica de Capricórnio (Rota 4)

Fontes:
    Cidades BR    : IBGE (Instituto Brasileiro de Geografia e Estatística)
    Cidades PY    : MOPC (Ministerio de Obras Públicas y Comunicaciones)
    Cidades AR    : IGN (Instituto Geográfico Nacional Argentina)
    Cidades CL    : IGM (Instituto Geográfico Militar Chile)
    Passos andinos: Vialidad Nacional Argentina / Vialidad Chile
    Distâncias    : Google Maps (modo carro), DNIT, MOPC PY, Vialidad AR/CL
    Data coleta   : junho 2026

"""

from graph import Cidade, Aresta, Grafo


def construir_grafo() -> Grafo:
    grafo = Grafo()

    # ---- VÉRTICES ----
    cidades = [
        # BRASIL
        Cidade("Santos",                    lat=-23.9608, lon=-46.3331, altitude_m=2),
        Cidade("Presidente Epitacio",       lat=-21.7634, lon=-52.1122, altitude_m=261),
        Cidade("Tres Lagoas",               lat=-20.7878, lon=-51.7042, altitude_m=320),
        Cidade("Bataguassu",                lat=-21.7142, lon=-52.4222, altitude_m=329),
        Cidade("Nova Alvorada do Sul",      lat=-21.4658, lon=-54.3831, altitude_m=407),
        Cidade("Campo Grande",              lat=-20.4435, lon=-54.6478, altitude_m=532),
        Cidade("Porto Murtinho",            lat=-21.6978, lon=-57.8794, altitude_m=90),
        # PARAGUAI
        Cidade("Carmelo Peralta",           lat=-21.6883, lon=-57.9014, altitude_m=93),
        Cidade("Loma Plata",                lat=-22.3833, lon=-59.8333, altitude_m=133),
        Cidade("MJF Estigarribia",          lat=-22.0333, lon=-60.6167, altitude_m=163),
        Cidade("Pozo Hondo",                lat=-22.3333, lon=-62.5333, altitude_m=178),
        # ARGENTINA
        Cidade("Mision La Paz",             lat=-22.3789, lon=-62.5186, altitude_m=180),
        Cidade("Pozo de Maza",              lat=-22.9511, lon=-62.6189, altitude_m=152),
        Cidade("Tartagal",                  lat=-22.5164, lon=-63.8014, altitude_m=450),
        Cidade("San Salvador de Jujuy",     lat=-24.1856, lon=-65.2994, altitude_m=1259),
        Cidade("Salta",                     lat=-24.7821, lon=-65.4232, altitude_m=1187),
        Cidade("Susques",                   lat=-23.3972, lon=-66.3681, altitude_m=3620),
        Cidade("Paso de Jama",              lat=-23.2306, lon=-67.0125, altitude_m=4200),
        Cidade("San Antonio de los Cobres", lat=-24.2206, lon=-66.3219, altitude_m=3775),
        Cidade("Paso de Sico",              lat=-23.8869, lon=-67.2917, altitude_m=4079),
        # CHILE
        Cidade("San Pedro de Atacama",      lat=-22.9111, lon=-68.1994, altitude_m=2407),
        Cidade("Calama",                    lat=-22.4547, lon=-68.9292, altitude_m=2260),
        Cidade("Baquedano",                 lat=-23.3333, lon=-69.8333, altitude_m=1030),
        Cidade("Mejillones",                lat=-23.1000, lon=-70.4500, altitude_m=5),
        Cidade("Antofagasta",               lat=-23.6500, lon=-70.4000, altitude_m=15),
        Cidade("Iquique",                   lat=-20.2167, lon=-70.1456, altitude_m=12),
    ]
    for c in cidades:
        grafo.adicionar_cidade(c)

    # ---- ARESTAS (bidirecionais) ----
    # Formato: (origem, destino, dist_km, alt_passo_m ou None)
    arestas = [
        # --- Brasil ---
        Aresta("Santos", "Presidente Epitacio", 635, None),    # SP-270/BR-267
        Aresta("Santos", "Tres Lagoas", 648, None),            # SP-300/BR-262
        Aresta("Presidente Epitacio", "Bataguassu", 36, None), # Ponte Maurício Joppert
        Aresta("Bataguassu", "Nova Alvorada do Sul", 248, None),# BR-267
        Aresta("Nova Alvorada do Sul", "Campo Grande", 121, None),# BR-163
        Aresta("Tres Lagoas", "Campo Grande", 326, None),      # BR-262
        Aresta("Campo Grande", "Porto Murtinho", 438, None),   # BR-060/BR-267
        # --- Fronteira BR/PY ---
        Aresta("Porto Murtinho", "Carmelo Peralta", 3, None),  # Ponte Bioceânica
        # --- Paraguai (Chaco) ---
        Aresta("Carmelo Peralta", "Loma Plata", 277, None),    # Ruta PY15
        Aresta("Carmelo Peralta", "MJF Estigarribia", 295, None),# Ruta alternativa
        Aresta("Loma Plata", "MJF Estigarribia", 101, None),   # Ruta PY09
        Aresta("MJF Estigarribia", "Pozo Hondo", 220, None),   # Ruta PY15
        # --- Fronteira PY/AR ---
        Aresta("Pozo Hondo", "Mision La Paz", 2, None),        # Ponte s/ Pilcomayo


        # --- Argentina ---

        # deslocamento real e não mínimos para refletir um cenário realista
        Aresta("Mision La Paz", "Pozo de Maza", 185, None),     # RP 54
        Aresta("Pozo de Maza", "Tartagal", 335, None),

        # RP54/RN34
        Aresta("Tartagal", "San Salvador de Jujuy", 325, None),# RN34
        Aresta("Tartagal", "Salta", 365, None),                # RN34/RN9
        Aresta("San Salvador de Jujuy", "Salta", 120, None),   # RN9
        Aresta("San Salvador de Jujuy", "Susques", 200, None), # RN52 (via Purmamarca)
        Aresta("Salta", "Susques", 295, None),                 # RN51/RN40
        Aresta("Salta", "San Antonio de los Cobres", 165, None),# RN51
        Aresta("San Antonio de los Cobres", "Paso de Sico", 135, 4079), # RN51 — PASSO SICO
        Aresta("Susques", "Paso de Jama", 155, None),          # RN52
        # --- Fronteira AR/CL (passos andinos) ---
        Aresta("Paso de Jama", "San Pedro de Atacama", 156, 4810), # CH-27 — PASSO JAMA
        # --- Chile ---
        Aresta("San Pedro de Atacama", "Calama", 100, None),   # CH-23
        Aresta("Paso de Sico", "Calama", 215, None),           # Rota via Sico
        Aresta("Calama", "Baquedano", 147, None),              # CH-25
        Aresta("Calama", "Iquique", 387, None),                # CH-24/Ruta 5
        Aresta("Baquedano", "Antofagasta", 73, None),          # Ruta 5
        Aresta("Baquedano", "Mejillones", 60, None),           # Ruta 5/Ruta 1
        Aresta("Mejillones", "Antofagasta", 65, None),         # Ruta 1
        Aresta("Antofagasta", "Iquique", 415, None),           # Ruta 1 (litorânea)
    ]

    for aresta in arestas:
        grafo.adicionar_aresta_bidirecional(aresta)

    return grafo
