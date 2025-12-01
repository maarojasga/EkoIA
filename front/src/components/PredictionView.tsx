import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { BrainCircuit, TrendingDown } from 'lucide-react';

const data = [
  { year: '2020', actual: 4000, proyectado: 4000 },
  { year: '2021', actual: 4200, proyectado: 4100 },
  { year: '2022', actual: 4100, proyectado: 4250 },
  { year: '2023', actual: 4500, proyectado: 4400 },
  { year: '2024', actual: null, proyectado: 4600 },
  { year: '2025', actual: null, proyectado: 4800 },
  { year: '2026', actual: null, proyectado: 5100 },
  { year: '2030', actual: null, proyectado: 6000 },
];

const PredictionView = () => {
  return (
    <div className="space-y-6 animate-fade-in">
      <Card className="bg-primary/5 border-primary/20">
        <CardContent className="pt-6">
          <div className="flex items-start gap-4">
            <BrainCircuit className="h-8 w-8 text-primary mt-1" />
            <div>
              <h3 className="font-bold text-lg text-primary">Modelo Predictivo IA (Beta)</h3>
              <p className="text-sm text-muted-foreground">
                Basado en tendencias históricas, se proyecta un aumento del <strong>15%</strong> en emisiones para 2026 
                si no se aplican correctivos en el sector agrícola y transporte.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            Proyección de Emisiones <TrendingDown className="h-4 w-4 text-muted-foreground" />
          </CardTitle>
        </CardHeader>
        <CardContent className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="colorProy" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#8884d8" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorAct" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#82ca9d" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#82ca9d" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis dataKey="year" />
              <YAxis />
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted/30" />
              <Tooltip contentStyle={{ backgroundColor: 'hsl(var(--card))', borderRadius: '8px' }} />
              <Area type="monotone" dataKey="proyectado" stroke="#8884d8" fillOpacity={1} fill="url(#colorProy)" name="Proyección" />
              <Area type="monotone" dataKey="actual" stroke="#82ca9d" fillOpacity={1} fill="url(#colorAct)" name="Datos Reales" />
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
};

export default PredictionView;