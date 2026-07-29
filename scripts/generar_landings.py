#!/usr/bin/env python3
"""generar_landings.py — Genera landings SEO con contenido rico para indexación."""
import json
import statistics
from pathlib import Path
from datetime import datetime
import html as html_module

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

# ── ACCIONES TERAPÉUTICAS ──────────────────────────────────────────────
ACCIONES = {
    "omeprazol": "Inhibidor de la bomba de protones",
    "metformina": "Antidiabético (biguanida)",
    "enalapril": "Antihipertensivo (inhibidor de la enzima convertidora de angiotensina)",
    "losartan": "Antihipertensivo (bloqueador del receptor de angiotensina II)",
    "levotiroxina": "Hormona tiroidea sintética",
    "clonazepam": "Benzodiazepina ansiolítica y anticonvulsivante",
    "alprazolam": "Benzodiazepina ansiolítica",
    "lorazepam": "Benzodiazepina ansiolítica",
    "sertralina": "Antidepresivo inhibidor selectivo de la recaptación de serotonina",
    "atorvastatina": "Hipolipemiante (inhibidor de la HMG-CoA reductasa)",
    "zolpidem": "Hipnótico no benzodiazepínico",
    "paracetamol": "Analgésico y antipirético",
    "ibuprofeno": "Antiinflamatorio no esteroide",
    "amoxicilina": "Antibiótico betalactámico",
    "acido-acetilsalicilico": "Antiplaquetario y antiinflamatorio no esteroide",
    "salbutamol": "Broncodilatador agonista beta-2 adrenérgico",
    "losartan-hidroclorotiazida": "Antihipertensivo combinado (bloqueador AT1 + diurético)",
    "prednisona": "Corticoesteroide antiinflamatorio",
    "escitalopram": "Antidepresivo inhibidor selectivo de la recaptación de serotonina",
    "diazepam": "Benzodiazepina ansiolítica y anticonvulsivante",
    "carbamazepina": "Anticonvulsivante y estabilizador del ánimo",
    "fenobarbital": "Anticonvulsivante (barbitúrico)",
    "betametasona": "Corticoesteroide",
    "naproxeno": "Antiinflamatorio no esteroide",
    "diclofenac": "Antiinflamatorio no esteroide",
    "amlodipina": "Antihipertensivo (bloqueante de los canales de calcio)",
    "carvedilol": "Antihipertensivo y betabloqueante",
    "clortalidona": "Diurético tiazídico",
    "furosemida": "Diurético de asa",
    "hidroclorotiazida": "Diurético tiazídico",
    "espironolactona": "Diurético ahorrador de potasio",
    "glibenclamida": "Antidiabético (sulfonilurea)",
    "insulina-glargina": "Insulina basal de acción prolongada",
    "insulina": "Hormona hipoglucemiante",
    "levodopa-carbidopa": "Antiparkinsoniano",
    "pregabalina": "Anticonvulsivante y analgésico neuropático",
    "gabapentina": "Anticonvulsivante y analgésico neuropático",
    "clozapina": "Antipsicótico atípico",
    "litio": "Estabilizador del ánimo",
    "valproato": "Anticonvulsivante y estabilizador del ánimo",
    "risperidona": "Antipsicótico atípico",
    "quetiapina": "Antipsicótico atípico",
    "olanzapina": "Antipsicótico atípico",
    "haloperidol": "Antipsicótico típico",
    "fluoxetina": "Antidepresivo inhibidor selectivo de la recaptación de serotonina",
    "venlafaxina": "Antidepresivo inhibidor de la recaptación de serotonina y noradrenalina",
    "levomepromazina": "Antipsicótico fenotiazínico",
    "metoclopramida": "Antiemético y procinético",
    "ipratropio": "Broncodilatador anticolinérgico",
    "sildenafil": "Inhibidor de la fosfodiesterasa tipo 5",
    "cetirizina": "Antihistamínico de segunda generación",
    "loratadina": "Antihistamínico de segunda generación",
    "pantoprazol": "Inhibidor de la bomba de protones",
    "aciclovir": "Antiviral (análogo de nucleósido)",
    "azitromicina": "Antibiótico macrólido",
    "bupropion": "Antidepresivo y coadyuvante para dejar de fumar",
    "etinilestradiol-levonorgestrel": "Anticonceptivo hormonal combinado (estrógeno + progestágeno)",
    "drospirenona-etinilestradiol": "Anticonceptivo hormonal combinado (estrógeno + progestágeno)",
    "desogestrel": "Anticonceptivo hormonal (progestágeno solo)",
    "clopidogrel": "Antiagregante plaquetario",
    "warfarina": "Anticoagulante oral (antagonista de la vitamina K)",
    "rivaroxaban": "Anticoagulante oral de acción directa (inhibidor del factor Xa)",
    "bisoprolol": "Antihipertensivo betabloqueante cardioselectivo",
    "metoprolol": "Antihipertensivo betabloqueante cardioselectivo",
    "ramipril": "Antihipertensivo (inhibidor de la enzima convertidora de angiotensina)",
    "valsartan": "Antihipertensivo (bloqueador del receptor de angiotensina II)",
    "telmisartan": "Antihipertensivo (bloqueador del receptor de angiotensina II)",
    "rosuvastatina": "Hipolipemiante (inhibidor de la HMG-CoA reductasa)",
    "digoxina": "Cardiotónico (glucósido digitálico)",
    "amoxicilina-clavulanico": "Antibiótico betalactámico con inhibidor de betalactamasa",
    "cefalexina": "Antibiótico cefalosporina de primera generación",
    "ciprofloxacina": "Antibiótico quinolona",
    "metronidazol": "Antibiótico y antiparasitario (nitroimidazol)",
    "nitrofurantoina": "Antibiótico urinario",
    "butilescopolamina": "Antiespasmódico anticolinérgico",
    "domperidona": "Antiemético y procinético",
    "famotidina": "Antagonista de los receptores H2 de histamina",
    "loperamida": "Antidiarreico (opioide de acción periférica)",
    "simeticona": "Antiflatulento (agente antiespumante)",
    "tramadol": "Analgésico opioide de acción central",
    "meloxicam": "Antiinflamatorio no esteroide (inhibidor preferencial de la COX-2)",
    "ketorolac": "Antiinflamatorio no esteroide de uso analgésico",
    "celecoxib": "Antiinflamatorio no esteroide inhibidor selectivo de la COX-2",
    "budesonide": "Corticoesteroide inhalatorio/nasal",
    "montelukast": "Antiasmático (antagonista de los receptores de leucotrienos)",
    "fluticasona": "Corticoesteroide inhalatorio/nasal",
    "clotrimazol": "Antifúngico tópico (imidazol)",
    "fluconazol": "Antifúngico sistémico (triazol)",
    "mupirocina": "Antibiótico tópico",
    "acido-folico": "Vitamina (suplemento de ácido fólico/vitamina B9)",
    "complejo-b": "Suplemento vitamínico (complejo de vitaminas del grupo B)",
    "vitamina-d": "Suplemento vitamínico (colecalciferol)",
    "sulfato-ferroso": "Suplemento de hierro (antianémico)",
    "dorzolamida-timolol": "Antiglaucomatoso combinado (inhibidor de la anhidrasa carbónica + betabloqueante)",
    "latanoprost": "Antiglaucomatoso (análogo de prostaglandina)",
    "desloratadina": "Antihistamínico de segunda generación",
    "levocetirizina": "Antihistamínico de segunda generación",
    "melatonina": "Regulador del ciclo sueño-vigilia",
    "acetilcisteina": "Mucolítico",
    "ambroxol": "Mucolítico y expectorante",
}

