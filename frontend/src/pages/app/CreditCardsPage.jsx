import { useState, useEffect } from 'react';
import { Plus, CreditCard, Pencil, Trash, X } from '@phosphor-icons/react';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';
import Modal from '../../components/ui/Modal';
import { creditCardService } from '../../services/credit-card.service';

const FLAGS = ['Visa', 'Mastercard', 'American Express', 'Elo', 'Hipercard', 'Outros'];
const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#ef4444', '#f97316', '#eab308', '#10b981', '#06b6d4'];

export default function CreditCardsPage() {
    const [cards, setCards] = useState([]);
    const [loading, setLoading] = useState(true);
    const [modalOpen, setModalOpen] = useState(false);
    const [editingCard, setEditingCard] = useState(null);
    const [formData, setFormData] = useState({
        name: '',
        bank: '',
        flag: 'Visa',
        limit_amount: '',
        closing_day: 10,
        due_day: 15,
        color: '#6366f1'
    });
    const [error, setError] = useState('');

    useEffect(() => {
        loadCards();
    }, []);

    const loadCards = async () => {
        try {
            const data = await creditCardService.getSummary();
            setCards(data);
        } catch (err) {
            console.error('Erro ao carregar cartões:', err);
        } finally {
            setLoading(false);
        }
    };

    const openCreateModal = () => {
        setEditingCard(null);
        setFormData({
            name: '',
            bank: '',
            flag: 'Visa',
            limit_amount: '',
            closing_day: 10,
            due_day: 15,
            color: '#6366f1'
        });
        setError('');
        setModalOpen(true);
    };

    const openEditModal = (card) => {
        setEditingCard(card);
        setFormData({
            name: card.name,
            bank: card.bank,
            flag: card.flag,
            limit_amount: card.limit_amount,
            closing_day: card.closing_day,
            due_day: card.due_day,
            color: card.color
        });
        setError('');
        setModalOpen(true);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        try {
            const data = {
                ...formData,
                limit_amount: parseFloat(formData.limit_amount),
                closing_day: parseInt(formData.closing_day),
                due_day: parseInt(formData.due_day)
            };

            if (editingCard) {
                await creditCardService.update(editingCard.id, data);
            } else {
                await creditCardService.create(data);
            }

            setModalOpen(false);
            loadCards();
        } catch (err) {
            setError(err.response?.data?.detail || 'Erro ao salvar cartão');
        }
    };

    const handleDelete = async (cardId) => {
        if (!confirm('Tem certeza que deseja desativar este cartão?')) return;

        try {
            await creditCardService.delete(cardId);
            loadCards();
        } catch (err) {
            alert(err.response?.data?.detail || 'Erro ao desativar cartão');
        }
    };

    const getFlagColor = (flag) => {
        const colors = {
            'Visa': 'from-blue-600 to-blue-800',
            'Mastercard': 'from-orange-600 to-red-600',
            'American Express': 'from-blue-400 to-blue-600',
            'Elo': 'from-gray-600 to-gray-800',
            'Hipercard': 'from-red-500 to-red-700',
        };
        return colors[flag] || 'from-gray-600 to-gray-800';
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white">Cartões de Crédito</h1>
                    <p className="text-gray-400 mt-1">Gerencie seus cartões e limites</p>
                </div>
                <Button icon={Plus} onClick={openCreateModal}>
                    Novo Cartão
                </Button>
            </div>

            {/* Lista de Cartões */}
            {loading ? (
                <div className="text-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500 mx-auto"></div>
                    <p className="text-gray-400 mt-4">Carregando cartões...</p>
                </div>
            ) : cards.length === 0 ? (
                <Card>
                    <div className="text-center py-12">
                        <CreditCard size={48} className="mx-auto mb-4 text-gray-600" />
                        <h3 className="text-lg font-semibold text-white mb-2">Nenhum cartão cadastrado</h3>
                        <p className="text-gray-400 mb-4">Cadastre seu primeiro cartão de crédito</p>
                        <Button icon={Plus} onClick={openCreateModal}>
                            Novo Cartão
                        </Button>
                    </div>
                </Card>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {cards.map((card) => (
                        <div
                            key={card.id}
                            className={`bg-gradient-to-br ${getFlagColor(card.flag)} rounded-xl p-6 text-white relative group`}
                            style={{ backgroundColor: card.color, backgroundImage: 'none' }}
                        >
                            {/* Card Header */}
                            <div className="flex justify-between items-start mb-8">
                                <div>
                                    <p className="text-sm opacity-80">{card.bank}</p>
                                    <p className="text-lg font-bold">{card.name}</p>
                                    <p className="text-xs opacity-60">{card.flag}</p>
                                </div>
                                <CreditCard size={28} />
                            </div>

                            {/* Card Info */}
                            <div className="space-y-4">
                                <div>
                                    <p className="text-sm opacity-80">Limite disponível</p>
                                    <p className="text-2xl font-bold">
                                        {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(card.available_limit)}
                                    </p>
                                </div>

                                {/* Progress Bar */}
                                <div>
                                    <div className="flex justify-between text-xs mb-1">
                                        <span className="opacity-80">Utilizado</span>
                                        <span>{card.usage_percentage}%</span>
                                    </div>
                                    <div className="bg-white/20 rounded-full h-2">
                                        <div
                                            className={`bg-white rounded-full h-2 transition-all ${card.usage_percentage > 80 ? 'bg-red-300' : 'bg-white'
                                                }`}
                                            style={{ width: `${Math.min(card.usage_percentage, 100)}%` }}
                                        />
                                    </div>
                                </div>

                                {/* Fatura Atual */}
                                <div className="bg-white/10 rounded-lg p-3">
                                    <p className="text-xs opacity-80">Fatura Atual</p>
                                    <p className="text-lg font-bold">
                                        {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(card.current_bill_total)}
                                    </p>
                                </div>
                            </div>

                            {/* Actions */}
                            <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                                <button
                                    onClick={() => openEditModal(card)}
                                    className="p-1.5 bg-white/20 rounded-lg hover:bg-white/30 transition-colors"
                                >
                                    <Pencil size={14} />
                                </button>
                                <button
                                    onClick={() => handleDelete(card.id)}
                                    className="p-1.5 bg-white/20 rounded-lg hover:bg-red-500/50 transition-colors"
                                >
                                    <Trash size={14} />
                                </button>
                            </div>
                        </div>
                    ))}

                    {/* Add Card Button */}
                    <button
                        onClick={openCreateModal}
                        className="border-2 border-dashed border-gray-700 rounded-xl p-6 flex flex-col items-center justify-center text-gray-500 hover:border-emerald-500 hover:text-emerald-500 transition-colors min-h-[250px]"
                    >
                        <Plus size={32} />
                        <span className="mt-2 font-medium">Novo Cartão</span>
                    </button>
                </div>
            )}

            {/* Modal de Cadastro/Edição */}
            <Modal
                isOpen={modalOpen}
                onClose={() => setModalOpen(false)}
                title={editingCard ? 'Editar Cartão' : 'Novo Cartão'}
            >
                <form onSubmit={handleSubmit} className="space-y-4">
                    {error && (
                        <div className="bg-red-500/10 border border-red-500 text-red-500 rounded-lg p-3 text-sm">
                            {error}
                        </div>
                    )}

                    <Input
                        label="Nome do Cartão"
                        placeholder="Ex: Nubank, Inter..."
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        required
                    />

                    <Input
                        label="Banco"
                        placeholder="Ex: Nubank, Banco Inter..."
                        value={formData.bank}
                        onChange={(e) => setFormData({ ...formData, bank: e.target.value })}
                        required
                    />

                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-1">Bandeira</label>
                        <select
                            value={formData.flag}
                            onChange={(e) => setFormData({ ...formData, flag: e.target.value })}
                            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                        >
                            {FLAGS.map(flag => (
                                <option key={flag} value={flag}>{flag}</option>
                            ))}
                        </select>
                    </div>

                    <Input
                        label="Limite Total"
                        type="number"
                        step="0.01"
                        placeholder="5000.00"
                        value={formData.limit_amount}
                        onChange={(e) => setFormData({ ...formData, limit_amount: e.target.value })}
                        required
                    />

                    <div className="grid grid-cols-2 gap-4">
                        <Input
                            label="Dia Fechamento"
                            type="number"
                            min="1"
                            max="31"
                            value={formData.closing_day}
                            onChange={(e) => setFormData({ ...formData, closing_day: e.target.value })}
                            required
                        />
                        <Input
                            label="Dia Vencimento"
                            type="number"
                            min="1"
                            max="31"
                            value={formData.due_day}
                            onChange={(e) => setFormData({ ...formData, due_day: e.target.value })}
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Cor</label>
                        <div className="flex gap-2">
                            {COLORS.map(color => (
                                <button
                                    key={color}
                                    type="button"
                                    onClick={() => setFormData({ ...formData, color })}
                                    className={`w-8 h-8 rounded-full transition-transform ${formData.color === color ? 'scale-125 ring-2 ring-white' : ''
                                        }`}
                                    style={{ backgroundColor: color }}
                                />
                            ))}
                        </div>
                    </div>

                    <div className="flex gap-3 pt-4">
                        <Button type="submit" className="flex-1">
                            {editingCard ? 'Salvar' : 'Criar Cartão'}
                        </Button>
                        <Button
                            type="button"
                            variant="secondary"
                            onClick={() => setModalOpen(false)}
                        >
                            Cancelar
                        </Button>
                    </div>
                </form>
            </Modal>
        </div>
    );
}