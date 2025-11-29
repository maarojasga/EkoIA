import { motion } from 'framer-motion';
import { Target, CheckCircle2, Sparkles } from 'lucide-react';

const ProjectInfo = () => {
  const fadeInUp = {
    initial: { opacity: 0, y: 30 },
    whileInView: { opacity: 1, y: 0 },
    viewport: { once: true },
    transition: { duration: 0.6 }
  };

  return (
    <div className="py-20 bg-background">
      <div className="container mx-auto px-6">
        {/* Introduction */}
        <motion.div {...fadeInUp} className="max-w-4xl mx-auto text-center mb-20">
          <h2 className="text-4xl md:text-5xl font-heading font-bold text-foreground mb-6">
            EcoBalance360
          </h2>
          <p className="text-lg text-muted-foreground leading-relaxed">
            Buscamos analizar y visualizar el balance de carbono en Colombia, identificar territorios emisores y sumideros de CO₂, 
            y utilizar estos datos para tomar decisiones de mitigación y compensación climática. Este proyecto se enfoca en el 
            desarrollo sostenible mediante el uso de datos abiertos para la gestión ambiental y la transición hacia prácticas 
            más sostenibles en áreas clave como la energía, agricultura y uso del suelo.
          </p>
        </motion.div>

        {/* Objetivo General */}
        <motion.div {...fadeInUp} className="max-w-5xl mx-auto mb-20" id="objetivos">
          <div className="bg-gradient-secondary p-10 rounded-2xl shadow-card text-white">
            <div className="flex items-start gap-4 mb-4">
              <div className="p-3 bg-white/20 rounded-xl">
                <Target className="w-8 h-8" />
              </div>
              <div>
                <h3 className="text-3xl font-heading font-bold mb-4">Objetivo General</h3>
                <p className="text-lg leading-relaxed text-white/90">
                  Desarrollar una herramienta de analítica territorial que permita visualizar y predecir el balance de carbono 
                  en Colombia, identificando zonas emisoras y sumideros de CO₂, a partir de datos abiertos, con el fin de apoyar 
                  la toma de decisiones para la mitigación del cambio climático en los territorios colombianos.
                </p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Objetivos Específicos */}
        <motion.div {...fadeInUp} className="max-w-5xl mx-auto mb-20">
          <h3 className="text-3xl font-heading font-bold text-center text-foreground mb-12">
            Objetivos Específicos
          </h3>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                number: "01",
                title: "Datos Abiertos",
                description: "Recopilar y normalizar los datos abiertos disponibles sobre calidad del aire, emisiones de CO₂, y cobertura forestal en Colombia, para calcular el balance de carbono en cada municipio y generar un índice de equilibrio climático."
              },
              {
                number: "02",
                title: "Mapa Interactivo",
                description: "Crear un mapa interactivo con tecnologías geoespaciales (GeoPandas, QGIS) para visualizar el balance de carbono, y aplicar modelos predictivos (machine learning) para estimar las emisiones de CO₂ y la captura de carbono a futuro."
              },
              {
                number: "03",
                title: "Recomendaciones",
                description: "Proporcionar recomendaciones específicas a nivel municipal sobre acciones de mitigación y compensación climática, basadas en los resultados obtenidos del análisis de emisiones y captura de carbono."
              }
            ].map((objetivo, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="bg-card p-8 rounded-xl shadow-card border border-border hover:shadow-elegant transition-all group"
              >
                <div className="text-5xl font-heading font-black text-primary/20 mb-4 group-hover:text-primary/40 transition-colors">
                  {objetivo.number}
                </div>
                <h4 className="text-xl font-heading font-bold text-foreground mb-3">
                  {objetivo.title}
                </h4>
                <p className="text-muted-foreground leading-relaxed">
                  {objetivo.description}
                </p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Impacto */}
        <motion.div {...fadeInUp} className="max-w-5xl mx-auto">
          <div className="bg-gradient-primary p-10 rounded-2xl shadow-elegant text-white">
            <div className="flex items-start gap-4 mb-6">
              <div className="p-3 bg-white/20 rounded-xl">
                <Sparkles className="w-8 h-8" />
              </div>
              <h3 className="text-3xl font-heading font-bold">Impacto Esperado</h3>
            </div>
            <ul className="space-y-4 text-lg">
              {[
                "La herramienta proporcionará a ciudadanos, gobiernos locales y empresas una visión clara de las zonas emisoras y los sumideros de carbono en Colombia, lo que les permitirá tomar decisiones informadas sobre sus acciones climáticas y energéticas.",
                "A través de las recomendaciones del modelo, los municipios podrán priorizar las acciones de mitigación y compensación, como reforestación o proyectos de energía limpia, contribuyendo a la sostenibilidad ambiental y cumpliendo con los compromisos nacionales e internacionales en relación con los ODS 13 y 15.",
                "La integración de datos abiertos permitirá que las políticas públicas y los proyectos privados se orienten hacia la reducción de emisiones y el aumento de la captura, lo que acelerará la transición hacia una economía baja en carbono.",
                "El uso de esta herramienta fortalecerá la capacidad de los municipios y otras entidades públicas para adaptarse al cambio climático de manera proactiva, alineando los esfuerzos de mitigación y adaptación."
              ].map((item, index) => (
                <motion.li
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  className="flex items-start gap-3"
                >
                  <CheckCircle2 className="w-6 h-6 flex-shrink-0 mt-1" />
                  <span className="text-white/90">{item}</span>
                </motion.li>
              ))}
            </ul>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default ProjectInfo;