# ── DESCRIPCIONES ÚNICAS POR DROGA ────────────────────────────────────
DESCRIPCIONES = {
    "omeprazol": "El omeprazol es uno de los medicamentos más recetados en Argentina para el tratamiento de la acidez estomacal, úlceras gástricas y reflujo gastroesofágico. Actúa reduciendo la producción de ácido en el estómago bloqueando la bomba de protones.",
    "metformina": "La metformina es el medicamento de primera línea para el tratamiento de la diabetes tipo 2 en Argentina. Reduce la glucosa en sangre mejorando la sensibilidad a la insulina sin provocar hipoglucemia.",
    "enalapril": "El enalapril es un antihipertensivo ampliamente utilizado en Argentina para controlar la presión arterial alta y tratar la insuficiencia cardíaca. Pertenece a la familia de los IECA.",
    "losartan": "El losartán es un antihipertensivo de la familia de los ARA II, indicado para la hipertensión arterial y la protección renal en pacientes diabéticos. Es una alternativa al enalapril con menos efectos adversos.",
    "levotiroxina": "La levotiroxina es la hormona tiroidea sintética utilizada para tratar el hipotiroidismo. Es uno de los medicamentos de uso crónico más frecuentes en Argentina, especialmente en mujeres.",
    "clonazepam": "El clonazepam es una benzodiazepina utilizada para tratar la ansiedad, los ataques de pánico y algunas formas de epilepsia. Requiere prescripción médica y su uso prolongado debe ser supervisado.",
    "alprazolam": "El alprazolam es una benzodiazepina de acción rápida indicada para el trastorno de ansiedad generalizada y los ataques de pánico. Es uno de los ansiolíticos más recetados en Argentina.",
    "lorazepam": "El lorazepam es una benzodiazepina utilizada para el tratamiento de la ansiedad aguda e insomnio. Se usa también en el ámbito hospitalario para sedación.",
    "sertralina": "La sertralina es uno de los antidepresivos más recetados en Argentina. Pertenece a la familia de los ISRS y es eficaz para la depresión, el trastorno obsesivo-compulsivo y la ansiedad social.",
    "atorvastatina": "La atorvastatina es el hipolipemiante más utilizado en Argentina para reducir el colesterol LDL y prevenir enfermedades cardiovasculares. Se toma una vez al día, generalmente de noche.",
    "zolpidem": "El zolpidem es un hipnótico no benzodiazepínico indicado para el insomnio de corto plazo. Actúa rápidamente y tiene menor riesgo de dependencia que las benzodiazepinas.",
    "paracetamol": "El paracetamol es el analgésico y antipirético más utilizado en Argentina. Alivia el dolor leve a moderado y baja la fiebre. Es seguro en dosis correctas para adultos y niños.",
    "ibuprofeno": "El ibuprofeno es un antiinflamatorio no esteroide (AINE) utilizado para el dolor, la fiebre y la inflamación. Es uno de los medicamentos de venta libre más consumidos en Argentina.",
    "amoxicilina": "La amoxicilina es el antibiótico de primera línea para infecciones respiratorias, urinarias y dentales en Argentina. Pertenece a la familia de las penicilinas y requiere prescripción médica.",
    "acido-acetilsalicilico": "El ácido acetilsalicílico (aspirina) se usa en Argentina tanto como analgésico y antipirético como para la prevención cardiovascular en dosis bajas. Es antiplaquetario a dosis de 100 mg.",
    "salbutamol": "El salbutamol es el broncodilatador de rescate más utilizado en Argentina para el asma y la EPOC. Actúa rápidamente abriendo las vías respiratorias durante una crisis.",
    "losartan-hidroclorotiazida": "La combinación de losartán e hidroclorotiazida ofrece un control más eficaz de la hipertensión arterial al combinar dos mecanismos de acción distintos en un solo comprimido.",
    "prednisona": "La prednisona es un corticoesteroide potente utilizado para tratar enfermedades inflamatorias, autoinmunes y alérgicas graves. Su uso prolongado requiere supervisión médica.",
    "escitalopram": "El escitalopram es un antidepresivo ISRS de última generación con menor cantidad de efectos adversos. Es uno de los antidepresivos más recetados en Argentina para depresión y ansiedad.",
    "diazepam": "El diazepam es una benzodiazepina clásica utilizada para la ansiedad, el insomnio, los espasmos musculares y la epilepsia. Tiene larga duración de acción.",
    "carbamazepina": "La carbamazepina es un anticonvulsivante utilizado para la epilepsia y el trastorno bipolar. También se indica para la neuralgia del trigémino.",
    "fenobarbital": "El fenobarbital es uno de los anticonvulsivantes más antiguos y económicos disponibles en Argentina. Sigue siendo de primera línea en ciertos tipos de epilepsia.",
    "betametasona": "La betametasona es un corticoesteroide de alta potencia disponible en cremas, inyectables y comprimidos. Se usa para dermatitis, artritis y cuadros inflamatorios graves.",
    "naproxeno": "El naproxeno es un antiinflamatorio no esteroide de acción prolongada (cada 12 horas) indicado para el dolor, la artritis y la dismenorrea.",
    "diclofenac": "El diclofenac es un AINE muy utilizado en Argentina para el dolor musculoesquelético, artritis y cólicos. Disponible en comprimidos, inyectable y gel tópico.",
    "amlodipina": "La amlodipina es un bloqueante de los canales de calcio utilizado para la hipertensión arterial y la angina de pecho. Se toma una vez al día y tiene efecto prolongado.",
    "carvedilol": "El carvedilol es un betabloqueante no selectivo utilizado para la hipertensión arterial y la insuficiencia cardíaca. Combina efecto betabloqueante y vasodilatador.",
    "clortalidona": "La clortalidona es un diurético tiazídico de acción prolongada utilizado para la hipertensión arterial. Tiene mayor duración que la hidroclorotiazida.",
    "furosemida": "La furosemida es un diurético de asa potente utilizado para el edema y la insuficiencia cardíaca. Actúa rápidamente y puede administrarse por vía oral o intravenosa.",
    "hidroclorotiazida": "La hidroclorotiazida es el diurético tiazídico más utilizado en Argentina, frecuentemente combinado con otros antihipertensivos para mejorar el control de la presión arterial.",
    "espironolactona": "La espironolactona es un diurético ahorrador de potasio utilizado para la insuficiencia cardíaca, la hipertensión y el hiperaldosteronismo.",
    "glibenclamida": "La glibenclamida es un antidiabético oral de la familia de las sulfonilureas. Estimula la secreción de insulina y se usa para la diabetes tipo 2 cuando la metformina no es suficiente.",
    "insulina-glargina": "La insulina glargina es una insulina de acción prolongada (basal) que se administra una vez al día. Proporciona un nivel de insulina estable durante 24 horas.",
    "insulina": "La insulina es la hormona esencial para el tratamiento de la diabetes tipo 1 y algunos casos de diabetes tipo 2. Existen múltiples tipos según su duración de acción.",
    "levodopa-carbidopa": "La combinación levodopa/carbidopa es el tratamiento estándar para la enfermedad de Parkinson en Argentina. La carbidopa potencia el efecto de la levodopa y reduce sus efectos adversos.",
    "pregabalina": "La pregabalina es un anticonvulsivante también indicado para el dolor neuropático y el trastorno de ansiedad generalizada. Es eficaz para la fibromialgia y la neuralgia postherpética.",
    "gabapentina": "La gabapentina es un anticonvulsivante utilizado para la epilepsia y el dolor neuropático. Precede a la pregabalina y sigue siendo ampliamente utilizada por su bajo costo.",
    "clozapina": "La clozapina es un antipsicótico atípico reservado para la esquizofrenia resistente a otros tratamientos. Requiere monitoreo regular del recuento sanguíneo.",
    "litio": "El litio es el estabilizador del ánimo de referencia para el trastorno bipolar. Su rango terapéutico es estrecho y requiere controles periódicos de litemia.",
    "valproato": "El valproato de sodio es un anticonvulsivante y estabilizador del ánimo utilizado para la epilepsia y el trastorno bipolar. También se usa para la prevención de migraña.",
    "risperidona": "La risperidona es un antipsicótico atípico utilizado para la esquizofrenia, el trastorno bipolar y los trastornos del espectro autista.",
    "quetiapina": "La quetiapina es un antipsicótico atípico utilizado para la esquizofrenia, el trastorno bipolar y como coadyuvante en la depresión mayor.",
    "olanzapina": "La olanzapina es un antipsicótico atípico eficaz para la esquizofrenia y el trastorno bipolar. Su principal efecto adverso es el aumento de peso.",
    "haloperidol": "El haloperidol es un antipsicótico típico clásico utilizado para la esquizofrenia y los estados de agitación. Disponible en comprimidos, gotas e inyectable.",
    "fluoxetina": "La fluoxetina fue el primer ISRS disponible en el mercado. Sigue siendo ampliamente utilizada para la depresión, el TOC y la bulimia nerviosa.",
    "venlafaxina": "La venlafaxina es un antidepresivo IRSN eficaz para la depresión mayor, el trastorno de ansiedad generalizada y el dolor neuropático.",
    "levomepromazina": "La levomepromazina es un antipsicótico fenotiazínico utilizado para la esquizofrenia y como sedante. También se emplea en cuidados paliativos.",
    "metoclopramida": "La metoclopramida es un antiemético y procinético utilizado para las náuseas, los vómitos y el reflujo gastroesofágico. Actúa acelerando el vaciamiento gástrico.",
    "ipratropio": "El ipratropio es un broncodilatador anticolinérgico utilizado en la EPOC y el asma como tratamiento de mantenimiento. Actúa dilatando los bronquios por un mecanismo diferente al salbutamol.",
    "sildenafil": "El sildenafil es el principio activo del Viagra, utilizado para la disfunción eréctil. También tiene indicación médica para la hipertensión pulmonar.",
    "cetirizina": "La cetirizina es un antihistamínico de segunda generación utilizado para la rinitis alérgica, la urticaria y las alergias cutáneas. Produce menos somnolencia que los antihistamínicos clásicos.",
    "loratadina": "La loratadina es un antihistamínico de segunda generación sin efecto sedante. Es uno de los más utilizados en Argentina para las alergias estacionales.",
    "pantoprazol": "El pantoprazol es un inhibidor de la bomba de protones similar al omeprazol. Se usa para la gastritis, el reflujo y la prevención de úlceras en pacientes que toman AINEs.",
    "aciclovir": "El aciclovir es un antiviral utilizado para el tratamiento del herpes zóster, el herpes genital y el herpes labial. Reduce la duración y la gravedad de los brotes.",
    "azitromicina": "La azitromicina es un antibiótico macrólido de administración corta (generalmente 3 a 5 días) indicado para infecciones respiratorias, de piel y de transmisión sexual.",
    "bupropion": "El bupropión es un antidepresivo atípico también aprobado para dejar de fumar. Actúa sobre la dopamina y la noradrenalina, sin afectar la serotonina.",
    "etinilestradiol-levonorgestrel": "Es uno de los anticonceptivos orales combinados más recetados en Argentina. Se toma en ciclos mensuales y también reduce el sangrado menstrual y el acné en muchas usuarias.",
    "drospirenona-etinilestradiol": "Anticonceptivo oral combinado con un progestágeno de perfil antiandrogénico. Suele indicarse también para el acné y el síndrome premenstrual.",
    "desogestrel": "Anticonceptivo de progestágeno solo (\"minipíldora\"), sin estrógeno. Es una opción para quienes no pueden tomar anticonceptivos combinados, como durante la lactancia.",
    "clopidogrel": "El clopidogrel previene la formación de coágulos al inhibir la agregación plaquetaria. Se indica frecuentemente tras un infarto, un ACV o la colocación de un stent coronario.",
    "warfarina": "La warfarina es un anticoagulante clásico que requiere controles periódicos de RIN (razón internacional normalizada) para ajustar la dosis. Se usa en fibrilación auricular y prevención de trombosis.",
    "rivaroxaban": "El rivaroxaban es un anticoagulante de acción directa que no requiere los controles de sangre frecuentes que exige la warfarina. Se usa en fibrilación auricular y tromboembolismo venoso.",
    "bisoprolol": "El bisoprolol es un betabloqueante cardioselectivo usado para la hipertensión, la angina y la insuficiencia cardíaca. Reduce la frecuencia cardíaca y la demanda de oxígeno del corazón.",
    "metoprolol": "El metoprolol es un betabloqueante muy utilizado tras un infarto y en arritmias, además de la hipertensión. Existe en formulaciones de liberación inmediata y prolongada.",
    "ramipril": "El ramipril es un IECA (inhibidor de la enzima convertidora de angiotensina) indicado para la hipertensión y la protección cardiovascular y renal, especialmente en personas con diabetes.",
    "valsartan": "El valsartán es un ARA-II (bloqueador del receptor de angiotensina II), una alternativa a los IECA para quienes desarrollan tos con enalapril u otros -pril.",
    "telmisartan": "El telmisartán es un ARA-II de acción prolongada (una toma diaria) usado para la hipertensión y la protección cardiovascular.",
    "rosuvastatina": "La rosuvastatina es una estatina de alta potencia para reducir el colesterol LDL. Suele preferirse sobre la atorvastatina cuando se necesita mayor reducción con dosis más bajas.",
    "digoxina": "La digoxina es un cardiotónico de uso antiguo pero vigente en la insuficiencia cardíaca y ciertas arritmias como la fibrilación auricular. Tiene un margen terapéutico estrecho y requiere control médico estricto.",
    "amoxicilina-clavulanico": "Combina amoxicilina con ácido clavulánico, que bloquea las betalactamasas de algunas bacterias resistentes. Se usa en infecciones respiratorias, urinarias y de piel que no responden a la amoxicilina sola.",
    "cefalexina": "La cefalexina es un antibiótico cefalosporina de primera generación, útil en infecciones de piel, partes blandas y vías urinarias. Es una alternativa frecuente en alergia leve a la penicilina (con precaución médica).",
    "ciprofloxacina": "La ciprofloxacina es un antibiótico del grupo de las quinolonas, usado principalmente en infecciones urinarias y gastrointestinales. Su uso se reserva cada vez más por el riesgo de resistencia y efectos adversos en tendones.",
    "metronidazol": "El metronidazol trata infecciones por bacterias anaerobias y parásitos como la giardiasis y la tricomoniasis. No se debe combinar con alcohol durante el tratamiento.",
    "nitrofurantoina": "La nitrofurantoína es un antibiótico específico para infecciones urinarias bajas (cistitis). No es eficaz para infecciones renales porque no alcanza buena concentración en sangre.",
    "butilescopolamina": "Conocida en Argentina como Buscapina, alivia los espasmos y cólicos del tubo digestivo y las vías urinarias. Existe sola o combinada con analgésicos como el dipirona.",
    "domperidona": "La domperidona alivia náuseas, vómitos y sensación de pesadez estomacal acelerando el vaciado gástrico. A diferencia de otros antieméticos, no suele atravesar la barrera hematoencefálica.",
    "famotidina": "La famotidina reduce la producción de ácido gástrico, aliviando la acidez y el reflujo. Es una alternativa a los inhibidores de la bomba de protones como el omeprazol.",
    "loperamida": "La loperamida reduce la motilidad intestinal para controlar la diarrea aguda. No debe usarse si hay fiebre alta o sangre en las heces sin consultar antes a un médico.",
    "simeticona": "La simeticona reduce los gases intestinales rompiendo las burbujas que los forman. Suele combinarse con otros medicamentos digestivos para el meteorismo y la distensión abdominal.",
    "tramadol": "El tramadol es un analgésico opioide para dolor moderado a intenso que no responde a los AINEs comunes. Requiere receta archivada y control médico por su potencial de dependencia.",
    "meloxicam": "El meloxicam es un antiinflamatorio con menor efecto sobre el estómago que otros AINEs clásicos, usado en artrosis y artritis. Se toma generalmente una vez al día.",
    "ketorolac": "El ketorolac es un antiinflamatorio de alta potencia analgésica, usado en dolor agudo moderado a severo (posoperatorio, cólico renal). Su uso se limita a pocos días por el riesgo gastrointestinal y renal.",
    "celecoxib": "El celecoxib es un AINE que inhibe selectivamente la COX-2, con menor riesgo de daño gástrico que los AINEs tradicionales. Se usa en artrosis, artritis reumatoidea y dolor agudo.",
    "budesonide": "El budesonide es un corticoide de uso inhalatorio (asma, EPOC) o nasal (rinitis alérgica), con acción local y baja absorción sistémica en comparación con los corticoides orales.",
    "montelukast": "El montelukast se usa en el asma y la rinitis alérgica bloqueando los leucotrienos, sustancias inflamatorias de las vías respiratorias. Se toma por vía oral, generalmente por la noche.",
    "fluticasona": "La fluticasona es un corticoide inhalatorio o nasal usado en asma, EPOC y rinitis alérgica. Suele combinarse con broncodilatadores como el salmeterol en inhaladores combinados.",
    "clotrimazol": "El clotrimazol es un antifúngico tópico para hongos de piel, pie de atleta y candidiasis vaginal. Se presenta en crema, óvulos y solución según la indicación.",
    "fluconazol": "El fluconazol es un antifúngico oral de dosis única frecuente para la candidiasis vaginal, y en esquemas más prolongados para otras micosis. Se metaboliza en el hígado, por lo que interactúa con varios medicamentos.",
    "mupirocina": "La mupirocina es un antibiótico de uso exclusivamente tópico para infecciones bacterianas de piel como el impétigo. También se usa para eliminar el estafilococo de las fosas nasales en portadores.",
    "acido-folico": "El ácido fólico (vitamina B9) es esencial en el embarazo para prevenir defectos del tubo neural, por lo que se indica desde antes de la concepción. También se usa en ciertas anemias.",
    "complejo-b": "El complejo B agrupa vitaminas B1, B6, B12 y otras, usadas en neuropatías, fatiga y como suplemento general. No reemplaza una dieta equilibrada ni el tratamiento de la causa de fondo.",
    "vitamina-d": "La vitamina D (colecalciferol) es clave para la absorción de calcio y la salud ósea. Su déficit es frecuente en Argentina por baja exposición solar, y se corrige con suplementos orales.",
    "sulfato-ferroso": "El sulfato ferroso trata y previene la anemia por déficit de hierro, común en embarazadas y personas con sangrados crónicos. Se recomienda tomarlo lejos de las comidas para mejorar su absorción, aunque puede causar molestias digestivas.",
    "dorzolamida-timolol": "Combina dos mecanismos para reducir la presión intraocular en el glaucoma: la dorzolamida (inhibidor de la anhidrasa carbónica) y el timolol (betabloqueante). Se aplica en gotas oftálmicas.",
    "latanoprost": "El latanoprost es un colirio análogo de las prostaglandinas usado en el glaucoma para reducir la presión intraocular, generalmente con una sola aplicación diaria.",
    "desloratadina": "La desloratadina es un antihistamínico de segunda generación, metabolito activo de la loratadina, usado para alergias y urticaria con bajo efecto sedante.",
    "levocetirizina": "La levocetirizina es el isómero activo de la cetirizina, usado en rinitis alérgica y urticaria crónica con buena eficacia a dosis más bajas.",
    "melatonina": "La melatonina es una hormona que regula el ciclo de sueño, usada como ayuda para conciliar el sueño y en el jet lag. En Argentina se vende como suplemento, con concentraciones variables según el producto.",
    "acetilcisteina": "La acetilcisteína es un mucolítico que fluidifica las secreciones respiratorias, facilitando su expulsión en resfríos, bronquitis y otras afecciones con mucosidad espesa.",
    "ambroxol": "El ambroxol es un mucolítico y expectorante muy usado en jarabe para la tos productiva y las afecciones respiratorias con exceso de flema.",
}

