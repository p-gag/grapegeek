import Link from 'next/link';

interface StatCardProps {
  icon: React.ReactNode;
  value: number | string;
  label: string;
  href?: string;
}

export default function StatCard({ icon, value, label, href }: StatCardProps) {
  const inner = (
    <div className="bg-white p-8 rounded-xl shadow-brand transition-all duration-300 flex flex-col items-center text-center">
      <div className={`text-brand mb-4 transition-transform duration-300 ${href ? 'group-hover:scale-110' : ''}`}>
        {icon}
      </div>
      <p className="text-4xl font-bold text-gray-900 mb-2">
        {typeof value === 'number' ? value.toLocaleString() : value}
      </p>
      <p className="text-gray-600 text-lg">{label}</p>
    </div>
  );

  return href
    ? <Link href={href} className="block group hover:shadow-brand-hover rounded-xl transition-shadow duration-300">{inner}</Link>
    : <div>{inner}</div>;
}
