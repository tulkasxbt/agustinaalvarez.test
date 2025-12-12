import os
import re

BASE_DIR = r"d:\Proyectos\Web\agustinaalvarez.com - auto"

# TEXT VARIATIONS
VARIATIONS = {
    "botox": {
        "root": "La toxina botulínica es el estándar de oro en Buenos Aires para suavizar arrugas de expresión y refrescar la mirada. Se aplica estratégicamente para relajar la musculatura facial manteniendo la naturalidad.",
        "belgrano": "En nuestro centro de Belgrano, la aplicación de toxina botulínica es uno de los tratamientos más solicitados por vecinos de la zona. Buscamos resultados sutiles que respeten tus rasgos, ideales para pacientes de Belgrano R y C.",
        "palermo": "Descubrí el efecto de la toxina botulínica en Palermo (CABA). Un procedimiento rápido, ideal para el ritmo de vida de Palermo, que devuelve frescura al rostro suavizando gestos sin perder expresividad.",
        "nunez": "En Núñez, ofrecemos tratamientos de toxina botulínica con la máxima precisión médica. Si vivís en la zona norte o Núñez, acercate para rejuvenecer tu mirada con técnicas avanzadas y seguras."
    },
    "sculptra": {
        "root": "Sculptra es un bioestimulador de colágeno de primera línea en CABA. Restaura la estructura dérmica y recupera la firmeza perdida con el tiempo, brindando un efecto lifting natural y progresivo.",
        "belgrano": "Para nuestras pacientes en Belgrano, Sculptra es la opción elegida para combatir la flacidez sin cirugía. Este bioestimulador regenera tu propio colágeno, logrando una piel firme y radiante en pleno corazón de Belgrano.",
        "palermo": "En Palermo, la demanda de tratamientos que mejoran la calidad de piel crece. Sculptra ofrece en nuestra sede una biostimulación potente para recuperar contornos definidos con un acabado totalmente natural.",
        "nunez": "Sculptra en Núñez: la solución para tensar la piel desde adentro. Ideal para quienes buscan resultados duraderos y naturales en la zona de Núñez, estimulando la regeneración biológica de la piel."
    },
    "rellenos": { # acido_hialuronico
        "root": "Los rellenos de ácido hialurónico en Buenos Aires permiten reponer volúmenes, atenuar surcos y embellecer el rostro. Utilizamos marcas premium para garantizar seguridad y durabilidad en cada aplicación.",
        "belgrano": "En Belgrano realizamos rellenos de ácido hialurónico con un enfoque artístico y médico. Devolvemos el volumen perdido en pómulos o mentón, siempre priorizando la armonía facial que buscan nuestros pacientes de Belgrano.",
        "palermo": "Armonización facial con ácido hialurónico en Palermo (CABA). Resaltamos tus mejores rasgos y suavizamos líneas de cansancio. Un toque de frescura disponible cerca de tu casa en Palermo.",
        "nunez": "Rellenos faciales en Núñez para una apariencia descansada. Si estás en Núñez y buscás mejorar surcos o definir ángulos, el ácido hialurónico es tu aliado con resultados inmediatos y seguros."
    },
    "labios": { # relleno_labios
        "root": "El relleno de labios en CABA es un arte que busca equilibrio y sensualidad. Hidratación, perfilado y volumen sutil son las claves de nuestros tratamientos labiales en la ciudad.",
        "belgrano": "Labios definidos y naturales en Belgrano. Nos especializamos en técnicas que evitan el exceso ('duck face'), priorizando la forma y la hidratación que prefieren nuestras pacientes de Belgrano.",
        "palermo": "Diseño de labios en Palermo (CABA). Ya sea que busques un volumen audaz o solo hidratación (Glossy Lips), en nuestro consultorio de Palermo personalizamos la técnica a tu estilo.",
        "nunez": "Perfilado y volumen de labios en Núñez. Realzamos tu sonrisa con ácido hialurónico de alta gama. Consultá en Núñez por nuestros protocolos de Lips Refresh para un look renovado."
    },
    "radiesse": {
        "root": "Radiesse es un inductor de colágeno dual que aporta tensión y define el óvalo facial. Disponible en Buenos Aires, es ideal para tratar la flacidez y mejorar la calidad de la piel simultáneamente.",
        "belgrano": "Radiesse en Belgrano: el secreto para un efecto lifting sin cirugía. Recuperá la definición de tu mandíbula y tensá tu piel con este tratamiento estrella en nuestra clínica de Belgrano.",
        "palermo": "Definición y firmeza con Radiesse en Palermo. Si sentís que tu piel perdió tensión, este bioestimulador es la solución perfecta que ofrecemos a nuestros pacientes de la zona de Palermo.",
        "nunez": "Tensado facial con Radiesse en Núñez. Combatí la flacidez y mejorá la textura de tu piel con hidroxiapatita de calcio, un tratamiento seguro y eficaz disponible ahora en Núñez."
    },
    "enzimas": { # enzimas_pbserum
        "root": "Las enzimas PBSerum en CABA revolucionan el tratamiento de grasa localizada y flacidez. Un cóctel biológico que disuelve adiposidad y reafirma tejidos sin necesidad de quirófano.",
        "belgrano": "Reducción de papada y afinamiento facial con enzimas en Belgrano. Olvidate de la grasa localizada con este tratamiento innovador que ofrecemos para la comunidad de Belgrano.",
        "palermo": "Enzimas recombinantes en Palermo (CABA). Modelá tu rostro y cuerpo con la última tecnología biológica. Resultados visibles en pocas sesiones para nuestros pacientes de Palermo.",
        "nunez": "Tratamiento enzimático en Núñez. Si buscás eliminar adiposidad localizada en rostro o cuerpo, las enzimas PBSerum son tu mejor opción en nuestra sede de Núñez."
    },
    "peeling": {
        "root": "Los peelings médicos en Buenos Aires renuevan tu piel, tratando manchas, poros dilatados y opacidad. Personalizamos los ácidos para cada fototipo y necesidad dermatológica.",
        "belgrano": "Renovación celular con peeling en Belgrano. Ideal para el cambio de estación, nuestros peelings médicos devuelven la luminosidad a tu piel. Consultá en Belgrano por el protocolo ideal para vos.",
        "palermo": "Peeling químico en Palermo para una piel Glow. Eliminá imperfecciones y unificá el tono de tu piel con nuestros tratamientos exfoliantes diseñados para la piel urbana de Palermo.",
        "nunez": "Peelings dermatológicos en Núñez. Tratamos manchas solares, secuelas de acné y piel apagada con ácidos de uso médico. Acercate a Núñez para renovar tu cutis."
    },
    "laser_qswitch": {
        "root": "El láser Q-Switch en CABA es la tecnología de elección para eliminar manchas solares, melasma y tatuajes. Un tratamiento potente y preciso para una piel uniforme.",
        "belgrano": "Láser Q-Switch en Belgrano: adiós a las manchas. Recuperá el tono uniforme de tu piel con nuestra tecnología láser avanzada, disponible para todos los vecinos de Belgrano.",
        "palermo": "Eliminación de manchas y tatuajes en Palermo (CABA). Con el láser Q-Switch logramos borrar imperfecciones pigmentarias de forma segura. Tecnología de punta en Palermo.",
        "nunez": "Tratamiento de manchas con láser Q-Switch en Núñez. Si el sol dejó huellas en tu piel, nuestro láser en Núñez es la solución efectiva para recuperar una piel limpia y sin manchas."
    },
    "luz_pulsada": {
        "root": "La Luz Pulsada Intensa (IPL) en Buenos Aires es fundamental para tratar rosácea y fotoenvejecimiento. Mejora la calidad global de la piel, cerrando poros y eliminando rojeces.",
        "belgrano": "IPL Luz Pulsada en Belgrano para pieles con rosácea o manchas. Unificá el tono y mejorá la textura de tu rostro con este tratamiento lumínico en el corazón de Belgrano.",
        "palermo": "Rejuvenecimiento con Luz Pulsada en Palermo. Ideal para tratar el daño solar y las rojeces, dejando tu piel suave y luminosa. Descubrilo en nuestra sede de Palermo.",
        "nunez": "Luz Pulsada Intensa en Núñez. Combatí el enrojecimiento y las manchas difusas con sesiones rápidas y efectivas. Tecnología IPL a tu alcance en Núñez."
    },
    "radiofrecuencia": {
        "root": "La radiofrecuencia médica en CABA estimula el colágeno mediante calor profundo. Es el tratamiento no invasivo por excelencia para mantener la firmeza facial y corporal.",
        "belgrano": "Radiofrecuencia tensora en Belgrano. Mantené tu piel firme y elástica con sesiones agradables de radiofrecuencia. El complemento ideal para tu rutina de belleza en Belgrano.",
        "palermo": "Lifting térmico con radiofrecuencia en Palermo (CABA). Estimulá tu colágeno natural y prevení la flacidez con nuestra tecnología de radiofrecuencia en Palermo.",
        "nunez": "Radiofrecuencia facial y corporal en Núñez. Tensado de piel efectivo y sin tiempo de recuperación. Vení a Núñez y probá los beneficios del calor terapéutico."
    },
    "mesoterapia": { # General mesoterapia
        "root": "La mesoterapia facial en Buenos Aires nutre la piel desde el interior. Microinyecciones de vitaminas y activos que revitalizan, hidratan y aportan luminosidad instantánea.",
        "belgrano": "Mesoterapia estética en Belgrano. Un shock de nutrientes para tu piel que combate el cansancio y la deshidratación. Tratamientos personalizados para pacientes de Belgrano.",
        "palermo": "Mesofrench y vitaminas en Palermo. Revitalizá tu rostro con el famoso cóctel de vitaminas. La mesoterapia es el secreto de una piel radiante en Palermo.",
        "nunez": "Nutrición dérmica con mesoterapia en Núñez. Aportale a tu piel lo que las cremas no alcanzan. Vitaminas y ácido hialurónico inyectable en nuestra sede de Núñez."
    },
    "mesoterapia_filorga": { # NCTF
        "root": "NCTF de Filorga es la mesoterapia premium en CABA. Un complejo de más de 50 ingredientes que regenera la piel, cierra poros y aporta un brillo inigualable.",
        "belgrano": "Filorga NCTF 135HA en Belgrano. La mesoterapia de lujo que eligen las celebridades, ahora cerca de tu casa en Belgrano. Calidad suprema para una piel perfecta.",
        "palermo": "Tratamiento Filorga en Palermo (CABA). Experimentá la biorrevitalización celular con el estándar francés de Filorga. Piel de porcelana disponible en Palermo.",
        "nunez": "Mesoterapia Filorga en Núñez. Rejuvenecimiento polivitamínico intenso para pieles exigentes. Descubrí el poder del NCTF en Núñez."
    },
    "erbium": {
        "root": "El láser Erbium en Buenos Aires ofrece un resurfacing efectivo para cicatrices y arrugas finas. Una renovación profunda de la piel con un tiempo de recuperación controlado.",
        "belgrano": "Resurfacing con Láser Erbium en Belgrano. Mejorá cicatrices de acné y textura irregular con la precisión del láser Erbium. Tecnología dermatológica en Belgrano.",
        "palermo": "Láser Erbium en Palermo para piel nueva. Si buscás renovar completamente la superficie de tu piel, nuestro tratamiento láser en Palermo es la indicación precisa.",
        "nunez": "Rejuvenecimiento láser Erbium en Núñez. Eliminá imperfecciones y suavizá tu piel con tecnología ablativa controlada. Consultanos en Núñez."
    },
    "profhilo": {
        "root": "Profhilo en CABA representa una nueva categoría: la bioremodelación. Ácido hialurónico ultrapuro que tensa e hidrata sin aportar volumen, ideal para cara y cuello.",
        "belgrano": "Profhilo en Belgrano: efecto tensor natural. Tratá la laxitud de la piel en rostro y cuello con este innovador producto. Bioremodelación disponible en Belgrano.",
        "palermo": "Hidratación y tensión con Profhilo en Palermo. La solución para pieles apagadas y con flacidez leve. Recuperá la jugosidad de tu piel en Palermo.",
        "nunez": "Tratamiento Profhilo en Núñez. Revertí el envejecimiento cutáneo con la tecnología de IBSA. Ácido hialurónico térmico para pacientes exigentes en Núñez."
    },
    "plasma": { # plasma_rico_plaquetas
        "root": "El Plasma Rico en Plaquetas (PRP) en Buenos Aires es la medicina regenerativa aplicada a la estética. Utiliza tus propios factores de crecimiento para rejuvenecer la piel.",
        "belgrano": "PRP Plasma Rico en Plaquetas en Belgrano. Bioestimulación autóloga y segura. Mejorá la calidad de tu piel con tu propia biología en nuestro centro de Belgrano.",
        "palermo": "Tratamiento Vampiro / PRP en Palermo (CABA). Regeneración celular máxima para rostro y cabello. Descubrí los beneficios del plasma en Palermo.",
        "nunez": "Plasma Rico en Plaquetas en Núñez. Estimulá la producción de colágeno de forma 100% natural. Tratamiento regenerativo disponible en Núñez."
    },
    "skinbooster": { # longlasting implies skinbooster roughly or similar category
        "root": "Los Skinboosters y Long Lasting en CABA hidratan la piel en profundidad. Mejoran la elasticidad y estructura dérmica, creando un efecto de piel de vidrio duradero.",
        "belgrano": "Skinbooster y Long Lasting en Belgrano. Hidratación inyectable profunda para pieles secas o maduras. Recuperá el brillo natural en Belgrano.",
        "palermo": "Efecto Glow con Skinbooster en Palermo. La hidratación que tu crema no logra, la conseguimos con microinyecciones de hialurónico fluido en Palermo.",
        "nunez": "Hidratación profunda Long Lasting en Núñez. Tratamiento de larga duración para mejorar la calidad de piel. Acercate a Núñez para probarlo."
    },
    "capilar": {
        "root": "Nuestros tratamientos capilares en Buenos Aires combinan mesoterapia y tecnología para frenar la caída y fortalecer el cabello. Protocolos médicos para alopecia.",
        "belgrano": "Recuperación capilar en Belgrano. Frená la caída del cabello con nuestros planes personalizados de mesoterapia y plasma en Belgrano.",
        "palermo": "Salud capilar en Palermo (CABA). Fortalecé tu pelo y mejorá su densidad con tratamientos médicos comprobados. Consultá en Palermo.",
        "nunez": "Tratamiento para la caída del cabello en Núñez. Abordaje integral de la alopecia con las mejores técnicas del mercado. Soluciones capilares en Núñez."
    },
    "alquimia": {
        "root": "Alquimia es un protocolo exclusivo de peeling y renovación en CABA. Combina aparatología y activos para una piel radiante y libre de impurezas.",
        "belgrano": "Protocolo Alquimia en Belgrano. Un ritual de renovación facial profunda que limpia y revitaliza. Exclusivo en nuestra sede de Belgrano.",
        "palermo": "Alquimia Facial en Palermo. La limpieza profunda y peeling que tu piel necesita para brillar en la noche de Palermo. Renovación total.",
        "nunez": "Tratamiento Alquimia en Núñez. Combinación de técnicas para una piel perfecta. Descubrí nuestro protocolo firma en Núñez."
    }
}

