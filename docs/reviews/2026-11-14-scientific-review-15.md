# Revisión científica 15 — ajuste directo de extremos de intervalo

El ajuste directo reduce la pérdida frente a los cuantiles asimétricos empíricos en las ocho temporadas, para ambos puntos y cohortes. No domina la referencia simétrica/activa en todos los destinos ni establece cobertura garantizada. Mantener publicación M1 y 14 compuertas.

[Protocolo fijado antes de resultados](2026-11-14-science-protocol-15.md). Se mantienen los puntos M1 y M1/B, escala raíz y α=0,2. El optimizador resuelve los puntos de quiebre de la pérdida con clipping y restricciones de orden, sin malla arbitraria. Las calibraciones usan exclusivamente predicciones de origen; la temporada externa no participa.

## Resultado anidado principal

54 comunas, 5.184 pares. Menor IS es mejor. Cobertura es proporción empírica frente a S-NPP, no probabilidad certificada de incendios.

| Punto | Cohorte de calibración | Ajuste | IS todos los meses | Cobertura | Anchura |
| --- | --- | --- | ---: | ---: | ---: |
| M1 | active | empirical_quantiles | 11.84473 | 82.81 % | 6.68686 |
| M1 | all_months | empirical_quantiles | 11.89671 | 81.54 % | 5.04888 |
| M1_B | active | empirical_quantiles | 10.70195 | 81.31 % | 5.80594 |
| M1_B | all_months | empirical_quantiles | 10.63431 | 80.07 % | 4.45642 |
| M1 | active | minimum_interval_score | 9.66984 | 88.52 % | 6.68146 |
| M1 | all_months | minimum_interval_score | 9.25677 | 87.83 % | 5.87560 |
| M1_B | active | minimum_interval_score | 9.43924 | 88.52 % | 6.28520 |
| M1_B | all_months | minimum_interval_score | 9.08305 | 87.71 % | 5.52113 |
| M1 | active | symmetric_active_reference | 10.01052 | 90.22 % | 6.42373 |
| M1_B | active | symmetric_active_reference | 9.34861 | 88.93 % | 5.58815 |

El ajuste IS supera a su control empírico de igual cohorte en 8/8 temporadas, también al medir solo meses activos. Esos contrastes son retrospectivos dentro de un desarrollo adaptativo; no constituyen validación independiente. El mínimo de entrenamiento es esperable por construcción, mientras que los valores de esta tabla provienen de los folds externos.

Para M1/B, IS óptimo con todos los meses reduce IS global 10,63431→9,08305 frente al empírico, pero su cobertura activa es 75,81 %, frente a 82,17 % al calibrar solo activos. La referencia simétrica/activa obtiene IS global 9,34861 y cobertura activa 78,31 %. El ajuste activo IS alcanza IS activo 15,99931 y cobertura 82,17 %, con anchura activa 10,15804 frente a 8,94065 de la referencia: la mejora exige intervalos más anchos en esa población. No elegir la cohorte al conocer la actividad del destino.

## Transporte posterior descriptivo

M1/B IS global de la referencia simétrica/activa frente al ajuste IS/todos: 10,01800 frente a 10,06561 en 2020–2021 y 12,34151 frente a 12,07790 en 2022–2025. La primera comparación empeora y la segunda mejora. Los períodos posteriores ya fueron consultados; se conservan la exclusión agosto/septiembre 2020 y la transición enero–junio 2022. No se reajusta con esas etiquetas.

## Controles, límites y reproducción

85 tests Python pasan. Los seis controles empíricos/asimétricos y simétricos/activos reproducen los resultados anteriores a tolerancia 1e-10 tanto anidados como posteriores. Tests adicionales comparan el óptimo con enumeración exhaustiva y perturbaciones, verifican clipping/orden/desempate, preservan calibración desconocida cuando no hay activos y prueban que cambiar o eliminar las etiquetas futuras no altera extremos.

Se guardan 51.840 intervalos anidados y 37.800 posteriores, 64 llamadas de ajuste puntual, extremos por fold y finales, pérdidas de calibración, diez combinaciones completas, contrastes por temporada y manifiesto en `data/processed/interval_loss_fit_audit/`. Se congela la calibración antes de leer el destino. La firma del modelo puntual anterior y los hashes de datos, publicación y etapas anteriores permanecen idénticos.

La optimización no mide oportunidad de observación ni convierte cero detecciones en ausencia física. No produce conteos de incendios, alertas o pronósticos. El método es candidato experimental; hace falta una prueba futura predefinida y evaluación de observabilidad para promoverlo.

```sh
uv run python -m unittest discover -s tests
uv run python pipeline/interval_loss_fit_audit.py
```
