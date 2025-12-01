import Hero from '@/components/Hero';
import ProjectInfo from '@/components/ProjectInfo';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { ArrowRight, LayoutDashboard } from 'lucide-react';
import { Link } from 'react-router-dom';

const Index = () => {
  return (
    <div className="min-h-screen flex flex-col">
      <Hero />
      <ProjectInfo />
      
      {/* Sección CTA para ir al Dashboard */}
      <section className="py-24 bg-muted/30">
        <div className="container mx-auto px-6 text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="max-w-2xl mx-auto"
          >
            <h2 className="text-4xl font-heading font-bold text-foreground mb-6">
              Explora los Datos en Tiempo Real
            </h2>
            <p className="text-lg text-muted-foreground mb-10">
              Accede a nuestro dashboard interactivo para visualizar mapas de calor, 
              analizar tendencias históricas y filtrar emisiones por región y sector económico.
            </p>
            
            <Link to="/dashboard">
              <Button size="lg" className="h-14 px-8 text-lg gap-3 shadow-elegant hover:scale-105 transition-transform">
                <LayoutDashboard className="w-5 h-5" />
                Acceder al Dashboard
                <ArrowRight className="w-5 h-5" />
              </Button>
            </Link>
          </motion.div>
        </div>
      </section>

      <footer className="py-12 bg-secondary text-white mt-auto">
        <div className="container mx-auto px-6 text-center">
          <p className="text-lg mb-2">
            EkoIA - Análisis de Balance de Carbono en Colombia
          </p>
          <p className="text-white/70">
            Desarrollado por EMKUBAR para EkoIA
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Index;