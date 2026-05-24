/* eslint-disable react-hooks/exhaustive-deps, react-hooks/set-state-in-effect */
import { useState, useEffect } from 'react';
import {
    Plus,
    MagnifyingGlass,
    CheckCircle,
    XCircle,
    Trash,
    CreditCard,
    Money,
    Calendar
} from '@phosphor-icons/react';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';
import Badge from '../../components/ui/Badge';
import Modal from '../../components/ui/Modal';
import { billService } from '../../services/bill.service';
import { creditCardService } from '../../services/credit-card.service';
import { categoryService } from '../../services/category.service';
import { formatCurrency, formatDate, formatApiError } from '../../utils/format';

const PAYMENT_ICONS = {
    credit_card: CreditCard,
    cash: Money,
    debit_card: CreditCard,
    pix: Money,
    boleto: Money,
    transfer: Money
};

export default function BillsPage() {
    const [bills, setBills] = useState([]);
    const [loading, setLoading] = useState(true);
    const [modalOpen, setModalOpen] = useState(false);
    const [editingBill, setEditingBill] = useState(null);
    const [filters, setFilters] = useState({
        status: '',
        search: '',
        billing_month: new Date().toISOString().slice(0, 7) + '-01'
    });

    // Dados para formulário
    const [categories, setCategories] = useState([]);
    const [cards, setCards] = useState([]);
    const [formData, setFormData] = useState({
        description: '',
        amount: '',
        installments: 1,
        purchase_date: new Date().toISOString().split('T')[0],
        category_id: '',
        card_id: '',
        payment_type: 'credit_card',
        notes: ''
    });
    const [error, setError] = useState('');

    const loadBills = async () => {
        try {
            setLoading(true);
            const params = {};
            if (filters.status) params.status = filters.status;
            if (filters.search) params.search = filters.search;
            if (filters.billing_month) params.billing_month = filters.billing_month;

            const data = await billService.listAll(params);
            setBills(Array.isArray(data) ? data : []);
        } catch (err) {
            console.error('Erro ao carregar contas:', err);
            setBills([]);
        } finally {
            setLoading(false);
        }
    };

    const loadCategories = async () => {
        try {
            const data = await categoryService.listAll('expense');
            setCategories(data);
        } catch (err) {
            console.error('Erro ao carregar categorias:', err);
        }
    };

    const loadCards = async () => {
        try {
            const data = await creditCardService.listAll(true);
            setCards(data);
        } catch (err) {
            console.error('Erro ao carregar cartões:', err);
        }
    };

    useEffect(() => {
        loadBills();
        loadCategories();
        loadCards();
    }, [filters]);

    const openCreateModal = () => {
        setEditingBill(null);
        setFormData({
            description: '',
            amount: '',
            installments: 1,
            purchase_date: new Date().toISOString().split('T')[0],
            category_id: categories[0]?.id || '',
            card_id: '',
            payment_type: 'credit_card',
            notes: ''
        });
        setError('');
        setModalOpen(true);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        try {
            const installments = formData.payment_type === 'credit_card'
                ? Math.max(1, Math.min(48, parseInt(formData.installments) || 1))
                : 1;
            const card_id = formData.payment_type === 'credit_card'
                ? (parseInt(formData.card_id) || null)
                : null;

            const amount = parseFloat(formData.amount);
            if (!Number.isFinite(amount) || amount <= 0) {
                setError('Informe um valor válido maior que zero.');
                return;
            }

            const payload = {
                description: formData.description,
                amount,
                installments,
                purchase_date: formData.purchase_date,
                category_id: parseInt(formData.category_id, 10),
                card_id,
                payment_type: formData.payment_type,
                notes: formData.notes || undefined
            };

            if (editingBill) {
                await billService.update(editingBill.id, payload);
                setModalOpen(false);
                await loadBills();
            } else {
                await billService.create(payload);
                setModalOpen(false);
                // Limpa filtro de mês para exibir parcelas em meses futuros
                setFilters((prev) => ({ ...prev, billing_month: '' }));
            }
        } catch (err) {
            setError(formatApiError(err, 'Erro ao salvar conta'));
        }
    };

    const handlePay = async (id) => {
        try {
            await billService.pay(id);
            loadBills();
        } catch {
            alert('Erro ao pagar conta');
        }
    };

    const handleCancel = async (id) => {
        try {
            await billService.cancel(id);
            loadBills();
        } catch {
            alert('Erro ao cancelar conta');
        }
    };

    const handleDelete = async (id) => {
        if (!confirm('Tem certeza que deseja excluir esta conta?')) return;
        try {
            await billService.delete(id);
            loadBills();
        } catch (err) {
            alert(err.response?.data?.detail || 'Erro ao excluir');
        }
    };

    const getStatusBadge = (status) => {
        const statusMap = {
            pending: { variant: 'warning', label: 'Pendente' },
            paid: { variant: 'success', label: 'Pago' },
            overdue: { variant: 'danger', label: 'Vencido' },
            cancelled: { variant: 'default', label: 'Cancelado' }
        };
        const s = statusMap[status] || statusMap.pending;
        return <Badge variant={s.variant}>{s.label}</Badge>;
    };

    const isOverdue = (bill) => {
        if (bill.status === 'overdue') return true;
        if (bill.status !== 'pending' || !bill.due_date) return false;
        const due = new Date(bill.due_date.includes('T') ? bill.due_date : `${bill.due_date}T12:00:00`);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        return due < today;
    };

    const selectedCard = formData.card_id ? cards.find(c => c.id === parseInt(formData.card_id)) : null;
    const parsedAmount = parseFloat(formData.amount);
    const exceedsLimit = formData.payment_type === 'credit_card' && 
        selectedCard && 
        !isNaN(parsedAmount) && 
        parsedAmount > selectedCard.available_limit;

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white">Contas a Pagar</h1>
                    <p className="text-gray-400 mt-1">Gerencie suas despesas e pagamentos</p>
                </div>
                <Button icon={Plus} onClick={openCreateModal}>
                    Nova Conta
                </Button>
            </div>

            {/* Filtros */}
            <Card padding={true}>
                <div className="flex flex-wrap gap-3">
                    <div className="flex-1 min-w-[200px]">
                        <Input
                            placeholder="Buscar descrição..."
                            value={filters.search}
                            onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                            icon={MagnifyingGlass}
                        />
                    </div>
                    <select
                        value={filters.status}
                        onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                        className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                    >
                        <option value="">Todos os status</option>
                        <option value="pending">Pendentes</option>
                        <option value="paid">Pagos</option>
                        <option value="overdue">Vencidos</option>
                    </select>
                    <Input
                        type="month"
                        value={filters.billing_month ? filters.billing_month.slice(0, 7) : ''}
                        onChange={(e) => setFilters({
                            ...filters,
                            billing_month: e.target.value ? `${e.target.value}-01` : ''
                        })}
                    />
                </div>
            </Card>

            {/* Lista de Contas */}
            <Card padding={false}>
                {loading ? (
                    <div className="text-center py-12">
                        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500 mx-auto"></div>
                    </div>
                ) : bills.length === 0 ? (
                    <div className="text-center py-12 px-6">
                        <Money size={48} className="mx-auto mb-4 text-gray-600" />
                        <h3 className="text-lg font-semibold text-white mb-2">Nenhuma conta encontrada</h3>
                        <p className="text-gray-400 mb-4">Registre sua primeira conta a pagar</p>
                        <Button icon={Plus} onClick={openCreateModal}>
                            Nova Conta
                        </Button>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-gray-700">
                                    <th className="text-left p-4 text-sm font-medium text-gray-400">Descrição</th>
                                    <th className="text-left p-4 text-sm font-medium text-gray-400">Valor</th>
                                    <th className="text-left p-4 text-sm font-medium text-gray-400">Categoria</th>
                                    <th className="text-left p-4 text-sm font-medium text-gray-400">Pagamento</th>
                                    <th className="text-left p-4 text-sm font-medium text-gray-400">Vencimento</th>
                                    <th className="text-left p-4 text-sm font-medium text-gray-400">Status</th>
                                    <th className="text-right p-4 text-sm font-medium text-gray-400">Ações</th>
                                </tr>
                            </thead>
                            <tbody>
                                {bills.map((bill) => {
                                    const PaymentIcon = PAYMENT_ICONS[bill.payment_type] || Money;
                                    const overdue = isOverdue(bill);

                                    return (
                                        <tr
                                            key={bill.id}
                                            className={`border-b border-gray-700/50 hover:bg-gray-700/30 transition-colors ${overdue ? 'bg-red-500/5' : ''
                                                }`}
                                        >
                                            <td className="p-4">
                                                <div>
                                                    <p className="text-white font-medium">{bill.description}</p>
                                                    {bill.installments > 1 && (
                                                        <p className="text-xs text-gray-400 mt-0.5">
                                                            Parcela {bill.current_installment}/{bill.installments}
                                                            {bill.card_name && ` • ${bill.card_name}`}
                                                        </p>
                                                    )}
                                                    {bill.card_name && bill.installments === 1 && (
                                                        <p className="text-xs text-gray-400 mt-0.5">{bill.card_name}</p>
                                                    )}
                                                </div>
                                            </td>
                                            <td className="p-4">
                                                <span className="text-white font-medium">
                                                    {formatCurrency(bill.total_amount)}
                                                </span>
                                                {bill.installments > 1 && (
                                                    <p className="text-xs text-gray-400">
                                                        {bill.installments}x {formatCurrency(bill.amount)}
                                                    </p>
                                                )}
                                            </td>
                                            <td className="p-4">
                                                <div className="flex items-center gap-2">
                                                    <div
                                                        className="w-3 h-3 rounded-full"
                                                        style={{ backgroundColor: bill.category_color }}
                                                    />
                                                    <span className="text-gray-300 text-sm">{bill.category_name}</span>
                                                </div>
                                            </td>
                                            <td className="p-4">
                                                <div className="flex items-center gap-2">
                                                    <PaymentIcon size={16} className="text-gray-400" />
                                                    <span className="text-gray-300 text-sm capitalize">
                                                        {bill.payment_type === 'credit_card' ? 'Crédito' :
                                                            bill.payment_type === 'debit_card' ? 'Débito' :
                                                                bill.payment_type === 'pix' ? 'PIX' :
                                                                    bill.payment_type === 'cash' ? 'Dinheiro' :
                                                                        bill.payment_type}
                                                    </span>
                                                </div>
                                            </td>
                                            <td className="p-4">
                                                <div className="flex items-center gap-2">
                                                    <Calendar size={16} className={overdue ? 'text-red-500' : 'text-gray-400'} />
                                                    <span className={`text-sm ${overdue ? 'text-red-500 font-medium' : 'text-gray-300'}`}>
                                                        {formatDate(bill.due_date)}
                                                    </span>
                                                </div>
                                            </td>
                                            <td className="p-4">
                                                {getStatusBadge(overdue ? 'overdue' : bill.status)}
                                            </td>
                                            <td className="p-4">
                                                <div className="flex items-center justify-end gap-1">
                                                    {bill.status === 'pending' && (
                                                        <>
                                                            <button
                                                                onClick={() => handlePay(bill.id)}
                                                                className="p-2 hover:bg-emerald-500/20 rounded-lg transition-colors text-gray-400 hover:text-emerald-500"
                                                                title="Pagar"
                                                            >
                                                                <CheckCircle size={18} />
                                                            </button>
                                                            <button
                                                                onClick={() => handleCancel(bill.id)}
                                                                className="p-2 hover:bg-red-500/20 rounded-lg transition-colors text-gray-400 hover:text-red-500"
                                                                title="Cancelar"
                                                            >
                                                                <XCircle size={18} />
                                                            </button>
                                                        </>
                                                    )}
                                                    <button
                                                        onClick={() => handleDelete(bill.id)}
                                                        className="p-2 hover:bg-red-500/20 rounded-lg transition-colors text-gray-400 hover:text-red-500"
                                                        title="Excluir"
                                                    >
                                                        <Trash size={18} />
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                )}
            </Card>

            {/* Modal Nova/Editar Conta */}
            <Modal
                isOpen={modalOpen}
                onClose={() => setModalOpen(false)}
                title={editingBill ? 'Editar Conta' : 'Nova Conta a Pagar'}
                size="lg"
            >
                <form onSubmit={handleSubmit} className="space-y-4">
                    {error && (
                        <div className="bg-red-500/10 border border-red-500 text-red-500 rounded-lg p-3 text-sm">
                            {error}
                        </div>
                    )}

                    <Input
                        label="Descrição"
                        placeholder="Ex: Compra supermercado"
                        value={formData.description}
                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                        required
                    />

                    <div className="grid grid-cols-2 gap-4">
                        <Input
                            label="Valor"
                            type="number"
                            step="0.01"
                            placeholder="150.00"
                            value={formData.amount}
                            onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                            required
                        />
                        <Input
                            label="Data da Compra"
                            type="date"
                            value={formData.purchase_date}
                            onChange={(e) => setFormData({ ...formData, purchase_date: e.target.value })}
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-1">
                            Forma de Pagamento
                        </label>
                        <div className="grid grid-cols-3 gap-2">
                            {[
                                { value: 'credit_card', label: 'Crédito' },
                                { value: 'debit_card', label: 'Débito' },
                                { value: 'pix', label: 'PIX' },
                                { value: 'cash', label: 'Dinheiro' },
                                { value: 'boleto', label: 'Boleto' },
                                { value: 'transfer', label: 'Transferência' }
                            ].map((type) => (
                                <button
                                    key={type.value}
                                    type="button"
                                    onClick={() => setFormData({ ...formData, payment_type: type.value })}
                                    className={`p-2 rounded-lg text-sm font-medium transition-colors ${formData.payment_type === type.value
                                            ? 'bg-emerald-500 text-white'
                                            : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                                        }`}
                                >
                                    {type.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    {formData.payment_type === 'credit_card' && (
                        <>
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-1">Cartão</label>
                                <select
                                    value={formData.card_id}
                                    onChange={(e) => setFormData({ ...formData, card_id: e.target.value })}
                                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                                    required
                                >
                                    <option value="">Selecione um cartão</option>
                                    {cards.map((card) => (
                                        <option key={card.id} value={card.id}>
                                            {card.name} ({card.bank}) - Disp: {formatCurrency(card.available_limit)}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            {exceedsLimit && (
                                <div className="bg-amber-500/10 border border-amber-500 text-amber-400 rounded-lg p-3 text-sm flex items-start gap-2">
                                    <span className="mt-0.5">⚠️</span>
                                    <div>
                                        <strong>Limite Excedido:</strong> Esta compra (<strong>{formatCurrency(parsedAmount)}</strong>) é maior que o limite disponível no cartão (<strong>{formatCurrency(selectedCard.available_limit)}</strong>).
                                    </div>
                                </div>
                            )}

                            <Input
                                label="Parcelas"
                                type="number"
                                min="1"
                                max="48"
                                value={formData.installments}
                                onChange={(e) => setFormData({ ...formData, installments: e.target.value })}
                                helper={formData.amount && parseInt(formData.installments) > 0 ?
                                    `${formData.installments}x de ${formatCurrency(formData.amount / parseInt(formData.installments))} = ${formatCurrency(parseFloat(formData.amount))}`
                                    : ''
                                }
                            />
                        </>
                    )}

                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-1">Categoria</label>
                        <select
                            value={formData.category_id}
                            onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
                            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                            required
                        >
                            <option value="">Selecione uma categoria</option>
                            {categories.map((cat) => (
                                <option key={cat.id} value={cat.id}>{cat.name}</option>
                            ))}
                        </select>
                    </div>

                    <Input
                        label="Observações"
                        placeholder="Notas adicionais..."
                        value={formData.notes}
                        onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                    />

                    <div className="flex gap-3 pt-4">
                        <Button type="submit" className="flex-1">
                            {editingBill ? 'Salvar' : 'Criar Conta'}
                        </Button>
                        <Button type="button" variant="secondary" onClick={() => setModalOpen(false)}>
                            Cancelar
                        </Button>
                    </div>
                </form>
            </Modal>
        </div>
    );
}