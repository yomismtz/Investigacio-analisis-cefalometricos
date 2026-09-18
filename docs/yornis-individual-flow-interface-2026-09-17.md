# Yornis · Individual Flow + interfaz refinada

Actualización integrada del flujo **Caso individual**.

## Flujo funcional

1. Seleccionar uno o varios análisis cefalométricos.
2. Elegir dentro de cada análisis las medidas y/o ángulos deseados.
3. Construir automáticamente la lista mínima de landmarks necesarios.
4. Abrir el espacio de trazado.
5. Calcular y conservar únicamente los resultados seleccionados.

## Interfaz

- Tarjetas de análisis con jerarquía visual.
- Contadores tipo chip para resultados seleccionados.
- Botones de medidas/ángulos integrados en cada tarjeta.
- Ventana de selección de resultados con tarjetas individuales.
- Paso visual: análisis → medidas/ángulos → puntos.
- Integración con las 8 paletas existentes de Yornis.
- Mejor espaciado, tipografía y estados de acción.

## Metadatos de Windows

Editor / Publisher:

**Yomira Salgado Martínez**

Copyright:

**© 2026 Yomira Salgado Martínez**

La marca del producto continúa como **Yornis · Yom Dental Análisis**.

## Validación

La actualización conserva separadas las capas clínicas y visuales. No modifica las fórmulas cefalométricas, geometría ni referencias auditadas.

Se añadieron pruebas para verificar que:

- Caso individual abre el selector antes del trazado.
- La selección exacta de medidas se conserva.
- Los resultados no elegidos se filtran.
- El contexto de investigación se reinicia al entrar al flujo individual.