# ── DROGAS RELACIONADAS ────────────────────────────────────────────────
RELACIONADAS = {
    "omeprazol": ["pantoprazol", "metoclopramida"],
    "pantoprazol": ["omeprazol", "metoclopramida"],
    "metformina": ["glibenclamida", "insulina"],
    "glibenclamida": ["metformina", "insulina"],
    "insulina": ["insulina-glargina", "metformina"],
    "insulina-glargina": ["insulina", "metformina"],
    "enalapril": ["losartan", "amlodipina", "hidroclorotiazida"],
    "losartan": ["enalapril", "amlodipina", "losartan-hidroclorotiazida"],
    "losartan-hidroclorotiazida": ["losartan", "enalapril", "hidroclorotiazida"],
    "amlodipina": ["enalapril", "losartan", "carvedilol"],
    "carvedilol": ["enalapril", "amlodipina"],
    "hidroclorotiazida": ["clortalidona", "furosemida", "espironolactona"],
    "clortalidona": ["hidroclorotiazida", "furosemida"],
    "furosemida": ["hidroclorotiazida", "espironolactona"],
    "espironolactona": ["furosemida", "hidroclorotiazida"],
    "ibuprofeno": ["naproxeno", "diclofenac", "paracetamol"],
    "naproxeno": ["ibuprofeno", "diclofenac"],
    "diclofenac": ["ibuprofeno", "naproxeno"],
    "paracetamol": ["ibuprofeno", "acido-acetilsalicilico"],
    "acido-acetilsalicilico": ["paracetamol", "ibuprofeno"],
    "clonazepam": ["alprazolam", "lorazepam", "diazepam"],
    "alprazolam": ["clonazepam", "lorazepam", "diazepam"],
    "lorazepam": ["clonazepam", "alprazolam", "diazepam"],
    "diazepam": ["clonazepam", "alprazolam", "lorazepam"],
    "sertralina": ["escitalopram", "fluoxetina", "venlafaxina"],
    "escitalopram": ["sertralina", "fluoxetina", "venlafaxina"],
    "fluoxetina": ["sertralina", ["escitalopram"], "venlafaxina"],
    "venlafaxina": ["sertralina", "escitalopram", "bupropion"],
    "bupropion": ["venlafaxina", "sertralina"],
    "risperidona": ["quetiapina", "olanzapina", "haloperidol"],
    "quetiapina": ["risperidona", "olanzapina", "haloperidol"],
    "olanzapina": ["risperidona", "quetiapina", "haloperidol"],
    "haloperidol": ["risperidona", "quetiapina", "levomepromazina"],
    "levomepromazina": ["haloperidol", "quetiapina"],
    "clozapina": ["risperidona", "quetiapina", "olanzapina"],
    "carbamazepina": ["valproato", "fenobarbital", "pregabalina"],
    "valproato": ["carbamazepina", "litio", "pregabalina"],
    "fenobarbital": ["carbamazepina", "valproato"],
    "pregabalina": ["gabapentina", "carbamazepina"],
    "gabapentina": ["pregabalina", "carbamazepina"],
    "litio": ["valproato", "quetiapina"],
    "amoxicilina": ["azitromicina", "aciclovir"],
    "azitromicina": ["amoxicilina"],
    "aciclovir": ["azitromicina"],
    "salbutamol": ["ipratropio"],
    "ipratropio": ["salbutamol"],
    "cetirizina": ["loratadina"],
    "loratadina": ["cetirizina"],
    "atorvastatina": ["losartan", "enalapril"],
    "levotiroxina": ["metformina"],
    "betametasona": ["prednisona"],
    "prednisona": ["betametasona", "ibuprofeno"],
    "levodopa-carbidopa": ["pregabalina"],
    "zolpidem": ["clonazepam", "lorazepam"],
    "sildenafil": [],
    "metoclopramida": ["omeprazol", "pantoprazol"],
    "etinilestradiol-levonorgestrel": ["drospirenona-etinilestradiol", "desogestrel"],
    "drospirenona-etinilestradiol": ["etinilestradiol-levonorgestrel", "desogestrel"],
    "desogestrel": ["etinilestradiol-levonorgestrel", "drospirenona-etinilestradiol"],
    "clopidogrel": ["rivaroxaban", "warfarina", "acido-acetilsalicilico"],
    "warfarina": ["rivaroxaban", "clopidogrel"],
    "rivaroxaban": ["warfarina", "clopidogrel"],
    "bisoprolol": ["carvedilol", "metoprolol"],
    "metoprolol": ["bisoprolol", "carvedilol"],
    "ramipril": ["enalapril", "losartan"],
    "valsartan": ["losartan", "telmisartan"],
    "telmisartan": ["losartan", "valsartan"],
    "rosuvastatina": ["atorvastatina"],
    "digoxina": ["furosemida", "carvedilol"],
    "amoxicilina-clavulanico": ["amoxicilina", "cefalexina"],
    "cefalexina": ["amoxicilina", "amoxicilina-clavulanico"],
    "ciprofloxacina": ["nitrofurantoina", "metronidazol"],
    "metronidazol": ["ciprofloxacina", "nitrofurantoina"],
    "nitrofurantoina": ["ciprofloxacina", "cefalexina"],
    "butilescopolamina": ["simeticona", "domperidona"],
    "domperidona": ["metoclopramida", "butilescopolamina"],
    "famotidina": ["omeprazol", "pantoprazol"],
    "loperamida": ["simeticona", "butilescopolamina"],
    "simeticona": ["butilescopolamina", "loperamida"],
    "tramadol": ["paracetamol", "ibuprofeno"],
    "meloxicam": ["diclofenac", "celecoxib"],
    "ketorolac": ["diclofenac", "tramadol"],
    "celecoxib": ["meloxicam", "diclofenac"],
    "budesonide": ["salbutamol", "ipratropio", "montelukast"],
    "montelukast": ["budesonide", "cetirizina"],
    "fluticasona": ["budesonide", "salbutamol"],
    "clotrimazol": ["fluconazol", "mupirocina"],
    "fluconazol": ["clotrimazol"],
    "mupirocina": ["clotrimazol"],
    "acido-folico": ["complejo-b", "sulfato-ferroso"],
    "complejo-b": ["acido-folico", "vitamina-d"],
    "vitamina-d": ["complejo-b", "sulfato-ferroso"],
    "sulfato-ferroso": ["acido-folico", "vitamina-d"],
    "dorzolamida-timolol": ["latanoprost"],
    "latanoprost": ["dorzolamida-timolol"],
    "desloratadina": ["loratadina", "cetirizina"],
    "levocetirizina": ["cetirizina", "desloratadina"],
    "melatonina": ["zolpidem", "clonazepam"],
    "acetilcisteina": ["ambroxol"],
    "ambroxol": ["acetilcisteina"],
}

