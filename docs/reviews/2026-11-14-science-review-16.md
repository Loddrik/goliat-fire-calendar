# Revisión 16 — el cero aislado aporta poco

Protocolo fijado antes de medir: [protocolo 16](2026-11-14-science-protocol-16.md). Evaluación retrospectiva adaptativa; no nuevo holdout ni validación de incendios físicos. Unidad: celdas-día diurnas registradas por S-NPP agregadas por comuna y mes.

## Resultado principal

Sobre 5.184 filas, B tiene MAE 1,903194. Forzar cero cuando Aqua=0 conservando exactamente su selección y regularización da 1,903515: empeora un 0,017 %. El sesgo pasa de −0,0872 a −0,2737. Esta ablación no demuestra una mejora por tratar el cero como ausencia de actividad.

El gate elegido internamente sin cambiar regularización logra 1,893888 (0,489 %). Reescoger también la regularización logra 1,871937 (1,642 %), pero mezcla dos cambios y no debe atribuirse al gate aislado. B/P guardado tiene 1,883928; la diferencia adicional es pequeña.

| Bloque | B | Z misma regularización | Gate interno fijo | Gate y regularización |
|---|---:|---:|---:|---:|
| Nested 2012–2019 | 1,903194 | 1,903515 | 1,893888 | 1,871937 |
| Transporte 4 adelante | 2,239129 | 2,228578 | 2,231438 | 2,201971 |
| Transporte 4 atrás | 1,861186 | 1,863672 | 1,857615 | 1,859407 |
| Transporte 6 adelante | 1,931063 | 1,918398 | 1,913306 | 1,889143 |
| Transporte 6 atrás | 1,716298 | 1,732249 | 1,716714 | 1,715779 |
| 2020–2021 descriptivo | 1,960280 | 2,005916 | 1,962473 | 1,958901 |
| 2022–2025 descriptivo | 2,374788 | 2,358676 | 2,367022 | 2,360695 |

El oráculo retrospectivo restringido a elegir entre cero y B únicamente cuando Aqua=0 llega a MAE 1,822128. Su ganancia máxima de 0,081066 no es un modelo y no limita métodos que cambien cantidades positivas. Utiliza etiquetas de destino exclusivamente para cuantificar ese techo optimista.

## Integridad y decisión

Se reprodujeron controles previos a tolerancia 1e-10, con máscaras y ajustes dentro de cada origen: 64 ajustes nested, 24 de transporte y uno completo. El modelo completo se congeló antes de consultar destinos posteriores, ya explorados previamente. Se verificó que Z conserve exactamente las predicciones positivas de B y que la inferencia no dependa de etiquetas de destino.

No promover. Conservar el resultado negativo aislado y distinguirlo de la ganancia del paquete con regularización. No sumar sus porcentajes a los del modelo de dos partes: compiten en la misma población. Publicación M1/14 y datos base permanecen protegidos.

Los manifiestos, selecciones, estratos, predicciones y contrastes completos están en `data/processed/zero_anchor_audit/`. Las pruebas sintéticas específicas son seis; el conjunto de las etapas 16–17 y preflight anónimo pasó 119 pruebas antes de incorporar el acceso autenticado.
