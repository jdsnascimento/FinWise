/* eslint-disable react-hooks/set-state-in-effect */
import { useState, useEffect } from 'react';
import { Plus, Pencil, Trash, Tag } from '@phosphor-icons/react';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';
import Modal from '../../components/ui/Modal';
import { categoryService } from '../../services/category.service';
import { formatApiError } from '../../utils/format';

const ICONS = ['receipt', 'restaurant', 'car', 'home', 'heart', 'book', 'gamepad', 'cart', 'credit-card', 'briefcase', 'laptop', 'trending-up', 'tag', 'gift', 'airplane', 'phone', 'camera', 'music'];
const COLORS = ['#ef4444', '#f97316', '#eab308', '#84cc16', '#10b981', '#06b6d4', '#3b82f6', '#6366f1', '#8b5cf6', '#a855f7', '#ec4899', '#f43f5e'];

const CategoryList = ({ categories, type, onEdit, onDelete, onCreate }) => (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {categories.map((cat) => (
            <div
                key={cat.id}
                className="bg-gray-700/50 rounded-lg p-4 flex items-center gap-3 group hover:bg-gray-700 transition-colors"
            >
                <div
                    className="w-8 h-8 rounded-lg flex items-center justify-center text-white"
                    style={{ backgroundColor: cat.color }}
                >
                    <Tag size={16} />
                </div>
                <span className="text-gray-300 text-sm flex-1">{cat.name}</span>
                <div className="opacity-0 group-hover:opacity-100 flex gap-1 transition-opacity">
                    <button
                        onClick={() => onEdit(cat)}
                        className="p-1 hover:bg-gray-600 rounded text-gray-400 hover:text-white"
                    >
                        <Pencil size={14} />
                    </button>
                    <button
                        onClick={() => onDelete(cat.id)}
                        className="p-1 hover:bg-red-500/20 rounded text-gray-400 hover:text-red-500"
                    >
                        <Trash size={14} />
                    </button>
                </div>
            </div>
        ))}
        <button
            onClick={() => onCreate(type)}
            className="border-2 border-dashed border-gray-600 rounded-lg p-4 flex flex-col items-center justify-center text-gray-500 hover:border-emerald-500 hover:text-emerald-500 transition-colors"
        >
            <Plus size={20} />
            <span className="text-xs mt-1">Nova</span>
        </button>
    </div>
);

export default function CategoriesPage() {
    const [expenseCategories, setExpenseCategories] = useState([]);
    const [incomeCategories, setIncomeCategories] = useState([]);
    const [modalOpen, setModalOpen] = useState(false);
    const [editingCategory, setEditingCategory] = useState(null);
    const [error, setError] = useState('');
    const [formData, setFormData] = useState({
        name: '',
        icon: 'receipt',
        color: '#10b981',
        type: 'expense'
    });

    const loadCategories = async () => {
        try {
            const expenses = await categoryService.listAll('expense');
            const incomes = await categoryService.listAll('income');
            setExpenseCategories(Array.isArray(expenses) ? expenses : []);
            setIncomeCategories(Array.isArray(incomes) ? incomes : []);
        } catch (err) {
            console.error('Erro ao carregar categorias:', err);
        }
    };

    useEffect(() => {
        loadCategories();
    }, []);

    const openCreateModal = (type) => {
        setEditingCategory(null);
        setFormData({
            name: '',
            icon: 'receipt',
            color: type === 'expense' ? '#ef4444' : '#10b981',
            type
        });
        setError('');
        setModalOpen(true);
    };

    const openEditModal = (category) => {
        setEditingCategory(category);
        setFormData({
            name: category.name,
            icon: category.icon,
            color: category.color,
            type: category.type
        });
        setError('');
        setModalOpen(true);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        const name = formData.name?.trim();
        if (!name || name.length < 2) {
            setError('O nome deve ter pelo menos 2 caracteres.');
            return;
        }

        const payload = {
            name,
            icon: formData.icon,
            color: formData.color,
            type: formData.type
        };

        try {
            if (editingCategory) {
                await categoryService.update(editingCategory.id, payload);
            } else {
                await categoryService.create(payload);
            }
            setModalOpen(false);
            loadCategories();
        } catch (err) {
            setError(formatApiError(err, 'Erro ao salvar categoria'));
        }
    };

    const handleDelete = async (id) => {
        if (!confirm('Desativar esta categoria?')) return;
        try {
            await categoryService.delete(id);
            loadCategories();
        } catch {
            alert('Erro ao desativar categoria');
        }
    };

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-white">Categorias</h1>
                <p className="text-gray-400 mt-1">Personalize suas categorias de gastos e receitas</p>
            </div>

            <Card title="Despesas" subtitle="Categorias para contas a pagar">
                <CategoryList categories={expenseCategories} type="expense" onEdit={openEditModal} onDelete={handleDelete} onCreate={openCreateModal} />
            </Card>

            <Card title="Receitas" subtitle="Categorias para contas a receber">
                <CategoryList categories={incomeCategories} type="income" onEdit={openEditModal} onDelete={handleDelete} onCreate={openCreateModal} />
            </Card>

            <Modal
                isOpen={modalOpen}
                onClose={() => setModalOpen(false)}
                title={editingCategory ? 'Editar Categoria' : 'Nova Categoria'}
            >
                <form onSubmit={handleSubmit} className="space-y-4">
                    {error && (
                        <div className="bg-red-500/10 border border-red-500 text-red-500 rounded-lg p-3 text-sm">
                            {error}
                        </div>
                    )}
                    <Input
                        label="Nome"
                        placeholder="Ex: Alimentação"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        required
                    />

                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Ícone</label>
                        <div className="grid grid-cols-6 gap-2">
                            {ICONS.map((icon) => (
                                <button
                                    key={icon}
                                    type="button"
                                    onClick={() => setFormData({ ...formData, icon })}
                                    className={`p-2 rounded-lg text-center transition-colors ${formData.icon === icon
                                            ? 'bg-emerald-500 text-white'
                                            : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                                        }`}
                                >
                                    <Tag size={18} className="mx-auto" />
                                </button>
                            ))}
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Cor</label>
                        <div className="flex gap-2 flex-wrap">
                            {COLORS.map((color) => (
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
                            {editingCategory ? 'Salvar' : 'Criar'}
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