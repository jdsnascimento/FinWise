/** Formata valor monetário com segurança (evita crash com null/undefined). */
export function formatCurrency(value) {
    const num = Number(value);
    if (!Number.isFinite(num)) {
        return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(0);
    }
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(num);
}

/** Extrai mensagem legível de erros da API (FastAPI). */
export function formatApiError(err, fallback = 'Erro inesperado') {
    const detail = err?.response?.data?.detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
        return detail.map((item) => item.msg || item.message || JSON.stringify(item)).join('. ');
    }
    if (detail && typeof detail === 'object') {
        return detail.msg || detail.message || fallback;
    }
    return err?.message || fallback;
}

/** Formata data ISO com segurança. */
export function formatDate(dateStr) {
    if (!dateStr) return '—';
    const d = new Date(dateStr.includes('T') ? dateStr : `${dateStr}T12:00:00`);
    if (Number.isNaN(d.getTime())) return '—';
    return d.toLocaleDateString('pt-BR');
}