DROGAS = list(ACCIONES.keys())

with open(DATA_DIR / "medicamentos.json", encoding='utf-8') as f:
    data = json.load(f)

medicamentos = data.get('medicamentos', [])
HOY     = datetime.now().strftime("%d/%m/%Y")
HORA    = datetime.now().strftime("%H:%M")
LASTMOD = datetime.now().strftime("%Y-%m-%d")

por_droga: dict[str, list] = {}
for m in medicamentos:
    d = m.get('droga', '').lower().strip()
    if d:
        por_droga.setdefault(d, []).append(m)


def esc(val) -> str:
    return html_module.escape(str(val)) if val else ''


def generar_filas_tabla(meds: list) -> str:
    filas = ""
    for m in meds[:60]:
        precio = m.get('precio', 0) or 0
        marca  = esc(m.get('marca', 'N/A'))
        pres   = esc(m.get('presentacion', 'N/A'))
        lab    = esc(m.get('laboratorio', 'N/A'))
        filas += (
            f'<tr>'
            f'<td class="col-marca">{marca}</td>'
            f'<td class="col-pres">{pres}</td>'
            f'<td class="col-lab">{lab}</td>'
            f'<td class="col-precio">${precio:,.2f}</td>'
            f'</tr>\n'
        )
    return filas


