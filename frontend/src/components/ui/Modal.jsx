import { useEffect } from 'react';
import { X } from '@phosphor-icons/react';

export default function Modal({
    isOpen,
    onClose,
    title,
    children,
    size = 'md'
}) {
    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = 'unset';
        }
        return () => {
            document.body.style.overflow = 'unset';
        };
    }, [isOpen]);

    if (!isOpen) return null;

    const sizes = {
        sm: 'max-w-md',
        md: 'max-w-lg',
        lg: 'max-w-2xl',
        xl: 'max-w-4xl'
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div
                className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                onClick={onClose}
            />
            <div className={`
        relative bg-gray-800 rounded-xl border border-gray-700 
        w-full ${sizes[size]} max-h-[90vh] overflow-auto
        animate-in slide-in-from-bottom-4 duration-300
      `}>
                <div className="flex items-center justify-between p-6 border-b border-gray-700">
                    <h2 className="text-lg font-semibold text-white">{title}</h2>
                    <button
                        onClick={onClose}
                        className="p-1 hover:bg-gray-700 rounded-lg transition-colors text-gray-400 hover:text-white"
                    >
                        <X size={20} />
                    </button>
                </div>
                <div className="p-6">
                    {children}
                </div>
            </div>
        </div>
    );
}