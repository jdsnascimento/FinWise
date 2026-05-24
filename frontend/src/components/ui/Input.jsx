import { forwardRef } from 'react';

const Input = forwardRef(({
    label,
    error,
    helper,
    icon: Icon,
    className = '',
    ...props
}, ref) => {
    return (
        <div className="space-y-1">
            {label && (
                <label className="block text-sm font-medium text-gray-300">
                    {label}
                </label>
            )}
            <div className="relative">
                {Icon && (
                    <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
                        <Icon size={18} />
                    </div>
                )}
                <input
                    ref={ref}
                    className={`
            w-full px-3 py-2 
            ${Icon ? 'pl-10' : ''}
            bg-gray-700 border rounded-lg 
            text-white placeholder-gray-400
            focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500
            transition-colors
            ${error ? 'border-red-500' : 'border-gray-600'}
            ${className}
          `}
                    {...props}
                />
            </div>
            {error && (
                <p className="text-sm text-red-500">{error}</p>
            )}
            {helper && !error && (
                <p className="text-sm text-gray-400">{helper}</p>
            )}
        </div>
    );
});

Input.displayName = 'Input';
export default Input;