def generar_lista_marcas(meds: list) -> str:
    vistas: list[str] = []
    html = ""
    for m in meds:
        marca = m.get('marca', '')
        if marca and marca not in vistas:
            vistas.append(marca)
            html += f'<span class="marca-chip">{esc(marca)}</span>'
        if len(vistas) >= 15:
            break
    return html


def generar_stats(meds: list, nombre: str) -> str:
    """Genera bloque de estadísticas únicas basadas en datos reales."""
    if not meds:
        return ''

    precios = [m.get('precio', 0) or 0 for m in meds if m.get('precio')]
    if not precios:
        return ''

    precio_min  = min(precios)
    precio_max  = max(precios)
    precio_prom = statistics.mean(precios)
    n_marcas    = len(set(m.get('marca', '') for m in meds if m.get('marca')))
    n_labs      = len(set(m.get('laboratorio', '') for m in meds if m.get('laboratorio')))

    # Marca más barata
    mas_barato = min(meds, key=lambda m: m.get('precio', 999999) or 999999)
    marca_barata = esc(mas_barato.get('marca', ''))
    precio_barato = mas_barato.get('precio', 0) or 0

    return f'''<div class="landing-resumen">
    <h2>Resumen de precios de {esc(nombre)}</h2>
    <div class="about-stats-grid">
        <div class="stat-card">
            <div class="stat-label">Precio más bajo</div>
            <div class="stat-value">${precio_min:,.0f}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Precio promedio</div>
            <div class="stat-value">${precio_prom:,.0f}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Precio más alto</div>
            <div class="stat-value">${precio_max:,.0f}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Marcas disponibles</div>
            <div class="stat-value">{n_marcas}</div>
        </div>
    </div>
    <p class="landing-resumen-nota">
        Opción más económica: <strong>{marca_barata}</strong> a <strong>${precio_barato:,.2f}</strong> · {n_labs} laboratorios en el mercado
    </p>
</div>'''


