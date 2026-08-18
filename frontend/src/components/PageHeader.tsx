interface Props {
  kicker?: string;
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
}

export default function PageHeader({ kicker, title, subtitle, actions }: Props) {
  return (
    <div className="flex items-end justify-between gap-4 px-6 pt-6 pb-4">
      <div>
        {kicker && (
          <p className="text-[10px] uppercase tracking-[0.22em] text-ember-400 mb-1">{kicker}</p>
        )}
        <h2 className="font-display text-2xl font-semibold tracking-tight">{title}</h2>
        {subtitle && <p className="text-sm text-mist-400 mt-1 max-w-xl">{subtitle}</p>}
      </div>
      {actions}
    </div>
  );
}
