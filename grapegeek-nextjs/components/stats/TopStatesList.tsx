import Link from 'next/link';

interface StateData {
  name: string;
  value: number;
}

interface TopStatesListProps {
  data: StateData[];
}

export default function TopStatesList({ data }: TopStatesListProps) {
  const maxValue = data[0]?.value || 1;

  return (
    <div className="space-y-3">
      {data.map((state, index) => {
        const percentage = (state.value / maxValue) * 100;

        return (
          <div key={state.name} className="flex items-center gap-3">
            <div className="flex-shrink-0 w-8 text-center">
              <span className="text-sm font-semibold text-gray-500">#{index + 1}</span>
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium text-gray-900">{state.name}</span>
                <span className="text-sm font-semibold text-brand">
                  {state.value.toLocaleString()}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-brand h-2 rounded-full transition-all duration-500"
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </div>
          </div>
        );
      })}
      {data.length === 0 && (
        <p className="text-gray-500 text-center py-8">No data available</p>
      )}
    </div>
  );
}
