# Yornis v0.15.7 · Bird Assistant

## Objetivo

Convertir la selección de paleta en una función de acompañamiento: cada ave de la paleta se convierte en el asistente virtual local de Yornis.

## Cambios principales

- Ocho asistentes: Agaporni, Tucán, Pavorreal, Ninfa, Faisán, Quetzal, Guacamaya Roja y Guacamaya Azul.
- El asistente explica tareas frecuentes paso a paso.
- Buscador interno sobre guías de uso, 17 tablas de referencia y las mediciones del motor.
- Acceso directo a tablas desde los resultados del buscador.
- Atajo Ctrl+K para abrir el asistente y F1 para referencias.
- Selector de paleta mediante tarjetas con muestras de color, en lugar de depender sólo de un desplegable.
- Botones, pestañas, tablas, selecciones y estados adoptan de manera más visible los colores de la paleta elegida.
- Avatares de aves generados a alta resolución mediante supersampling y reescalado LANCZOS, sin depender de imágenes externas.
- Branding reconstruido a 512 px en el pipeline antes de empaquetar el ejecutable.

## Seguridad clínica

El asistente no diagnostica. Explica funciones, localiza información y muestra referencias ya auditadas. Se mantiene la geometría de v0.15.5/v0.15.6, no se interpolan edades no publicadas y no se restaura 35–45° como corte universal de C1–C7.

## Búsqueda

El índice interno combina:

- guías de uso de Yornis;
- las 17 tablas de referencia;
- las 102 mediciones automáticas del motor.

La búsqueda es local y no envía la consulta a servicios externos.

## Distribución

La versión se publica como v0.15.7 con instalador Windows x64, versión portable y SHA-256. El release sólo se crea cuando el marcador `desktop/YORNIS_RELEASE_V0157.txt` llega a `main` y el pipeline completo vuelve a pasar.
