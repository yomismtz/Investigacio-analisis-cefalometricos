# Yornis v0.15.4 · Audit Hardening

Esta revisión es una capa aditiva sobre v0.15.3. No cambia silenciosamente la definición geométrica de una medición clínica ya auditada; corrige persistencia, dependencias de landmarks, privacidad, exportación, respaldo, DPI y validación de software.

## Correcciones críticas

- Las variables Burstone/Legan dependientes del horizontal construido HP solicitan explícitamente S, N, Po y Or además de sus puntos primarios.
- CVM C2–C4 y alineación C2–C4 pasan a historial append-only por outcome. `latest_results` selecciona el último registro de cada análisis+medición sin destruir revisiones anteriores.
- Los respaldos usan `sqlite3.backup()`, ejecutan `PRAGMA integrity_check`, contienen un solo estudio y respetan `storage_root`. El respaldo AES usa el mismo snapshot consistente.
- Se añade verificación/extracción segura de respaldos antes de cualquier restauración activa.
- Cambiar `storage_root` migra los archivos administrados y actualiza las rutas de los casos; autosave usa el mismo root del estudio.
- Las radiografías administradas se renombran `YC_####` y ya no conservan el nombre fuente en `original_filename` ni en nuevos eventos de auditoría. La migración limpia nombres/rutas heredados del log.
- El JSON de investigación es pseudonimizado por defecto y no exporta rutas locales, nombre fuente ni hash de archivo.

## Exportación y reportes

- La sintaxis SPSS declara `/VARIABLES`, tipos de datos, `VARIABLE LEVEL` y etiquetas para CVM y alineación C2–C4.
- El PDF visual acepta radiografías PDF renderizando la primera página; los textos de landmarks usan una fuente TrueType cuando está disponible.
- El trazado visual del PDF deja de conectar secuencialmente todos los puntos de una medición y dibuja sólo segmentos geométricamente seguros.

## Protocolo y referencias

- El protocolo incorpora un campo explícito de población/cohorte/norma. Es texto metodológico; Yornis no inventa una tabla normativa a partir de la etiqueta.
- Sassouni se identifica en Investigación como ayuda geométrica que requiere confirmación visual.
- La longitud palatina COGS PNS–ANS conserva como referencia histórica: hombres 57.7 ± 2.5 mm y mujeres 52.6 ± 3.5 mm, etiquetada como muestra histórica, no como límite diagnóstico universal.
- El QC de puntos casi superpuestos deja de depender de un umbral fijo en píxeles. Sólo se aplica con calibración y se identifica como heurística técnica.
- La acción “Calcular y guardar” usa de verdad los QC bloqueantes: un caso con landmarks o calibración faltantes sólo se guarda como borrador/incompleto tras confirmación explícita.

## Windows / DPI

- El tamaño de ventana usa el área de trabajo del monitor actual en Windows, no sólo el tamaño total de pantalla.
- Los `Toplevel` dejan de competir por `tk scaling`, que es global al intérprete Tcl/Tk.
- Se mantiene el manifiesto `PerMonitorV2` de v0.15.3.

## Validación v0.15.4

La CI compila todos los módulos Python del escritorio, ejecuta la suite `unittest`, prueba backups y restauración, sintaxis SPSS, historial CVM, privacidad JSON y una barrera de regresión que llama a todas las mediciones automáticas registradas con geometría sintética no degenerada. Después construye el EXE, realiza cold-start, crea instalador y portable, y publica SHA-256.

La firma Authenticode es opcional y sólo se ejecuta cuando el repositorio dispone de un certificado de firma de código y su contraseña como secretos. No se genera una firma autofirmada para aparentar confianza.

## Alcance clínico

Yornis sigue siendo una herramienta educativa y de investigación. Pasar las pruebas de software no convierte las referencias históricas en normalidad universal ni sustituye una validación clínica externa contra trazados de referencia, población y protocolo definidos.
