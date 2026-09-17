# Yornis v0.15.9.2 · Scroll + Bird Sounds

## Objetivo

Esta revisión corrige la navegación vertical del launcher y añade una respuesta sonora diferenciada al seleccionar cada una de las ocho paletas inspiradas en aves.

## Scroll del launcher

El launcher usa un área desplazable con barra vertical visible. El contenido puede recorrerse con la barra, la rueda del mouse o trackpad y las teclas PageUp, PageDown, Home y End. La validación de interfaz reduce la ventana y comprueba que existe contenido fuera del viewport y que el desplazamiento modifica efectivamente la posición visible.

## Firmas sonoras por ave

Cada una de las ocho paletas tiene una firma sonora breve y distinta: Agaporni, Tucán, Pavorreal, Ninfa, Faisán, Quetzal, Guacamaya Roja y Guacamaya Azul. En Windows el sonido respeta el estado activado/desactivado y el volumen configurado. Las firmas se sintetizan localmente y no dependen de archivos de audio externos.

La demostración del sitio web usa Web Audio y sólo reproduce sonido después de una interacción del usuario; no existe autoplay.

## Alcance científico

La versión no modifica la geometría de las 102 mediciones ni las 17 tablas de referencia. Se mantienen las salvaguardas previas: no se restaura un corte universal 35–45° para C1–C7, no se interpolan edades no publicadas y las referencias dependientes de método, edad, sexo o población conservan su contexto.

## Validación

La rama de v0.15.9.2 superó 43 pruebas de regresión, además de auditoría específica de firmas sonoras, prueba GUI/HiDPI del scroll, compilación con PyInstaller, arranque en frío en Windows e instalación.

## Distribución

La página web usa el enlace `releases/latest` para dirigir a la publicación pública estable más reciente y evitar enlaces rotos cuando cambia el nombre del instalador. Antes de instalar, conviene comprobar la versión publicada y el archivo `SHA256SUMS.txt` correspondiente.
