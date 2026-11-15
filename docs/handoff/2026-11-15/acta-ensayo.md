# Acta de comprobación local para el presentador

**15 de noviembre de 2026, aproximadamente 13:54–13:59 UTC / 10:54–10:59 Santiago.** Operador: coordinador automatizado, con navegador aislado. Modalidad: build local y lectura de rutas/exportación; no ensayo humano cronometrado. Presentador y responsable receptor de release aún deben asignarse.

## Versión y alcance

Se construyó la aplicación con `npm --prefix web run build`: TypeScript y Vite terminaron con salida 0. El código de `web`, `server.mjs`, `package.json` y `package-lock.json` no tiene diferencias contra `6410fcb491e9a318419d7b142ddab52b1e483662`, candidato de PR64. La rama de entrega añade documentación y un renderer; no modifica esa aplicación ni sus JSON. Las dependencias raíz que faltaban se instalaron con `npm ci --ignore-scripts`, sin cambiar el lockfile.

Se inició `PORT=3999 node server.mjs` y se abrió `http://127.0.0.1:3999`. `/health` respondió `{"ok":true,"version":"local"}`. La respuesta no contiene un commit y no se usa para atribuir un despliegue. El commit de código se identifica por la comparación Git anterior y por los hashes del [recibo de ensayo](evidence/demo-receipt.json). Los checks históricos de ese commit están en el [recibo de CI](evidence/verification-snapshot.json).

## Recorrido efectivamente comprobado

| Paso | Ruta local | Resultado visto |
| --- | --- | --- |
| Tomé habilitada | `/explorar?cut=08111&lang=es` | Encabezado Tomé, datos hasta 13-11-2026, calendario/resumen y texto «Serie 2002–2026: observada desde 2012, aproximada antes». Mapa con atribución OpenFreeMap visible en esta sesión con red. |
| Tabla y exportación | `/explorar?cut=08111&lang=es&vista=tabla` | Calendario 2002–2026, leyendas «Observado» y «Aproximado», botón CSV. Descarga real de 293 filas: 120 `estimated` y 173 `observed`, con procedencia, fecha de corte y factor. |
| Concepción no habilitada | `/explorar?cut=08101&lang=es` | Encabezado Concepción y texto «Serie observada 2012–2026; antes de 2012 sin estimación». Conserva observaciones y exportaciones. |
| Historial por plataforma | `/explorar?cut=08111&lang=es&view=observed` | «Integridad SHA-256 verificada», archivo DPA 2023, selector de plataformas y leyenda explícita de valores no armonizados. Rango NOAA-20 mostrado 2018-04 → 2025-12. |

Se guardaron [captura de Tomé](evidence/demo-tome.png), [tabla de Tomé](evidence/demo-tome-table.png), [Concepción](evidence/demo-concepcion.png) y el [CSV descargado](evidence/demo-tome.csv). Las capturas son respaldo del candidato local, no prueba del sitio público ni del funcionamiento sin red.

## Afirmaciones que sí están listas para el guion

| Afirmación | Fuente y límite |
| --- | --- |
| El producto comprende 54 comunas. | Índice publicado y resumen técnico; no cobertura mundial. |
| La reconstrucción se habilita en 14. | Gates publicados; decisión mensual del proyecto, no certificación anual. |
| M1 usa un factor regional cercano a 2,35. | Método y parámetros; no equivalencia universal de instrumentos. |
| Detección y celda-día no cuentan incendios individuales. | Método, leyenda y metadatos CSV. |
| Un cero registrado no prueba ausencia de fuego. | Contratos e historia observada; falta denominador de observación útil. |
| E_coherent redujo MAE 12,18 % frente a M1 en el mismo panel de 5.184 filas. | Etapa 18; retrospectivo, con costes territoriales, no sustitución publicada. |
| El diagnóstico estacional tiene mediana APE 20,34 % y media relativa firmada −11,46 %. | Etapa 42, 112 casos aparentes después de selección; no MARE ni validación histórica. |
| F21 mostró una comparación favorable de CRPS. | Etapa 39; mismo mes histórico y referencia S-NPP, sin pronóstico futuro ni calibración demostrada. |
| Se recuperaron 956/1.071 originales exactos. | Manifest y verificador; ingestión/cartografía integral siguen sin reproducirse y el estricto conserva una fila distinta por lado. |
| CI del candidato pasó 358 tests. | Recibo identificado de PR64; controles de software, sin inferir despliegue o verdad física. |

Las fuentes detalladas y sus hashes están en [el mapa técnico](evidence/technical-source-map.json) y [el mapa de negocio](evidence/business-source-map.json). El estado de los PR corresponde a la consulta fechada del inventario.

## Qué falta confirmar con el equipo

El presentador debe recorrer el guion de tres minutos en su propia máquina y conexión, identificar la versión pública si decide usarla y comprobar la descarga. Si falla el mapa externo, mostrar calendario/tabla y las capturas atribuidas a esta versión. No se simuló un corte de red ni se verificó producción en esta comprobación.

El tar raw permanece en custodia local: `nasa/backups/goliat-raw-recovery-20261115-1327.tar`, SHA-256 `32bf13a8cdaceb5daade86baf648d0a3aec9471d5ea9e77e702a432d51aef0e1`. No se afirma transferencia al equipo receptor. La disponibilidad parcial no bloquea leer los JSON de la demo.

Los informes HTML se comprobaron en navegador a 390 y 1440 píxeles: las ocho combinaciones no tuvieron desbordamiento de página, IDs duplicados, fragmentos internos rotos ni dependencias HTML externas. Véase [acta de layout](evidence/html-browser-check.json). Es un control de layout, no una auditoría exhaustiva de accesibilidad.