def generar_relacionadas(droga_slug: str) -> str:
    """Genera sección de drogas relacionadas."""
    relacionadas = RELACIONADAS.get(droga_slug, [])
    # Filtrar las que son listas anidadas por error
    relacionadas = [r for r in relacionadas if isinstance(r, str) and r in ACCIONES]
    if not relacionadas:
        return ''

    items = ''
    for r in relacionadas[:3]:
        nombre_r = r.replace('-', ' ').replace('_', ' ').title()
        accion_r = ACCIONES.get(r, '')
        items += f'''<a href="{r}.html" class="relacionado-card">
            <div class="relacionado-nombre">{esc(nombre_r)}</div>
            <div class="relacionado-accion">{esc(accion_r)}</div>
        </a>'''

    return f'''<section class="relacionados">
    <h2>Medicamentos relacionados</h2>
    <div class="relacionados-grid">
        {items}
    </div>
</section>'''


def generar_faq(nombre: str, accion: str, precio_rango: str, n_marcas: int, precio_min: float) -> str:
    """Genera FAQ expandida con 4 preguntas únicas."""
    return f'''<section class="faq-landing">
    <h2>Preguntas frecuentes sobre {esc(nombre)}</h2>

    <details open>
        <summary>¿Cuánto cuesta {esc(nombre)} en Argentina hoy?</summary>
        <p>{precio_rango} Los precios varían según la marca, la presentación y el laboratorio. El precio más bajo disponible actualmente es de ${precio_min:,.0f} ARS. Consultá la tabla actualizada arriba para ver todas las opciones.</p>
    </details>

    <details open>
        <summary>¿Cuál es la acción terapéutica de {esc(nombre)}?</summary>
        <p>{esc(accion)}. Consultá siempre con tu médico antes de iniciar, modificar o interrumpir cualquier tratamiento.</p>
    </details>

    <details>
        <summary>¿Cuántas marcas de {esc(nombre)} hay en Argentina?</summary>
        <p>Según los datos actuales de SIAFAR/COFA, hay <strong>{n_marcas} marcas</strong> comerciales de {esc(nombre)} disponibles en el mercado argentino. Incluyen tanto versiones de marca como genéricos.</p>
    </details>

    <details>
        <summary>¿Los precios de {esc(nombre)} se actualizan seguido?</summary>
        <p>Los precios en remedi.ar se actualizan automáticamente dos veces al día (a las 10:30 y 18:00 hs de Argentina) a partir de los datos oficiales publicados por SIAFAR/COFA. Los precios son orientativos; te recomendamos confirmar en tu farmacia antes de comprar.</p>
    </details>
</section>'''


