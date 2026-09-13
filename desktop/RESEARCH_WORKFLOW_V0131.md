# YomCeph Desktop v0.13.1 Classic — Flujo de investigación

Esta versión mantiene la interfaz Classic de YomCeph 0.12.x y añade un flujo secuencial de investigación.

## Secuencia

1. Idioma en el instalador: Español o English.
2. Al abrir: Caso individual o Investigación.
3. Investigación: datos del protocolo mediante campos y listas de verificación.
4. Selección de uno o varios análisis cefalométricos.
5. Para cada análisis, selección de las mediciones/resultados que realmente formarán parte del estudio.
6. YomCeph calcula la lista mínima de landmarks requerida por esas mediciones.
7. Incorporación de radiografías: carga masiva, por lotes o registro manual. Límite de 1000 casos por estudio.
8. Cada registro conserva número/ID, edad, sexo, radiografía, estado y observaciones.
9. Al abrir un registro desde la base, se restauran sus metadatos, imagen, puntos y resultados guardados.
10. El caso se marca Completo únicamente cuando están registrados todos los resultados seleccionados para el protocolo.
11. Si no puede analizarse, puede marcarse Excluido con motivo documentado (calidad radiográfica, landmarks no identificables, criterios del protocolo u otro). El excluido deja de formar parte de la muestra válida pero permanece en la auditoría.
12. Exportación separada de muestra válida y auditoría completa.

## Identidad visual

La interfaz se mantiene exclusivamente dentro de la familia YomCeph: morado, violeta, púrpura, ciruela, lila y lavanda, con verde menta y verde turquesa como acentos. No se usarán azul genérico, rojo dominante ni paneles grises como identidad principal.

## Estados de la base de investigación

- ● verde menta / turquesa: **Completo** e incluido en la muestra válida.
- ● lila / lavanda: **Pendiente** o todavía sin iniciar.
- ● violeta: **En análisis / Incompleto**.
- ● ciruela / púrpura oscuro: **Excluido** o requiere revisión. No se utilizará rojo como color dominante.

El protocolo puede bloquearse cuando comienzan a registrarse casos válidos para evitar cambiar accidentalmente las variables del estudio a mitad de la recolección.

Los colores canónicos y sus códigos se centralizan en `yomceph_theme.py` para que botones, tablas, estados, puntos y trazados usen la misma identidad visual.
