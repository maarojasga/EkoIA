// src/pages/Dashboard.tsx
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchAvailableOptions, DashboardFilters } from '@/services/api';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from '@/components/ui/button';
import { Map as MapIcon, BarChart3, Filter, ArrowLeft, Sprout, Zap, BrainCircuit } from 'lucide-react'; // Importamos nuevos iconos
import Map from '@/components/Map';
import Statistics from '@/components/Statistics';
import CropsView from '@/components/CropsView'; // Nuevo
import EnergyView from '@/components/EnergyView'; // Nuevo
import PredictionView from '@/components/PredictionView'; // Nuevo
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
  const navigate = useNavigate();
  
  const [filters, setFilters] = useState<DashboardFilters>({
    year: 'all',
    region: 'all',
    category: 'all'
  });

  const { data: options } = useQuery({
    queryKey: ['dashboardOptions'],
    queryFn: fetchAvailableOptions
  });

  const handleFilterChange = (key: keyof DashboardFilters, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div className="min-h-screen bg-muted/10 flex flex-col">
      {/* Header */}
      <header className="bg-background border-b px-6 py-4 flex items-center justify-between sticky top-0 z-30">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-xl font-heading font-bold text-primary">EkoIA</h1>
            <p className="text-xs text-muted-foreground">Panel de Control Analítico</p>
          </div>
        </div>
      </header>

      <div className="flex-1 flex flex-col md:flex-row overflow-hidden">
        {/* Sidebar de Filtros */}
        <aside className="w-full md:w-64 bg-background border-r p-4 overflow-y-auto z-20 hidden md:block">
          <div className="flex items-center gap-2 mb-6 text-foreground font-semibold">
            <Filter className="h-4 w-4" /> Filtros Globales
          </div>
          
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-xs font-medium text-muted-foreground">Año</label>
              <Select value={filters.year} onValueChange={(v) => handleFilterChange('year', v)}>
                <SelectTrigger><SelectValue placeholder="Todos" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Histórico Completo</SelectItem>
                  {options?.years?.map(y => <SelectItem key={y} value={y.toString()}>{y}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-medium text-muted-foreground">Región</label>
              <Select value={filters.region} onValueChange={(v) => handleFilterChange('region', v)}>
                <SelectTrigger><SelectValue placeholder="Todas" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Nacional</SelectItem>
                  {options?.regions?.map(r => <SelectItem key={r} value={r}>{r}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-medium text-muted-foreground">Categoría</label>
              <Select value={filters.category} onValueChange={(v) => handleFilterChange('category', v)}>
                <SelectTrigger><SelectValue placeholder="Todas" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todas</SelectItem>
                  {options?.categories?.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            
            <div className="pt-4">
                <Button variant="outline" className="w-full text-xs" onClick={() => setFilters({ year: 'all', region: 'all', category: 'all' })}>
                    Limpiar Filtros
                </Button>
            </div>
          </div>
        </aside>

        {/* Área Principal con TABS expandidos */}
        <main className="flex-1 p-4 md:p-6 overflow-y-auto">
          <Tabs defaultValue="map" className="w-full h-full flex flex-col">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4 gap-4">
              <h2 className="text-2xl font-bold">Visualización de Datos</h2>
              
              <TabsList className="grid grid-cols-5 w-full sm:w-auto overflow-x-auto">
                <TabsTrigger value="map" className="gap-2"><MapIcon className="h-4 w-4 hidden sm:block"/> Mapa</TabsTrigger>
                <TabsTrigger value="stats" className="gap-2"><BarChart3 className="h-4 w-4 hidden sm:block"/> Estadísticas</TabsTrigger>
                <TabsTrigger value="crops" className="gap-2"><Sprout className="h-4 w-4 hidden sm:block"/> Cultivos</TabsTrigger>
                <TabsTrigger value="energy" className="gap-2"><Zap className="h-4 w-4 hidden sm:block"/> Energía</TabsTrigger>
                <TabsTrigger value="prediction" className="gap-2"><BrainCircuit className="h-4 w-4 hidden sm:block"/> Predicción</TabsTrigger>
              </TabsList>
            </div>

            <div className="flex-1">
                <TabsContent value="map" className="mt-0 h-full">
                    <Map filters={filters} />
                </TabsContent>

                <TabsContent value="stats" className="mt-0">
                    <Statistics filters={filters} />
                </TabsContent>

                {/* Nuevas Pestañas */}
                <TabsContent value="crops" className="mt-0">
                    <CropsView />
                </TabsContent>

                <TabsContent value="energy" className="mt-0">
                    <EnergyView />
                </TabsContent>

                <TabsContent value="prediction" className="mt-0">
                    <PredictionView />
                </TabsContent>
            </div>
          </Tabs>
        </main>
      </div>
    </div>
  );
};

export default Dashboard;