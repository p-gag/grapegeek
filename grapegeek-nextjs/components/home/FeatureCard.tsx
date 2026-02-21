import Link from 'next/link';

interface FeatureCardProps {
  title: string;
  description: string;
  href: string;
  icon: React.ReactNode;
}

export default function FeatureCard({ title, description, href, icon }: FeatureCardProps) {
  return (
    <Link href={href} className="block group">
      <div className="bg-white p-8 rounded-xl shadow-md hover:shadow-xl transition-all duration-300 h-full">
        <div className="text-purple-600 mb-4 group-hover:scale-110 transition-transform duration-300">
          {icon}
        </div>
        <h3 className="text-2xl font-bold text-gray-900 mb-3 group-hover:text-purple-600 transition-colors">
          {title}
        </h3>
        <p className="text-gray-600 leading-relaxed">
          {description}
        </p>
        <div className="mt-4 text-purple-600 font-semibold group-hover:translate-x-2 transition-transform inline-block">
          Explore →
        </div>
      </div>
    </Link>
  );
}
