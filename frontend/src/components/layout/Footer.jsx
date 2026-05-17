export default function Footer() {
    return (
        <footer className="mt-auto py-6 px-4 lg:px-6 border-t border-gray-800 bg-gray-900 text-center">
            <p className="text-sm text-gray-500">
                &copy; {new Date().getFullYear()} FinWise. Todos os direitos reservados.
            </p>
        </footer>
    );
}