# ── Mapeo de slugs a la forma exacta del campo 'droga' en medicamentos.json ──
# El slug se mantiene sin tilde (URL/SEO), pero el campo 'droga' real del
# dataset (SIAFAR/COFA) sí lleva acentuación, y algunas combinaciones usan
# coma en vez de guion/espacio. Sin este mapeo, estos 7 casos generaban
# paginas con "Sin datos disponibles" pese a existir precios reales.
SLUG_A_DROGA_REAL = {
    "rivaroxaban":                   "rivaroxabán",
    "telmisartan":                   "telmisartán",
    "nitrofurantoina":               "nitrofurantoína",
    "acetilcisteina":                "acetilcisteína",
    "valsartan":                     "valsartán",
    "drospirenona-etinilestradiol":  "drospirenona, etinilestradiol",
    "dorzolamida-timolol":           "dorzolamida, timolol",
    "butilescopolamina":             "hioscina,n-butilbr.",
    "amoxicilina-clavulanico":       "amoxicilina, clavulánico,ác.",
    "complejo-b":                    "vit.b,complejo",
    "acido-folico":                  "fólico,ác.",
    # vitamina-d: no existe como suplemento individual en el dataset actual.
    # "vitaminas" es la coincidencia mas cercana disponible (generica, 2
    # registros) -- se prefiere sobre "risedronato, calcio carbonato,
    # vitamina d" porque ese es un combo para osteoporosis, no un
    # suplemento de vitamina D. Igual es una aproximacion imperfecta:
    # revisar si en el futuro aparece colecalciferol/ergocalciferol solo.
    "vitamina-d":                    "vitaminas",
    "sulfato-ferroso":               "hierro",
    # etinilestradiol-levonorgestrel: el campo real en el dataset viene
    # truncado a 30 caracteres desde el PDF de origen ("etinilestradio",
    # sin la "l" final) -- se mapea tal cual aparece, no es un typo nuestro.
    "etinilestradiol-levonorgestrel": "levonorgestrel, etinilestradio",
}


# ── GENERAR LANDINGS ───────────────────────────────────────────────────
for droga_slug in DROGAS:
    nombre  = droga_slug.replace('-', ' ').replace('_', ' ').title()
    accion  = ACCIONES.get(droga_slug, "Medicamento")
    desc    = DESCRIPCIONES.get(droga_slug, f"{nombre} es un medicamento disponible en Argentina. Consultá precios actualizados de todas las marcas y presentaciones.")
    droga_real = SLUG_A_DROGA_REAL.get(droga_slug, droga_slug.replace('-', ' '))
    meds_dr = por_droga.get(droga_real, [])

    if not meds_dr:
        alt = droga_slug.rstrip('ao') + ('a' if droga_slug.endswith('o') else 'o')
        meds_dr = por_droga.get(alt.replace('-', ' '), [])

    # Excluir outliers (vigencia_score < 50) de la tabla y stats
    # para evitar mostrar precios obsoletos o corruptos en las landings
    meds_validos   = [m for m in meds_dr if (m.get('vigencia_score') or 100) >= 50 and (m.get('precio') or 0) > 0]
    meds_ordenados = sorted(meds_validos or meds_dr, key=lambda x: x.get('precio', 0) or 0)
    precios        = [m.get('precio', 0) or 0 for m in meds_validos if m.get('precio')]
    n_marcas       = len(set(m.get('marca', '') for m in meds_dr if m.get('marca')))

    if precios:
        precio_min   = min(precios)
        precio_max   = max(precios)
        precio_rango = f"Precios desde ${precio_min:,.0f} hasta ${precio_max:,.0f} (ARS)."
    else:
        precio_min   = 0
        precio_rango = "Consultá los precios actualizados en la tabla."

    if meds_ordenados:
        filas_tabla  = generar_filas_tabla(meds_ordenados)
        lista_marcas = generar_lista_marcas(meds_ordenados)
        bloque_stats = generar_stats(meds_ordenados, nombre)
    else:
        filas_tabla  = '<tr><td colspan="4" class="sin-datos-tabla">No se encontraron precios para este medicamento en la base de datos actual.</td></tr>'
        lista_marcas = '<p class="sin-datos-marcas">Sin datos disponibles.</p>'
        bloque_stats = ''

    bloque_relacionadas = generar_relacionadas(droga_slug)
    bloque_faq = generar_faq(nombre, accion, precio_rango, n_marcas, precio_min)

    # JSON-LD Drug schema + BreadcrumbList
    drug_ld = {
        "@context": "https://schema.org",
        "@type": "Drug",
        "name": nombre,
        "activeIngredient": nombre,
        "drugClass": accion,
        "description": desc,
        "url": f"https://remedi.ar/{droga_slug}.html",
    }
    if precio_min:
        drug_ld["offers"] = {
            "@type": "AggregateOffer",
            "priceCurrency": "ARS",
            "lowPrice": str(int(precio_min)),
            "highPrice": str(int(precio_max)) if precios else str(int(precio_min)),
            "offerCount": str(len(meds_ordenados)),
        }

    breadcrumb_ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "Inicio",
                "item": "https://remedi.ar/"
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": f"Precio de {nombre} en Argentina",
                "item": f"https://remedi.ar/{droga_slug}.html"
            }
        ]
    }

    json_ld = json.dumps(drug_ld, ensure_ascii=False, indent=2)
    json_ld_breadcrumb = json.dumps(breadcrumb_ld, ensure_ascii=False, indent=2)

    fname = droga_slug + ".html"

    JS_INLINE = """<script>
(function() {
    var btn = document.getElementById('btnTop');
    if (!btn) return;
    window.addEventListener('scroll', function() {
        btn.classList.toggle('visible', window.scrollY > 300);
    }, { passive: true });
    btn.addEventListener('click', function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}());
(function() {
    var wrapper = document.getElementById('tablaWrapper');
    var scroll  = document.getElementById('tablaScroll');
    if (!wrapper || !scroll) return;
    function check() {
        wrapper.classList.toggle('no-overflow', scroll.scrollWidth <= scroll.clientWidth);
    }
    check();
    window.addEventListener('resize', check);
}());
(function() {
    var inp = document.getElementById('buscador');
    var btn = document.getElementById('btnBuscar');
    function ir() {
        var q = inp ? inp.value.trim() : '';
        if (q.length >= 2) window.location.href = 'index.html?q=' + encodeURIComponent(q);
    }
    if (btn) btn.addEventListener('click', ir);
    if (inp) inp.addEventListener('keydown', function(e) { if (e.key === 'Enter') ir(); });
}());
(function() {
    var el = document.getElementById('footer-version');
    if (!el) return;
    fetch('package.json', { cache: 'no-cache' })
        .then(function(res) { if (!res.ok) throw new Error('no ok'); return res.json(); })
        .then(function(pkg) { el.textContent = 'v' + pkg.version; })
        .catch(function() { el.remove(); });
}());
</script>"""

    html_content = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(nombre)}: precio en Argentina hoy | remedi.ar</title>
    <meta name="author" content="remedi.ar">
    <meta name="description" content="Precio de {esc(nombre)} en Argentina hoy. {precio_rango} {n_marcas} marcas disponibles. Datos oficiales SIAFAR/COFA actualizados 2 veces al día. Gratis, sin registro.">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="https://remedi.ar/{droga_slug}.html">
    <link rel="stylesheet" href="style.css">
    <link rel="icon" type="image/svg+xml" href="img/favicon.svg">
    <link rel="manifest" href="manifest.json">
    <meta property="og:title" content="{esc(nombre)}: precio en Argentina — remedi.ar">
    <meta property="og:description" content="Precio de {esc(nombre)} en Argentina. {precio_rango} {n_marcas} marcas. Datos SIAFAR/COFA actualizados 2 veces al día.">
    <meta property="og:url" content="https://remedi.ar/{droga_slug}.html">
    <meta property="og:type" content="article">
    <meta property="og:locale" content="es_AR">
    <meta property="og:image" content="https://remedi.ar/img/og-image.png">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{esc(nombre)}: precio en Argentina — remedi.ar">
    <meta name="twitter:description" content="Precio de {esc(nombre)} en Argentina. {precio_rango}">
    <script type="application/ld+json">
{json_ld}
    </script>
    <script type="application/ld+json">
{json_ld_breadcrumb}
    </script>
