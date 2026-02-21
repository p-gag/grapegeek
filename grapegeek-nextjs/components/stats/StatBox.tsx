interface StatBoxProps {
  icon: React.ReactNode;
  value: number | string;
  label: string;
  subtext?: string;
  size?: 'default' | 'small';
}

export default function StatBox({ icon, value, label, subtext, size = 'default' }: StatBoxProps) {
  const isSmall = size === 'small';

  return (
    <div className="bg-white p-6 rounded-xl shadow-md border border-gray-100">
      <div className="flex flex-col items-center text-center">
        <div className={`text-purple-600 mb-3 ${isSmall ? '' : 'mb-4'}`}>
          {icon}
        </div>
        <p className={`font-bold text-gray-900 mb-2 ${isSmall ? 'text-3xl' : 'text-4xl'}`}>
          {typeof value === 'number' ? value.toLocaleString() : value}
        </p>
        <p className={`text-gray-600 font-medium ${isSmall ? 'text-base' : 'text-lg'}`}>
          {label}
        </p>
        {subtext && (
          <p className="text-gray-500 text-sm mt-2">{subtext}</p>
        )}
      </div>
    </div>
  );
}
