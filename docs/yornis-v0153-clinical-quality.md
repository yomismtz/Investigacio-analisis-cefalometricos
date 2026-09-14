# Yornis v0.15.3 · Clinical Quality

Esta revisión corrige hallazgos de la auditoría del ejecutable Windows v0.15.2 y mantiene separados dos conceptos: **geometría calculada** y **referencia clínica/histórica**. Una media histórica no se presenta como normalidad universal.

## Cambios clínico-matemáticos

### Legan–Burstone

Se corrigen tres variables verticales que antes utilizaban distancia euclidiana directa:

- `G'-Sn / Sn-Me'`: ahora usa las componentes perpendiculares al plano horizontal HP.
- `Sn-Stms / Stmi-Me'`: ahora usa las componentes perpendiculares a HP.
- `Brecha interlabial Stms-Stmi`: ahora se mide perpendicularmente a HP.

### Holdaway

La antigua variable `Espesor mentón Pg-Pg'` se sustituye por **`Espesor de mentón blando · Holdaway (nivel SPg)`**. La construcción obtiene la separación horizontal entre el plano facial óseo y el plano facial de tejidos blandos al nivel de suprapogonion, en lugar de usar la distancia euclidiana Pg–Pg'.

La referencia histórica se conserva como referencia de muestra y no como corte diagnóstico universal.

### Burstone COGS

Se añaden tres variables que faltaban del conjunto COGS implementado:

- `U6-NF altura`;
- `L6-MP altura`;
- `B-Pg // MP`.

Se conservan las referencias históricas por sexo cuando están disponibles. Si el sexo no se especifica, no se fuerza una clasificación automática.

### Sassouni

El módulo deja de limitarse a una convergencia simplificada de cuatro planos. Además del centro arquitectónico y la igualdad angular, expone como resultados de Investigación:

- radio del arco anterior O-ANS;
- residuos de FE, N, U1 y Pg respecto al arco anterior;
- radio del arco posterior O-Sp;
- residuo de Go respecto al arco posterior;
- índice facial Ra/Rp;
- relación dentaria `M' − (I' + 10°)`;
- relación dentaria `m' − (i' + 5°)`;
- relación `R − i`.

Los residuos y errores se presentan como resultados geométricos. No se inventa una tolerancia milimétrica universal para declarar normalidad Sassouni.

## Investigación

- El motor ahora expone `norm_text`/`reference` a partir del campo real `ref`, evitando que las referencias de la mayoría de las mediciones desaparezcan en modo Investigación.
- CVM C2–C4 y la alineación C2–C4 aparecen como outcomes especiales seleccionables del protocolo.
- Los resultados manuales CVM/alineación se guardan con la versión real del protocolo del caso y se conservan aunque posteriormente se vuelva a guardar el trazado numérico.
- `latest_results` obtiene la versión más reciente **por análisis + medición**, evitando perder outcomes especiales por diferencias de versión interna.
- Las referencias se contextualizan cuando corresponde por edad, sexo, población, tamaño facial, postura o técnica radiográfica.

## Calidad visual Windows

El ejecutable v0.15.3 incorpora un manifiesto Windows con `PerMonitorV2` además del escalado dinámico Tk/Segoe UI ya existente. El objetivo es impedir el escalado bitmap de compatibilidad de Windows que puede hacer que el texto se vea pixelado en pantallas con 125%, 150%, 200% o monitores con DPI distintos.

## Criterio de uso

Yornis sigue siendo una herramienta educativa y de investigación. Los intervalos históricos se muestran como **referencias**, no como fronteras biológicas universales ni diagnósticos. Las medidas lineales requieren una calibración radiográfica válida y los resultados dependientes de población deben interpretarse con la norma definida por el protocolo del estudio.
