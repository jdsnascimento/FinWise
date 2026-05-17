export default function Button({
    children,
    variant = 'primary',
    size = 'md',
    loading = false,
    icon: Icon,
    className = '',
    ...props
}) {
    const variants = {
        primary: 'bg-emerald-500 hover:bg-emerald-600 text-white',
        secondary: 'bg-gray-700 hover:bg-gray-600 text-white',
        danger: 'bg-red-500 hover:bg-red-600 text-white',
        ghost: 'bg-transparent hover:bg-gray-700 text-gray-300',
        outline: 'border border-emerald-500 text-emerald-500 hover:bg-emerald-500/10'
    };

    const sizes = {
        sm: 'px-3 py-1.5 text-sm',
        md: 'px-4 py-2 text-sm',
        lg: 'px-6 py-3 text-base'
    };

    return (
        <button
            className={`
        ${variants[variant]}
        ${sizes[size]}
        rounded-lg font-medium
        transition-all duration-200
        disabled:opacity-50 disabled:cursor-not-allowed
        inline-flex items-center gap-2
        ${className}
      `}
            disabled={loading}
            {...props}
        >
            {loading && (
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
            )}
            {Icon && !loading && <Icon size={18} />}
            {children}
        </button>
    );
}