MAPPING = {
    "botox.html": "botox",
    "sculptra.html": "sculptra",
    "rellenos.html": "rellenos",
    "labios.html": "labios",
    "radiesse.html": "radiesse",
    "enzimas_pbserum.html": "enzimas",
    "peeling.html": "peeling",
    "laser_qswitch.html": "laser_qswitch",
    "luz_pulsada.html": "luz_pulsada",
    "radiofrecuencia.html": "radiofrecuencia",
    "mesoterapia.html": "mesoterapia",
    "mesoterapia_filorga.html": "mesoterapia_filorga",
    "erbium.html": "erbium",
    "profhilo.html": "profhilo",
    "plasma.html": "plasma",
    "longlasting.html": "skinbooster",
    "tratamiento_capilar.html": "capilar",
    "alquimia.html": "alquimia"
}

def rewrite_branch(file_path, flavor):
    print(f"Rewriting {file_path} for {flavor}...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Skipping {file_path}, not found.")
        return

    # We iterate over the file content looking for the cards.
    # Pattern: <a href="KEY.html" ...> ... <div class="card" data-city="..."> ... <p class="line-height-1">TEXT_TO_REPLACE</p>
    
    # It's safer to separate the loop.
    for href, key in MAPPING.items():
        if key not in VARIATIONS:
            continue
            
        new_text = VARIATIONS[key][flavor]
        
        # Regex search pattern refactored
        search_pattern = re.compile(
            fr'(<a href="{href}"[^>]*>.*?<div class="card"[^>]*>\s*<p class="line-height-1">)(.*?)(<span class="dots">)',
            re.DOTALL
        )
        
        # Check if first pattern works (with dots)
        if search_pattern.search(content):
            content = search_pattern.sub(fr'\1{new_text}\3', content)
        else:
            # Try simple pattern (no dots, just closing p)
            search_pattern_simple = re.compile(
                fr'(<a href="{href}"[^>]*>.*?<div class="card"[^>]*>\s*<p class="line-height-1">)(.*?)(</p>)',
                re.DOTALL
            )
            
            match = search_pattern_simple.search(content)
            if match:
                # Only if doesn't contain dots inside
                if '<span class="dots">' not in match.group(2):
                     content = search_pattern_simple.sub(fr'\1{new_text}\3', content)
    
    if flavor == 'root':
        # De-localize title/desc
        content = content.replace("Tratamientos Faciales en Belgrano", "Tratamientos Faciales en Buenos Aires")
        content = content.replace("Facial Treatments in Belgrano", "Facial Treatments in Buenos Aires")
        # Ensure canonical remains "tratamientos.html"
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    # 1. Root
    root_file = os.path.join(BASE_DIR, "tratamientos.html")
    rewrite_branch(root_file, "root")
    
    # 2. Branches
    branches = ["belgrano", "palermo", "nunez"]
    for b in branches:
        path = os.path.join(BASE_DIR, b, "tratamientos.html")
        rewrite_branch(path, b)

if __name__ == "__main__":
    main()
