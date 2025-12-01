import { useQuery } from '@tanstack/react-query';
import { fetchGeneralStats, fetchTimeSeries, fetchTopEmitters, fetchCategoryStats, DashboardFilters } from '@/services/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell, Legend } from 'recharts';
import { Loader2, TrendingUp, Activity, AlertCircle, Leaf } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

interface StatisticsProps {
  filters: DashboardFilters;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d', '#ffc658', '#a4de6c', '#d0ed57'];

// Helper para extraer arreglos de cualquier estructura de respuesta
const getDataArray = (data: any) => {
  if (!data) return [];
  if (Array.isArray(data)) return data;
  
  // Posibles nombres de propiedades contenedoras
  if (data.time_series && Array.isArray(data.time_series)) return data.time_series;
  if (data.stats && Array.isArray(data.stats)) return data.stats;
  if (data.data && Array.isArray(data.data)) return data.data;
  if (data.categories && Array.isArray(data.categories)) return data.categories;
  if (data.top_emitters && Array.isArray(data.top_emitters)) return data.top_emitters;
  if (data.category_summary && Array.isArray(data.category_summary)) return data.category_summary;
  
  return [];
};

// Helper para detectar el valor numérico (total, mean, value, count)
const getValueKey = (data: any[]) => {
  if (!data || data.length === 0) return 'value';
  const first = data[0];
  // Orden de prioridad
  if ('total' in first) return 'total';
  if ('mean' in first) return 'mean';
  if ('value' in first) return 'value';
  if ('count' in first) return 'count'; 
  return 'value';
};

// Helper para detectar el nombre/etiqueta (Agregado CATEGORIA, DEPARTAMENTO, etc.)
const getNameKey = (data: any[], defaultKey: string) => {
  if (!data || data.length === 0) return defaultKey;
  const first = data[0];
  // Orden de prioridad de llaves probables
  if ('CATEGORIA' in first) return 'CATEGORIA'; 
  if ('categoria' in first) return 'categoria';
  if ('CATEGORY' in first) return 'CATEGORY';
  if ('REGION' in first) return 'REGION';
  if ('region' in first) return 'region';
  if ('DEPARTAMENTO' in first) return 'DEPARTAMENTO';
  if ('name' in first) return 'name';
  if ('ANO' in first) return 'ANO';
  if ('year' in first) return 'year';
  return defaultKey;
};

const Statistics = ({ filters }: StatisticsProps) => {
  const generalQuery = useQuery({ queryKey: ['generalStats', filters], queryFn: () => fetchGeneralStats(filters) });
  const timeSeriesQuery = useQuery({ queryKey: ['timeSeries', filters], queryFn: () => fetchTimeSeries(filters) });
  const topEmittersQuery = useQuery({ queryKey: ['topEmitters', filters], queryFn: () => fetchTopEmitters(10, filters) });
  const categoryQuery = useQuery({ queryKey: ['categoryStats', filters], queryFn: () => fetchCategoryStats(filters) });

  const isLoading = generalQuery.isLoading || timeSeriesQuery.isLoading || topEmittersQuery.isLoading || categoryQuery.isLoading;

  if (isLoading) {
    return <div className="flex justify-center p-12"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>;
  }

  if (generalQuery.isError) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error de Conexión</AlertTitle>
        <AlertDescription>No se pudieron obtener los datos. Revisa la consola o el backend.</AlertDescription>
      </Alert>
    );
  }

  const general = generalQuery.data || {};
  const timeSeries = getDataArray(timeSeriesQuery.data);
  const topEmitters = getDataArray(topEmittersQuery.data);
  const categories = getDataArray(categoryQuery.data);

  // --- Lógica de detección de llaves para gráficos ---
  const tsValKey = getValueKey(timeSeries);
  const tsNameKey = getNameKey(timeSeries, 'year');

  const topValKey = getValueKey(topEmitters);
  const topNameKey = getNameKey(topEmitters, 'name');

  const catValKey = getValueKey(categories);
  const catNameKey = getNameKey(categories, 'name'); 

  // --- CORRECCIÓN AQUÍ: Lectura de KPIs anidados ---
  // Ahora leemos dentro de 'co2_stats' si existe
  const stats = general.co2_stats || {};
  
  const totalEmissions = stats.total || general.total_emissions || 0;
  const avgEmissions = stats.mean || general.avg_emissions || 0;
  
  // 'total_records' está en la raíz, no en 'co2_stats'
  const countRecords = general.total_records || general.count || 0;

  return (
    <div className="space-y-6 animate-fade-in pb-10">
      {/* KPIs Generales */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Emisiones</CardTitle>
            <Leaf className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {totalEmissions.toExponential(2)}
            </div>
            <p className="text-xs text-muted-foreground pt-1">Toneladas CO₂eq</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Promedio</CardTitle>
            <TrendingUp className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {avgEmissions.toExponential(2)}
            </div>
            <p className="text-xs text-muted-foreground pt-1">Promedio por registro</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Registros</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{countRecords.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground pt-1">Datos analizados</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Filtro Actual</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold capitalize truncate">
              {filters.year !== 'all' ? filters.year : 'Histórico'}
            </div>
            <p className="text-xs text-muted-foreground truncate">
              {filters.region !== 'all' ? filters.region : 'Todas las regiones'}
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-1 lg:grid-cols-7">
        {/* Gráfico de Serie Temporal */}
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Evolución Temporal</CardTitle>
          </CardHeader>
          <CardContent className="h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={timeSeries} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted/30" />
                <XAxis dataKey={tsNameKey} fontSize={12} />
                <YAxis fontSize={12} tickFormatter={(val) => val.toExponential(0)} width={60} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'hsl(var(--card))', borderRadius: '8px', border: '1px solid hsl(var(--border))' }} 
                  itemStyle={{ color: 'hsl(var(--foreground))' }}
                  labelStyle={{ color: 'hsl(var(--foreground))' }}
                />
                <Line 
                  type="monotone" 
                  dataKey={tsValKey} 
                  stroke="hsl(var(--primary))" 
                  strokeWidth={3} 
                  dot={false} 
                  name="Emisiones"
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Gráfico de Categorías (Pie) */}
        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Por Categoría</CardTitle>
          </CardHeader>
          <CardContent className="h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              {categories.length > 0 ? (
                <PieChart>
                  <Pie
                    data={categories}
                    cx="50%"
                    cy="45%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={2}
                    dataKey={catValKey}
                    nameKey={catNameKey} 
                  >
                    {categories.map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'hsl(var(--card))', borderRadius: '8px', border: '1px solid hsl(var(--border))' }} 
                    itemStyle={{ color: 'hsl(var(--foreground))' }}
                  />
                  {/* Leyenda para ver nombres completos */}
                  <Legend 
                    layout="horizontal" 
                    verticalAlign="bottom" 
                    align="center"
                    wrapperStyle={{ fontSize: "11px", paddingTop: "10px" }}
                  />
                </PieChart>
              ) : (
                <div className="flex h-full items-center justify-center text-muted-foreground text-sm">
                  Sin datos de categorías.
                </div>
              )}
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Top Emisores */}
      <Card>
        <CardHeader>
          <CardTitle>Top Regiones Emisoras</CardTitle>
        </CardHeader>
        <CardContent className="h-[500px]">
          <ResponsiveContainer width="100%" height="100%">
            {topEmitters.length > 0 ? (
              <BarChart 
                data={topEmitters} 
                layout="vertical" 
                margin={{ left: 10, right: 30, top: 10, bottom: 10 }}
              >
                <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} className="stroke-muted/30" />
                <XAxis type="number" fontSize={12} tickFormatter={(val) => val.toExponential(0)} />
                <YAxis 
                  dataKey={topNameKey} 
                  type="category" 
                  width={140} 
                  fontSize={11} 
                  tick={{ fill: 'hsl(var(--foreground))' }}
                  interval={0}
                />
                <Tooltip 
                  cursor={{fill: 'transparent'}} 
                  contentStyle={{ backgroundColor: 'hsl(var(--card))', borderRadius: '8px', border: '1px solid hsl(var(--border))' }} 
                  itemStyle={{ color: 'hsl(var(--foreground))' }}
                />
                <Bar 
                  dataKey={topValKey} 
                  fill="hsl(var(--secondary))" 
                  radius={[0, 4, 4, 0]} 
                  barSize={24}
                  name="Emisiones"
                />
              </BarChart>
            ) : (
              <div className="flex h-full items-center justify-center text-muted-foreground text-sm">
                Sin datos de emisores.
              </div>
            )}
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
};

export default Statistics;