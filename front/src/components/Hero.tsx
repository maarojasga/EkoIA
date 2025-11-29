import { motion } from 'framer-motion';
import logo from '@/assets/EkoIA.png';

const Hero = () => {
  return (
    // Se cambió el fondo a un tono oscuro (slate-900) para contrastar con el naranja/azul del logo
    <section className="relative min-h-[65vh] flex items-center justify-center overflow-hidden bg-slate-900">
      
      {/* Elementos de fondo animados (blobs) */}
      {/* Se redujo la opacidad para no competir con el logo */}
      <div className="absolute inset-0 opacity-20 pointer-events-none">
        <div className="absolute top-10 left-10 w-64 h-64 bg-primary rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-10 right-10 w-80 h-80 bg-secondary rounded-full blur-3xl animate-float" style={{ animationDelay: '1s' }} />
      </div>

      <div className="container mx-auto px-6 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center flex flex-col items-center"
        >
          {/* Logo Principal */}
          <motion.img
            src={logo}
            alt="EkoIA Logo"
            className="h-54 md:h-80 w-auto object-contain drop-shadow-2xl"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          />
          
          {/* Slogan en texto blanco (Copy) */}
          <motion.p
            className="mt-8 text-xl md:text-2xl font-heading font-medium text-white max-w-3xl mx-auto leading-relaxed tracking-wide"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            Analítica territorial y datos abiertos para un futuro carbono neutral
          </motion.p>
        </motion.div>
      </div>

      {/* Decoración de ola inferior (conecta con el fondo blanco de la siguiente sección) */}
      <div className="absolute bottom-0 left-0 right-0">
        <svg viewBox="0 0 1440 120" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-auto">
          <path d="M0 0L60 10C120 20 240 40 360 46.7C480 53 600 47 720 43.3C840 40 960 40 1080 46.7C1200 53 1320 67 1380 73.3L1440 80V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0V0Z" fill="hsl(var(--background))"/>
        </svg>
      </div>
    </section>
  );
};

export default Hero;