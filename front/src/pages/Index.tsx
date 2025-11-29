import Hero from '@/components/Hero';
import ProjectInfo from '@/components/ProjectInfo';
import Map from '@/components/Map';
import Statistics from '@/components/Statistics';
import { motion } from 'framer-motion';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Map as MapIcon, BarChart3 } from 'lucide-react';

const Index = () => {
  return (
    <div className="min-h-screen">
      <Hero />
      <ProjectInfo />
      
      <section id="dashboard" className="py-20 bg-muted/30">
        <div className="container mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-12"
          >
            <h2 className="text-4xl md:text-5xl font-heading font-bold text-foreground mb-4">
              Explorador de Datos Climáticos
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Visualiza las emisiones de carbono a través de mapas interactivos o análisis estadísticos detallados.
            </p>
          </motion.div>

          <Tabs defaultValue="map" className="w-full">
            <div className="flex justify-center mb-8">
              <TabsList className="grid w-full max-w-[400px] grid-cols-2">
                <TabsTrigger value="map" className="flex items-center gap-2">
                  <MapIcon className="w-4 h-4" /> Mapa Interactivo
                </TabsTrigger>
                <TabsTrigger value="stats" className="flex items-center gap-2">
                  <BarChart3 className="w-4 h-4" /> Análisis Detallado
                </TabsTrigger>
              </TabsList>
            </div>

            <TabsContent value="map" className="mt-0">
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5 }}
              >
                <Map />
              </motion.div>
            </TabsContent>

            <TabsContent value="stats" className="mt-0">
              <Statistics />
            </TabsContent>
          </Tabs>
        </div>
      </section>

      <footer className="py-12 bg-secondary text-white">
        <div className="container mx-auto px-6 text-center">
          <p className="text-lg mb-2">
            EkoIA - Análisis de Balance de Carbono en Colombia
          </p>
          <p className="text-white/70">
            Desarrollado por EMKUBAR para EcoBalance360
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Index;