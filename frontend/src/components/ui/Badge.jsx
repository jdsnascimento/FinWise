export default function Badge({
    children,
    variant = 'default',
    className = ''
}) {
    const variants = {
        default: 'bg-gray-700 text-gray-300',
        success: 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20',
        warning: 'bg-yellow-500/10 text-yellow-500 border border-yellow-500/20',
        danger: 'bg-red-500/10 text-red-500 border border-red-500/20',
        info: 'bg-blue-500/10 text-blue-500 border border-blue-500/20',
    };

    return (
        <span className={`
      inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
      ${variants[variant]}
      ${className}
    `}>
            {children}
        </span>
    );
}