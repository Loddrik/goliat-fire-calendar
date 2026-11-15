# G0 autenticado: acceso y lectura técnica comprobados en una pareja

Con el token Earthdata suministrado por el usuario se adquirió únicamente la pareja técnica fijada por el preflight: Aqua del 3 de enero de 2019, 18:40–18:45 UTC, y S-NPP, 18:36–18:42 UTC, con sus dos archivos de geolocalización. No se eligió por resultados de fuego.

**Resultado:** acceso y esquemas leídos; InputPointer exacto en ambas plataformas; centros geolocalizados dentro de la AOI y extensiones de centros solapadas. **Esto no acredita todavía elegibilidad científica completa ni G1:** faltan interpretación específica de bits QA y diseño espacial/denominador. No se calculó una matriz de concordancia ni cantidades comparativas de fuego.

## Adquisición acotada

| Producto | Bytes descargados | Formato |
| --- | ---: | --- |
| MYD14 | 410.942 | HDF4 |
| MYD03 | 34.098.478 | HDF4 |
| VNP14IMG | 3.184.218 | HDF5/NetCDF4 |
| VNP03IMG | 156.055.168 | HDF5/NetCDF4 |
| **Total** | **193.748.806** | **184,77 MiB; límite 400 MiB** |

Los archivos crudos permanecen bajo `.runtime/observation-pilot/raw/`, ignorados por Git. Cada uno tiene SHA-256 y bytes registrados. El snapshot del descargador conserva el código exacto de adquisición; la inspección registra por separado el hash del lector actual. Los probes anónimos anteriores no se alteraron: sus HTTP302 documentan el estado sin autenticación; esta evidencia documenta la adquisición autenticada posterior.

El bearer se leyó del archivo secreto ignorado. Solo se adjuntó a hosts NASA incluidos explícitamente en una lista permitida. Los redirects se manejaron manualmente; al pasar a los dos CDN CloudFront se omitió Authorization. No se guardaron queries firmadas, bearer, cuerpos de error o formularios de autorización. No se aceptaron acuerdos de cuenta ni se inició un flujo interactivo nuevo.

## Lectura y asociación comprobadas

| Comprobación | Aqua | S-NPP |
| --- | --- | --- |
| Geolocalización nombrada en InputPointer | Coincide exactamente con MYD03 descargado | Coincide exactamente con VNP03IMG descargado |
| Máscara, QA y geolocalización | 2.030 × 1.354 | 6.464 × 6.400 |
| Centros dentro de la envolvente AOI fijada | 2.294 | 17.113 |
| Geometría disponible | Ángulos, coordenadas, gflags | Ángulos, coordenadas, quality_flag |
| Tiempo de escaneo disponible | 203 valores EV start/center time | 202 valores scan start/end y EV mid time |

Los conteos de centros no son conteos de fuego ni pares comparables. Su diferente densidad no se interpreta como un factor de armonización. La intersección de extensiones de centros dentro de la envolvente es aproximadamente `[-72.781876, -37.225422, -72.218224, -36.774094]`. Es una comprobación geométrica aproximada; no demuestra footprints idénticos, cobertura válida completa o elegibilidad bilateral.

Se leyeron completas las matrices de máscara y QA por bloques; se conservan hashes de sus valores y conteos de clases del **granule entero**, como pruebas del lector. Esos conteos no son un resultado de actividad en la AOI ni una comparación entre instrumentos.

Las leyendas reales confirman que la codificación debe ser específica de producto: MODIS identifica 0 como datos de entrada faltantes y 1/2 como clases obsoletas, mientras VIIRS usa 0 para no procesado, 1 para bow-tie y 2 para glint. No se trasladaron los significados de un sensor al otro. El QA es un campo de bits; su interpretación completa queda pendiente antes de usarlo como elegibilidad.

La metadata automática de MYD14 contiene `Suspect`, con explicación `not being investigated`. Se conserva el dato; no se interpreta por sí solo como calidad favorable ni como invalidez automática. Los tiempos nativos de escaneo se registraron con sus unidades y atributos: no se convierte un campo que dice solamente “seconds” a UTC sin comprobar su referencia temporal.

## Entorno aislado y pruebas

La lectura usa `.runtime/obs-env`, Python 3.10.0, separado del entorno principal. HDF5 se leyó con h5py; HDF4 con pyhdf, compilado contra bibliotecas bajo `.runtime/obs-native`. No se modificaron `pyproject.toml`, `uv.lock` ni bibliotecas globales. Las versiones y hashes de paquetes nativos se guardan en la evidencia.

```sh
.venv/bin/python pipeline/observation_authenticated.py \
  --deadline-utc 2026-11-15T01:17:49Z

DYLD_LIBRARY_PATH="$PWD/.runtime/obs-native/lib" \
  .runtime/obs-env/bin/python pipeline/observation_authenticated.py --inspect-only

.venv/bin/python -m unittest discover -s tests \
  -p test_observation_authenticated.py -v
```

El primer comando usa por defecto el archivo secreto local y no debe recibir el valor del token como argumento. Para repetir una descarga hay que indicar una hora límite futura; la inspección de archivos existentes no hace red.

Cuatro tests de transporte pasan: Authorization solo en hosts NASA exactos; ausencia de bearer y query firmada en redirects/evidencia; límite de bytes incluso sin Content-Length; rechazo de HTML cacheado como archivo científico. Los tests no necesitan credenciales ni paquetes HDF.

## Evidencia y decisión

[Adquisición](evidence/observation-authenticated/acquisition.json), [lectura técnica](evidence/observation-authenticated/inspection.json), [entorno](evidence/observation-authenticated/environment.json) y [manifiesto](evidence/observation-authenticated/manifest.json).

La adquisición y la lectura técnica dejan de ser una hipótesis. La oportunidad de observación y la comparabilidad analítica siguen siendo trabajo de G1. Una sola pareja no permite estimar mejora del modelo, cobertura del período ni fracción causal de desacuerdo. Se mantiene separado el éxito técnico de acceso/esquema del éxito científico del piloto.
