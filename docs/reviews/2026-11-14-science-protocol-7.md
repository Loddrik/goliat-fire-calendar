# Protocolo 7 — continuidad entre plataformas VIIRS

Auditoría descriptiva fijada antes de desglosar ratios locales o calcular métricas del puente. Las razones anuales regionales ya son conocidas por el método existente; no se presenta esta auditoría como una prueba ciega ni independiente. No se ajusta ningún candidato Aqua con estos resultados.

## Ventanas y datos

- Mantener la grilla y cartografía publicadas y la máscara fija versionada para comparar exactamente la definición operacional vigente, sin añadir otras transformaciones de la iteración 6.
- NOAA-20 frente a S-NPP: temporadas completas 2018–2025 (julio–junio). NOAA-21 frente a NOAA-20: temporadas completas 2023–2025, tras el inicio de archivos disponibles en marzo de 2023. No usar la temporada parcial 2026.
- Verificar por `inventory.csv` que las ventanas solicitadas SP/archivo-país cubren los días de cada período comparado. Eso prueba continuidad de archivos solicitados, **no** oportunidad real de observación. Excluir temporadas con días sin ventana documentada para una de las plataformas y registrar la exclusión. Señalar cualquier celda-día NRT que subsista.
- Las primeras/últimas detecciones seleccionadas no se interpretan como inicio/fin de misión ni como disponibilidad completa. Contar 0 en un archivo no significa ausencia física de fuego.

## Métricas predefinidas

1. Razón comparador/referencia por temporada regional, mes calendario y comuna; denominador cero → no identificable, no cero ni infinito.
2. Sesgo relativo y WAPE mensual emparejado, usando como denominador la suma de celdas-día de referencia. Un cociente de sumas cercano a uno puede coexistir con diferencias locales grandes.
3. Bootstrap de la razón regional por temporadas completas, 5.000 réplicas, semilla 20261114, intervalo percentil. Ocho o tres bloques, respectivamente; no garantía de equivalencia.
4. Todas las comunas se reportan. Un diagnóstico de señal suficiente exige ≥100 celdas-día de referencia en toda la ventana. Señalar razones fuera de [0,8;1,25] en ese grupo; son límites de cribado del proyecto, no estándares NASA ni compuertas de publicación nuevas.
5. Jaccard de celdas-día con detección entre ambas plataformas, regional y por comuna. Es concordancia de detecciones positivas, no precisión/recall frente a verdad de terreno. Diferencias de pasada, geolocalización y observabilidad pueden afectar el solape.

## Salidas y alcance

Directorio nuevo `data/processed/platform_bridge_audit/`: pares mensuales, razones anuales/mensuales/comunales, solape y resumen, con hashes de fuentes, inventario, máscara, código y protocolo. No ajustar factores ni cambiar la regla de plataforma por temporada. Se conservan por hash producción y auditorías anteriores. Tests de períodos julio–junio, empate de calendarios, intervalos solicitados, denominadores cero y solape de conjuntos. PR contra `dev`, con plazo de investigación 21:00 de Santiago.
