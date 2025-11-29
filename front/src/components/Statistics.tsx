import { useQuery } from '@tanstack/react-query';
import { fetchGeneralStats, fetchTimeSeries, fetchTopEmitters } from '@/services/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { Loader2, TrendingUp, Activity, AlertCircle } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

const Statistics = () => {
  // Queries para obtener datos
  const generalQuery = useQuery({ queryKey: ['generalStats'], queryFn: fetchGeneralStats });
  const timeSeriesQuery = useQuery({ queryKey: ['timeSeries'], queryFn: fetchTimeSeries });
  const topEmittersQuery = useQuery({ queryKey: ['topEmitters'], queryFn: () => fetchTopEmitters(10) });

  if (generalQuery.isLoading || timeSeriesQuery.isLoading || topEmittersQuery.isLoading) {
    return <div className="flex justify-center p-12"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>;
  }

  if (generalQuery.isError) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error de Conexión</AlertTitle>
        <AlertDescription>
          No se pudo conectar con el microservicio en http://localhost:8000. Asegúrate de que esté corriendo.
        </AlertDescription>
      </Alert>
    );
  }

  const general = generalQuery.data;
  const timeSeries = timeSeriesQuery.data;
  const topEmitters = topEmittersQuery.data;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Tarjetas de Resumen General */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Emisiones Totales</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{general?.total_emissions?.toExponential(2)}</div>
            <p className="text-xs text-muted-foreground">Toneladas de CO2eq</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Promedio por Registro</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{general?.avg_emissions?.toExponential(2)}</div>
            <p className="text-xs text-muted-foreground">Promedio global</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Registros</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{general?.count?.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">Puntos de datos analizados</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {/* Gráfico de Serie Temporal */}
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle>Evolución Temporal</CardTitle>
          </CardHeader>
          <CardContent className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={timeSeries}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="year" fontSize={12} />
                <YAxis fontSize={12} tickFormatter={(val) => val.toExponential(0)} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))' }}
                  itemStyle={{ color: 'hsl(var(--foreground))' }}
                />
                <Line type="monotone" dataKey="value" stroke="hsl(var(--primary))" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Gráfico de Top Emisores */}
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle>Top 10 Regiones Emisoras</CardTitle>
          </CardHeader>
          <CardContent className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topEmitters} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" horizontal={false} />
                <XAxis type="number" fontSize={12} tickFormatter={(val) => val.toExponential(0)} />
                <YAxis dataKey="name" type="category" width={100} fontSize={11} />
                <Tooltip 
                  cursor={{fill: 'transparent'}}
                  contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))' }}
                />
                <Bar dataKey="value" fill="hsl(var(--secondary))" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Statistics;