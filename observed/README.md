# Historia observada de FireChronos dentro de GOLIAT

Importada del commit `d61ccf826ed3dbfd6461ad19324b0d65f9ffd4ac` de FireChronos el 14-11-2026. Se preservan el explorador original, los scripts, los tests, la DPA normalizada y los datos derivados. No se importa la identidad ni la configuración de acceso del sitio privado original. El código incorporado queda bajo la licencia Apache 2.0 de este repositorio.

Esta es una publicación **observada por plataforma**, con DPA 2023 oficial y filtro Type=0. No usa los factores ni las compuertas de la reconstrucción de GOLIAT. La máscara persistente adicional no está aplicada. La cobertura de observación es desconocida; cero detecciones no equivale a ausencia de actividad. El archivo anual termina en 2025. Aqua conserva versiones distintas sin afirmar equivalencia.

`pipeline/publish_observed.py` valida los hashes de los 162 CSV, vuelve a contar detecciones y celdas-día y los contrasta con los 29.322 agregados mensuales. Produce un contrato separado en `dist/data/publication/`. React consume esos números ya publicados, sin recalcularlos. Los CSV y metadatos descargados corresponden a la vista y plataforma seleccionadas.

```sh
# Desde la raíz de GOLIAT; no requiere originales ni credenciales
python3 pipeline/publish_observed.py
npm test
npm run build
```

Para reproducir desde los originales, crear un entorno con `observed/requirements-geo.txt`, ejecutar desde esta carpeta los scripts `download_sources.py`, `prepare_boundaries.py`, `prepare_history.py` e `inventory.py`, y volver a publicar. `tests/verify_history.py` exige originales y geometría completa; no omite archivos faltantes. Los originales, las claves y el entorno no se versionan.

El explorador completo se sirve en `/observed/index.html`; la vista integrada de GOLIAT usa `/observed/data/publication/`. Fuentes: NASA FIRMS y SUBDERE / IDE Chile, [DPA 2023](https://geoportal.cl/geoportal/catalog/36391/division-politica-administrativa-2023).
