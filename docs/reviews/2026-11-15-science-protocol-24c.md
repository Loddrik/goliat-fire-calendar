# Protocolo24C — sensibilidad del modelo congelado al contrato

Congelación antes de nuevas métricas. Cap absoluto: inicio2026-11-15T04:29:28Z, fin2026-11-15T05:29:28Z, incluida revisión; no reiniciable.

## Pregunta y estimando

¿Cambia Δ=MAE(E_coherent)−MAE(M1_B) al sustituir conjuntamente input Aqua y target NOAA20 de contrato científico C a contrato publicado O? Unidad: comuna-mes celda-día; 54 comunas×64 meses=3456 filas, dominio20A Jul2020–Dic2025 excluyendo Ago/Sep2020, definido por archivo disponible, nunca actividad. No nuevos fits ni selección de modelos. Contratos son representaciones, no verdad física; no se valida transporte SNP→NOAA20.

Primaria: ΔOO−ΔCC y extremos CC/OO, agregación MAE por fila. τ=.01 MAE(B_CC), calculada sólo tras pasar identidades y siempre reportada. Materialidad |ΔOO−ΔCC|≥τ es regla de trabajo, no significación. Toda inversión de signo se registra; inversión material sólo si ambos |Δ|>τ. No promoción ni elección de contrato por ganador.

## Entradas y gates no compensables

Leer sólo artefactos existentes, sin credenciales ni descargas. Panel19 paired_predictions.parquet, panel20A contract_counts.parquet, predicciones18 later_predictions.parquet y modelo17 hurdle_audit/frozen_model.json. Modelo/hash17 y artefactos18/19/20A deben concordar con sus manifests. Preservar hashes de entradas/modelos/código/publicación antes y después.

Validar separadamente las54CSV publicadas Aqua y NOAA20: hash/tamaño/filas, CUT/nombre, plataforma/instrumento, día, confianza y type0, fuente inventariada/año, cuadrícula publicada reproducida. Aqua requiere MODIS, satellite Aqua, confianza numérica≥30; NOAA20 VIIRS/N20, n/h. No reutilizar sin adaptación el validador NOAA20 para Aqua. Validar además hash de geometría/manifest/índice/publicaciones, series mensuales detecciones y celdas-día de cada CSV contra observed-monthly.json y publicación por comuna. Null o falta de mes no es cero. Exigir exactamente3456 claves idénticas con ambos O disponibles; NOAA20 O igual O0 de20A, NOAA20 C igual Cmaskedall/19, Aqua C igual18/19. Recomputar modelo congelado sobre AquaC con estimate_frozen y extend; exigir los seis métodos igual18/19 en mismas filas, tolerancia1e-10 absoluta para estimaciones, claves y conteos exactos. Si cualquier gate falla: salida bloqueada, diagnóstico, sin pérdidas/rankings.

## Cálculo congelado

Congelar hashes de código/inputs y pruebas sintéticas antes de métricas. Recalcular seis funciones fijas M1, M1_B, E11_10, E_mean, E_coherent y E_proportional sobre AquaC y AquaO, sin tocar coeficientes/CDF/políticas17. Cada reconciliación/presupuesto propio ΣB usa las54 comunas antes de filtrar. κ10, sin grillas. Inputs de predicción exclusivamente CUT/season/m/g/aqua; labels no entran en modelo ni solver. Prueba de eliminar/cambiar target produce predicciones idénticas. Verificar suma, no negatividad, KKT y riesgo esperado≤B como18.

Factorial CC/CO/OC/OO (primera letra input Aqua; segunda target NOAA20), seis métodos secundarios si cabe dentro cap completo con revisión. CO/OC son diagnósticos mezclados, no productos coherentes nuevos. Primaria siempre coherente−B, sin elegir ranking.

Reportar all54/publicadas14/restantes40, sesgo y MAE regional (igualdad de presupuesto construida). Estratos pareados fijos definidos sobre YC: todos, YC=0, YC>0, YC≥50, AquaC=0 con YC>0, ambosC0. YC≥50 es extremo primario; YO≥50 sólo suplementario con tamaños/intersección/entradas/salidas, nunca población equivalente. Guardar resultados completos incluso adversos.

## Cotas y separación de ejes

Con input/predicciones/filas fijos, |ΔtargetO−ΔtargetC|≤2 mean|YC−YO|; global20A debe reproducir440/3456. Subgrupos/estratos necesitan sus propias cotas, nunca reutilizar440/3456. Con target fijo, |ΔinputO−ΔinputC|≤mean|EcohC−EcohO|+mean|BC−BO|, usando presupuestos propios. Verificar desigualdades numéricas y publicar componentes. No atribución causal de discrepancias al sensor, QA o fuego; no suma de porcentajes entre estudios.

## Salidas, pruebas y stop

Own pipeline/contract_model_sensitivity_audit.py, tests/test_contract_model_sensitivity_audit.py, data/processed/contract_model_sensitivity_audit/, docs/reviews/2026-11-15-science-review-24c.md. Pruebas sintéticas: validador Aqua/NOAA20 y rechazo plataforma/confianza/type/bytes, faltante no-cero, identidades fallo cerrado, población YC fija frente movimientosYO, cotas y materialidad incluidos límites estrictos de inversión.

Primera entrega≤60min con revisión. Si identidad falla: detener comparaciones. Si sensibilidad pequeña: cerrar hipótesis contractual acotada y continuarB, no descartar observabilidad. Si cambio material/perjuicio territorial: documentar dependencia/estimando, no elegir contrato favorable. Si cap o inconcluso: preservar gates/límites y cerrar, sin ampliar infraestructura, sin cambios de producción.23 primario negativo se conserva. G1 físico false; ninguna evidencia nueva es holdout fresco.
