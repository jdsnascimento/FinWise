export default function Card({
    children,
    title,
    subtitle,
    icon: Icon,
    action,
    className = '',
    padding = true
}) {
    return (
        <div className={`bg-gray-800 rounded-xl border border-gray-700/50 ${className}`}>
            {(title || action) && (
                <div className="flex items-center justify-between px-6 py-4 border-b border-gray-700/50">
                    <div className="flex items-center gap-3">
                        {Icon && <Icon size={20} className="text-emerald-500" />}
                        <div>
                            <h3 className="font-semibold text-white">{title}</h3>
                            {subtitle && <p className="text-sm text-gray-400">{subtitle}</p>}
                        </div>
                    </div>
                    {action && <div>{action}</div>}
                </div>
            )}
            <div className={padding ? 'p-6' : ''}>
                {children}
            </div>
        </div>
    );
}