</head>
<body>
<div class="hidden">
  <svg xmlns="http://www.w3.org/2000/svg">
    <symbol id="ic-info"   viewBox="0 0 24 24" fill="none" stroke-width="1.8"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></symbol>
    <symbol id="ic-shield" viewBox="0 0 24 24" fill="none" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></symbol>
    <symbol id="ic-file"   viewBox="0 0 24 24" fill="none" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></symbol>
    <symbol id="ic-mail"   viewBox="0 0 24 24" fill="none" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></symbol>
  </svg>
</div>
<div class="container">
    <a href="index.html" class="header-link">
        <header class="header">
            <div class="header-logo-circle">
                <img src="img/favicon.svg" alt="remedi.ar" width="38" height="38">
            </div>
            <div class="header-texto">
                <h1>remedi.ar - Precios de medicamentos</h1>
            </div>
        </header>
    </a>

    <main>
        <nav class="breadcrumb">
            <a href="index.html">Inicio</a>
            <span class="breadcrumb-sep">›</span>
            <span class="breadcrumb-actual">{esc(nombre)}</span>
        </nav>

        <div class="landing-hero">
            <h1>Precio de {esc(nombre)} en Argentina</h1>
            <p class="landing-subtitulo">{esc(accion)}</p>
            <p class="landing-rango-precio">{precio_rango}</p>
        </div>

        <p class="landing-descripcion">
            {esc(desc)}
        </p>

        {bloque_stats}

        <div class="aviso-medico">
            <p>
                <strong>Aviso médico:</strong> La información de este sitio es de carácter informativo y no reemplaza la consulta con un médico o farmacéutico. Ante cualquier duda sobre medicamentos, dosificación o tratamientos, consultá con un profesional de la salud.
            </p>
        </div>

        <div class="landing-seccion">
            <h2>Precios actualizados de {esc(nombre)}</h2>

            <p class="scroll-hint">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="9 18 15 12 9 6"/>
                </svg>
                Deslizá para ver más columnas
            </p>

            <div class="tabla-wrapper" id="tablaWrapper">
                <div class="tabla-scroll" id="tablaScroll">
                    <table class="tabla-precios">
                        <thead>
                            <tr>
                                <th>Marca</th>
                                <th>Presentación</th>
                                <th>Laboratorio</th>
                                <th>Precio público</th>
                            </tr>
                        </thead>
                        <tbody>
{filas_tabla}
                        </tbody>
                    </table>
                </div>
            </div>
            <p class="landing-tabla-nota">
                Fuente: SIAFAR / COFA · Precios orientativos · Actualizado {HOY} {HORA} hs.
            </p>
        </div>

        <div class="marcas-comerciales">
            <h2>Marcas comerciales de {esc(nombre)}</h2>
            <div class="marcas-comerciales-lista">
{lista_marcas}
            </div>
        </div>

        {bloque_faq}

        {bloque_relacionadas}

        <div class="buscar-otro-card">
            <h2>Buscar otro medicamento</h2>
            <p>Encontrá precios de cualquier medicamento en Argentina</p>
            <div class="busqueda-section">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="10" cy="10" r="7"/><line x1="15" y1="15" x2="21" y2="21"/>
                </svg>
                <input type="search" id="buscador"
                    placeholder="Ej: Paracetamol, Amoxicilina, Ibuprofeno..."
                    autocomplete="off">
                <button id="btnBuscar">
                    Buscar
                </button>
            </div>
        </div>
    </main>

    <footer class="footer">
        <div class="footer-fuentes">
            Fuente de datos:
            <a href="https://siafar.com/precios/pdf/" target="_blank" rel="noopener">SIAFAR / COFA</a>
            <span class="footer-sep">|</span>
            <a href="https://datos.pami.org.ar/dataset/medicamentos-para-afiliados" target="_blank" rel="noopener">PAMI</a>
        </div>
        <div class="footer-aviso">
            <svg width="14" height="14" aria-hidden="true"><use href="#ic-info"/></svg>
            <span><strong>Aviso médico:</strong> Esta información no reemplaza la consulta con un profesional de la salud. Verificá precios en tu farmacia.</span>
        </div>
        <div class="footer-legal">
            <a href="https://opensource.org/license/mit" target="_blank" rel="noopener">Licencia MIT</a>
            <span class="footer-sep">|</span>
            <span id="footer-version"></span>
        </div>
        <nav class="footer-links">
            <a href="about.html"><svg width="13" height="13" aria-hidden="true"><use href="#ic-info"/></svg>Cómo funciona</a>
            <a href="privacidad.html"><svg width="13" height="13" aria-hidden="true"><use href="#ic-shield"/></svg>Privacidad</a>
            <a href="terminos.html"><svg width="13" height="13" aria-hidden="true"><use href="#ic-file"/></svg>Términos</a>
            <a href="mailto:pablo.s.bella@gmail.com?subject=remedi.ar%20-%20Consulta"><svg width="13" height="13" aria-hidden="true"><use href="#ic-mail"/></svg>Contacto</a>
        </nav>

    </footer>
</div>

<button id="btnTop" aria-label="Volver arriba">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5">
        <polyline points="18 15 12 9 6 15"/>
    </svg>
</button>

{JS_INLINE}
</body>
</html>'''

    out = BASE_DIR / fname
    out.write_text(html_content, encoding='utf-8')
    print(f"✅ {fname}")

print(f"\n✅ {len(DROGAS)} landings generadas.")


# ── GENERAR SITEMAP ────────────────────────────────────────────────────
def generar_sitemap():
    urls = []
    urls.append(f"""  <url>
    <loc>https://remedi.ar/</loc>
    <lastmod>{LASTMOD}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>""")
    for droga_slug in DROGAS:
        urls.append(f"""  <url>
    <loc>https://remedi.ar/{droga_slug}.html</loc>
    <lastmod>{LASTMOD}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>""")
    for slug, freq, pri in [("privacidad", "monthly", "0.3"), ("terminos", "monthly", "0.3")]:
        urls.append(f"""  <url>
    <loc>https://remedi.ar/{slug}.html</loc>
    <lastmod>{LASTMOD}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{pri}</priority>
  </url>""")

    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += '\n'.join(urls)
    sitemap += '\n</urlset>'

    out = BASE_DIR / "sitemap.xml"
    out.write_text(sitemap, encoding='utf-8')
    print(f"✅ sitemap.xml generado con {len(urls)} URLs ({LASTMOD})")

generar_sitemap()
