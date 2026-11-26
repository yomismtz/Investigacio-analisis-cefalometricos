from __future__ import annotations

import yornis_reference_help_v0154 as _base

_EXTRA_TABLES = [
    {
        "id":"powell","title":"ANÁLISIS DE POWELL","subtitle":"Perfil blando · referencia estética orientativa","first":"Ángulo o plano",
        "source":"Powell N, Humphreys B. Proportions of the Aesthetic Face. Thieme-Stratton; 1984.",
        "note":"Proporciones estéticas históricas, no criterios diagnósticos ni estándares universales. La interpretación depende de edad, sexo, población, preferencias estéticas y técnica de fotografía/perfil.",
        "rows":[
            ("Ángulo nasofrontal","122°","±7°","Ángulo más agudo; glabela y/o dorso nasal relativamente más prominentes.","Transición armónica frente–nariz.","Ángulo más obtuso; región glabelar o puente nasal más planos."),
            ("Ángulo nasofacial","36°","±4°","Nariz menos proyectada o mentón relativamente más prominente.","Proyección nasal equilibrada respecto al perfil facial.","Nariz más proyectada o mentón relativamente retrusivo."),
            ("Ángulo nasomental","128°","±6°","Mayor prominencia nasal y/o mentoniana; perfil más tenso o angulado.","Relación armónica nariz–mentón.","Perfil más plano o menos definido; posible menor proyección mentoniana."),
            ("Ángulo mentocervical","87°","±7°","Ángulo cervicomentoniano más cerrado; mentón/cuello más agudos.","Contorno cuello–mentón estéticamente equilibrado.","Ángulo más abierto; posible retrusión mentoniana o plenitud submentoniana."),
            ("Interpretación global","Perfil armónico","cualitativa","Rasgos más agudos o prominentes en el perfil blando.","Proporciones faciales agradables dentro de la referencia clásica.","Rasgos más obtusos o suavizados del perfil."),
        ],
    },
    {
        "id":"via_aerea","title":"ANÁLISIS DE VÍA AÉREA","subtitle":"McNamara · referencia orientativa","first":"Ángulo o plano",
        "source":"McNamara JA Jr. A method of cephalometric evaluation. Am J Orthod. 1984;86(6):449-469. DOI 10.1016/S0002-9416(84)90352-X.",
        "rows":[
            ("Vía aérea superior (nasofaringe)","Adultos: 17.4 mm; aumenta con edad","♀ ±3.4 / ♂ ±4.3 mm","≤5 mm: indicador de posible compromiso, no diagnóstico; requiere valoración otorrinolaringológica.","Media adulta Ann Arbor; la deglución/posición del paladar puede limitar la medición.","Un valor alto aislado no confirma permeabilidad funcional."),
            ("Vía aérea inferior (orofaringe)","10–12 mm; cambio escaso con edad","Adultos: ♀ 11.3 ±3.3 / ♂ 13.5 ±4.3 mm","Un valor menor a la media no es notable por sí solo y no demuestra obstrucción.","Referencia descrita por McNamara; correlacionar con edad, postura y clínica.",">15 mm puede sugerir posición anterior de lengua; no equivale a mejor función."),
            ("Interpretación funcional","Indicador cefalométrico bidimensional","No es prueba funcional","La radiografía lateral no diagnostica apnea, obstrucción ni respiración oral.","Describe dimensiones en una proyección y momento determinados.","No permite inferir flujo aéreo normal ni ausencia de trastorno."),
            ("Relación con crecimiento","Interpretar con edad y desarrollo","No aplica","No inferir patrón vertical o maduración a partir de una sola medida faríngea.","Correlacionar con morfología, postura y exploración clínica.","No usar como predictor aislado de crecimiento o sueño."),
        ],
        "note":"McNamara advierte que la telerradiografía es una representación 2D de una estructura 3D; la deglución puede alterar el paladar blando. ≤5 mm en faringe superior solo indica posible compromiso; el diagnóstico requiere valoración otorrinolaringológica. En faringe inferior, un valor bajo no es notable por sí solo; >15 mm puede reflejar posición anterior de lengua.",
    },
    {
        "id":"craneo_cervical","title":"ANÁLISIS CRÁNEO-CERVICAL","subtitle":"Referencia postural de muestra; no es módulo de cálculo activo","first":"Ángulo o plano",
        "source":"Solow B, Tallgren A. Head posture and craniofacial morphology. Am J Phys Anthropol. 1976;44(3):417-435. DOI 10.1002/ajpa.1330440306; Rocabado M. protocolo de análisis cráneo-cervical (referencia secundaria; trazabilidad bibliográfica incompleta para algunas distancias).",
        "rows":[
            ("SN-OPT","92.18°","±6.00°","Ángulo menor que la media de esta muestra; puede describir mayor flexión relativa, no patología.","Media de muestra de 120 varones daneses de 22–30 años; registrar posición natural de cabeza.","Ángulo mayor que la media de esta muestra; puede describir mayor extensión relativa, no patología."),
            ("SN-CVT","97.72°","±5.65°","Ángulo menor que la media de esta muestra; describir la relación cabeza-columna.","Media de muestra de 120 varones daneses de 22–30 años; no generalizar a otras poblaciones.","Ángulo mayor que la media de esta muestra; describir la relación cabeza-columna."),
            ("OPT-CVT","Sin umbral universal validado","No aplica","Describir el ángulo entre tangentes; no inferir rectificación clínica por sí solo.","Comparar solo con una cohorte y protocolo de adquisición equivalentes.","Describir el ángulo entre tangentes; no inferir hiperlordosis clínica por sí solo."),
            ("Ángulo McGregor / odontoides","101°","±5°","Menor de 96°: desviación respecto a la referencia del protocolo Rocabado; no es diagnóstico.","96°–106°: intervalo orientativo del protocolo Rocabado.","Mayor de 106°: desviación respecto a la referencia del protocolo Rocabado; no es diagnóstico."),
            ("Espacio C0–C1","4–9 mm","Rango de protocolo","Menor de 4 mm: desviación del rango descrito; confirmar puntos y proyección.","4–9 mm: rango descrito en protocolo Rocabado.","Mayor de 9 mm: desviación del rango descrito; confirmar puntos y proyección."),
            ("Espacio C1–C2","Sin referencia verificada","No aplica","No clasificar con umbral en esta versión.","Registrar la medida si el protocolo está definido.","No clasificar con umbral en esta versión."),
            ("Altura triángulo hioideo H⊥C3-RGn","4 mm","±0.6 mm (protocolo)","Desviación del protocolo; confirmar puntos y escala.","Valor de protocolo Rocabado, no norma poblacional universal.","Desviación del protocolo; confirmar puntos y escala."),
            ("Triángulo hioideo","Descripción cualitativa","No aplica","Registrar posición y landmarks; no inferir función muscular aislada.","Describir el triángulo según el método y puntos definidos.","Registrar posición y landmarks; no inferir función muscular aislada."),
            ("Interpretación global","Descriptiva, no diagnóstica","No aplica","No diagnostica trastornos posturales, respiratorios ni cervicales.","Integrar con posición natural de cabeza y exploración clínica.","No diagnostica trastornos posturales, respiratorios ni cervicales."),
        ],
        "note":"SN-OPT 92.18°±6.00° y SN-CVT 97.72°±5.65° proceden de una muestra de 120 varones daneses de 22–30 años (Solow y Tallgren, 1976); son descriptivos de esa cohorte, no umbrales universales. Las referencias de Rocabado (McGregor–odontoides, C0–C1 y altura hioidea) son dependientes del protocolo y su trazabilidad bibliográfica completa debe confirmarse. Esta tabla es de referencia y no corresponde a un módulo de cálculo independiente en la versión actual; no permite diagnósticos posturales, respiratorios o cervicales.",
    },
    {
        "id":"lordosis_c1_c7","title":"LORDOSIS CERVICAL C1–C7","subtitle":"Referencia orientativa postural","first":"Ángulo o plano",
        "source":"Hardacker JW, Shuford RF, Capicotto PN, Pryor PW. Radiographic standing cervical segmental alignment in adult volunteers without neck symptoms. Spine. 1997;22(13):1472-1480. DOI 10.1097/00007632-199707010-00009. Muestra: 100 adultos; lordosis cervical total media −40.0° ±9.7° con su método de medición.",
        "rows":[
            ("Ángulo de lordosis C1–C7","Sin norma directa validada para esta construcción","No aplica","Describir la dirección y magnitud; no clasificar como rectificación patológica con un corte fijo.","Registrar método, puntos terminales y signo del ángulo; no aplicar 35–45° como rango universal.","Describir la dirección y magnitud; no clasificar como hiperlordosis patológica con un corte fijo."),
            ("Rango orientativo","No hay intervalo universal","No aplica","No utilizar el antiguo intervalo 35°–45° como umbral de normalidad.","La literatura reporta valores dependientes del método y de los niveles vertebrales incluidos.","No utilizar el antiguo intervalo 35°–45° como umbral de normalidad."),
            ("Implicación postural","Descripción radiográfica","cualitativa","No inferir síntomas, postura habitual ni adaptación respiratoria desde una imagen aislada.","La posición durante la adquisición puede modificar la curvatura observada.","No inferir síntomas, postura habitual ni adaptación respiratoria desde una imagen aislada."),
            ("Interpretación clínica","No diagnóstica","cualitativa","Requiere método reproducible y correlación clínica si existe indicación.","La referencia Hardacker es C0–C7 y no debe trasladarse automáticamente a una medición C1–C7.","Confirmar niveles, método, signo y contexto antes de comparar."),
        ],
        "note":"Se retira el antiguo rango 40°±5°/35°–45° por falta de una fuente que coincida con la construcción C1–C7 de esta tabla. Hardacker et al. informaron −40.0°±9.7° para lordosis cervical total en 100 adultos, pero su construcción y convención de signo deben comprobarse antes de trasladar esa cifra. No aplicar como corte universal.",
    },
]

existing = {t.get('id') for t in _base.TABLES}
for item in _EXTRA_TABLES:
    if item['id'] not in existing:
        _base.TABLES.append(item)

TABLES = _base.TABLES
DISCLAIMER = _base.DISCLAIMER
COLORS = _base.COLORS
validate_tables = _base.validate_tables
open_reference_help = _base.open_reference_help
attach_help_button = _base.attach_help_button
