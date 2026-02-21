import Link from 'next/link';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  icon: React.ReactNode;
  value: number | string;
  label: string;
  href: string;
}

export default function StatCard({ icon, value, label, href }: StatCardProps) {
  return (
    <Link href={href} className="block group">
      <div className="bg-white p-8 rounded-xl shadow-md hover:shadow-xl transition-shadow duration-300">
        <div className="flex flex-col items-center text-center">
          <div className="text-purple-600 mb-4 group-hover:scale-110 transition-transform duration-300">
            {icon}
          </div>
          <p className="text-4xl font-bold text-gray-900 mb-2">
            {typeof value === 'number' ? value.toLocaleString() : value}
          </p>
          <p className="text-gray-600 text-lg">{label}</p>
        </div>
      </div>
    </Link>
  );
}
